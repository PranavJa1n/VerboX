from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class ReviewerVerdict(str, Enum):
    AGREE = "agree"
    DISAGREE = "disagree"
    PARTIALLY_CORRECT = "partially_correct"

    @classmethod
    def parse(cls, val: str) -> "ReviewerVerdict":
        cleaned = str(val).strip().lower().replace(" ", "_").replace("-", "_")
        for member in cls:
            if member.value == cleaned:
                return member
        return cls.DISAGREE


class HumanLabel(BaseModel):
    label_id: str = Field(default_factory=lambda: f"hl_{uuid.uuid4().hex[:8]}")
    verdict_id: str
    reviewer: str
    reviewer_verdict: ReviewerVerdict
    correction_note: Optional[str] = ""
    reviewed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["reviewer_verdict"] = self.reviewer_verdict.value
        return data


class HumanFeedbackLoop:
    def __init__(self, mongo_client: Optional[Any] = None):
        self.mongo = mongo_client
        self._verdicts: Dict[str, Dict[str, Any]] = {}
        self._traces: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._labels: Dict[str, Dict[str, Any]] = {}

    def register_verdict(self, verdict: Dict[str, Any]) -> None:
        vid = verdict.get("verdict_id") or verdict.get("id")
        if vid:
            self._verdicts[vid] = verdict

    def register_span(self, span: Dict[str, Any]) -> None:
        tid = span.get("trace_id")
        if tid:
            self._traces[tid].append(span)

    async def submit_label(
        self,
        verdict_id: str,
        reviewer: str,
        reviewer_verdict: Union[str, ReviewerVerdict],
        correction_note: str = "",
        label_id: Optional[str] = None,
    ) -> HumanLabel:
        v_enum = reviewer_verdict if isinstance(reviewer_verdict, ReviewerVerdict) else ReviewerVerdict.parse(reviewer_verdict)
        label = HumanLabel(
            label_id=label_id or f"hl_{uuid.uuid4().hex[:8]}",
            verdict_id=verdict_id,
            reviewer=reviewer,
            reviewer_verdict=v_enum,
            correction_note=correction_note,
        )
        doc = label.to_dict()
        if self.mongo and hasattr(self.mongo, "db"):
            await self.mongo.db["human_labels"].insert_one(doc)
        else:
            self._labels[label.label_id] = doc
        return label

    async def get_labels_for_verdict(self, verdict_id: str) -> List[Dict[str, Any]]:
        if self.mongo and hasattr(self.mongo, "db"):
            cursor = self.mongo.db["human_labels"].find({"verdict_id": verdict_id})
            return await cursor.to_list(length=None)
        return [l for l in self._labels.values() if l.get("verdict_id") == verdict_id]

    async def get_all_labels(self) -> List[Dict[str, Any]]:
        if self.mongo and hasattr(self.mongo, "db"):
            cursor = self.mongo.db["human_labels"].find({})
            return await cursor.to_list(length=None)
        return list(self._labels.values())

    async def get_review_feed(
        self,
        flag_type: Optional[str] = None,
        agent_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        if self.mongo and hasattr(self.mongo, "verdicts"):
            query: Dict[str, Any] = {}
            if flag_type:
                query["flags.type"] = flag_type
            cursor = self.mongo.verdicts.find(query).limit(limit)
            items = await cursor.to_list(length=limit)
        else:
            items = list(self._verdicts.values())

        if flag_type:
            items = [v for v in items if any(f.get("type") == flag_type for f in v.get("flags", []))]
        return items[:limit]

    async def get_verdict_context(self, verdict_id: str) -> Dict[str, Any]:
        verdict = None
        if self.mongo and hasattr(self.mongo, "verdicts"):
            verdict = await self.mongo.verdicts.find_one({"verdict_id": verdict_id})
        verdict = verdict or self._verdicts.get(verdict_id)
        if not verdict:
            raise ValueError(f"Verdict '{verdict_id}' not found.")

        tid = verdict.get("trace_id")
        spans = []
        if self.mongo and hasattr(self.mongo, "get_spans_by_trace"):
            spans = await self.mongo.get_spans_by_trace(tid)
        elif self.mongo and hasattr(self.mongo, "traces"):
            spans = await self.mongo.traces.find({"trace_id": tid}).to_list(length=None)
        else:
            spans = self._traces.get(tid, [])

        target_span = next((s for s in spans if s.get("span_id") == verdict.get("span_id")), None)
        prior_steps = [s for s in spans if s.get("span_id") != verdict.get("span_id")]
        labels = await self.get_labels_for_verdict(verdict_id)

        return {
            "verdict": verdict,
            "target_span": target_span,
            "prior_steps": prior_steps,
            "human_labels": labels,
        }

    def cluster_disagreements(
        self,
        labels: List[Dict[str, Any]],
        verdicts_map: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        disagreements = [l for l in labels if l.get("reviewer_verdict") in ("disagree", "partially_correct")]
        buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for l in disagreements:
            v = verdicts_map.get(l.get("verdict_id"), {})
            note = (l.get("correction_note") or "").lower()

            if any(k in note for k in ["pre-approved", "approved", "exception", "ticket", "authorized"]):
                category = "pre_approved_exceptions"
            elif any(k in note for k in ["read-only", "read only", "get_", "query", "check_"]):
                category = "read_only_false_positives"
            elif any(k in note for k in ["duplicate", "dedup", "cache", "retry"]):
                category = "necessary_retries_or_polling"
            else:
                flags = v.get("flags", [])
                category = flags[0].get("type", "general") if flags else "general"

            buckets[category].append({"label": l, "verdict": v})

        clusters = []
        for cat, items in buckets.items():
            clusters.append({
                "cluster_id": cat,
                "count": len(items),
                "verdict_ids": [i["label"].get("verdict_id") for i in items],
                "sample_notes": [i["label"].get("correction_note") for i in items if i["label"].get("correction_note")][:3],
            })
        clusters.sort(key=lambda c: c["count"], reverse=True)
        return clusters

    def build_few_shot_examples(
        self,
        clusters: List[Dict[str, Any]],
        verdicts_map: Dict[str, Dict[str, Any]],
        spans_map: Optional[Dict[str, Dict[str, Any]]] = None,
        max_examples: int = 3,
    ) -> List[str]:
        spans_map = spans_map or {}
        examples = []
        for c in clusters:
            for vid in c.get("verdict_ids", []):
                if len(examples) >= max_examples:
                    break
                v = verdicts_map.get(vid, {})
                span = spans_map.get(v.get("span_id"), {})
                flags = v.get("flags", [])
                reason = flags[0].get("reason", "Flagged") if flags else "Clean"
                note = c.get("sample_notes", [""])[0] if c.get("sample_notes") else "Action allowed."
                examples.append(
                    f"Example [Tool: {span.get('tool_name', 'unknown')}]:\n"
                    f"  Args: {span.get('tool_arguments', {})}\n"
                    f"  Judge: {reason}\n"
                    f"  Human Correction: {note}\n"
                    f"  Correct Output: CLEAN"
                )
        return examples

    def calculate_agreement_metrics(
        self,
        labels: List[Dict[str, Any]],
        verdicts_map: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        total = len(labels)
        if total == 0:
            return {"total": 0, "agreement_rate": 0.0, "by_version": {}}

        agree = sum(1 for l in labels if l.get("reviewer_verdict") == "agree")
        disagree = sum(1 for l in labels if l.get("reviewer_verdict") == "disagree")
        partial = sum(1 for l in labels if l.get("reviewer_verdict") == "partially_correct")

        by_version: Dict[str, Dict[str, int]] = defaultdict(lambda: {"total": 0, "agree": 0})
        for l in labels:
            v = verdicts_map.get(l.get("verdict_id"), {})
            ver = v.get("prompt_version", "v1")
            by_version[ver]["total"] += 1
            if l.get("reviewer_verdict") == "agree":
                by_version[ver]["agree"] += 1

        trends = {}
        for ver, data in by_version.items():
            rate = round((data["agree"] / data["total"]) * 100, 2) if data["total"] else 0.0
            trends[ver] = {"total": data["total"], "agree": data["agree"], "rate_pct": rate}

        return {
            "total": total,
            "agree": agree,
            "disagree": disagree,
            "partially_correct": partial,
            "agreement_rate_pct": round((agree / total) * 100, 2),
            "by_version": trends,
        }

    def generate_refined_prompt(self, base_prompt: str, few_shots: List[str], version: str = "v2") -> str:
        prompt_lines = [base_prompt.strip(), f"\n# Few-Shot Refinements ({version}):"]
        for i, ex in enumerate(few_shots, 1):
            prompt_lines.append(f"\n--- Example {i} ---\n{ex}")
        return "\n".join(prompt_lines)
