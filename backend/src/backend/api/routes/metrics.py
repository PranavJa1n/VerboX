from fastapi import APIRouter, HTTPException
from backend.mongo_util.mongo_client import mongo_client
from backend.dedup.redis_client import RedisClient

router = APIRouter()
redis = RedisClient()

FLAG_TO_DECISION = {
    "policy_violation": "blocked",
    "risky": "blocked",
    "redundant": "cached",
    "inconsistent": "halted",
    "multi_agent_contradiction": "halted",
}


@router.get("/stats")
async def get_stats():
    try:
        all_verdicts = await mongo_client.verdicts.find({}).to_list(length=None)

        blocks = sum(1 for v in all_verdicts if v.get("flags"))
        total_flags = sum(len(v.get("flags", [])) for v in all_verdicts)

        labeled_ids = set()
        async for label in mongo_client.db["human_labels"].find({}, {"verdict_id": 1}):
            labeled_ids.add(label["verdict_id"])

        review = sum(
            1 for v in all_verdicts
            if v.get("flags") and v.get("verdict_id") not in labeled_ids
        )

        saved = int(redis.get("verbox:stats:duplicates_prevented") or 0)

        return {
            "blocks": blocks,
            "saved": saved,
            "flags": total_flags,
            "review": review,
            "pending": review,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/verdicts")
async def get_verdicts(limit: int = 50, severity_min: float = 0.0, flag_type: str = None):
    try:
        query = {"verdict_type": "step", "flags": {"$ne": []}}
        if flag_type:
            query["flags.type"] = flag_type

        # CHANGED: no .limit() here -- fetch every matching document first,
        # so severity filtering below doesn't operate on an already-truncated set.
        verdicts = await mongo_client.verdicts.find(query).sort("evaluated_at", -1).to_list(length=None)

        span_ids = [v["span_id"] for v in verdicts if v.get("span_id")]
        spans_cursor = mongo_client.traces.find({"span_id": {"$in": span_ids}})
        spans = await spans_cursor.to_list(length=None)
        span_map = {s["span_id"]: s for s in spans}

        rows = []
        for v in verdicts:
            flags = v.get("flags", [])
            if not flags:
                continue

            top_flag = max(flags, key=lambda f: f.get("severity", 0))
            if top_flag.get("severity", 0) < severity_min:
                continue

            span = span_map.get(v.get("span_id"), {})
            evaluated_at = v.get("evaluated_at")
            time_str = evaluated_at.strftime("%H:%M:%S UTC") if hasattr(evaluated_at, "strftime") else str(evaluated_at)[:19] + " UTC"

            rows.append({
                "id": v.get("verdict_id"),
                "time": time_str,
                "trace": v.get("trace_id", ""),
                "agent": span.get("agent_id", "unknown"),
                "tool": span.get("gen_ai.tool.name", span.get("tool_name", "unknown")),
                "rule": top_flag.get("type", "unknown"),
                "decision": FLAG_TO_DECISION.get(top_flag.get("type"), "blocked"),
                "severity": top_flag.get("severity", 0.0),
            })

            # CHANGED: stop collecting once we actually have `limit` real matches
            if len(rows) >= limit:
                break

        return {"count": len(rows), "items": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trust-scores")
async def get_trust_scores():
    try:
        step_verdicts = await mongo_client.verdicts.find({"verdict_type": "step"}).to_list(length=None)

        span_ids = [v["span_id"] for v in step_verdicts if v.get("span_id")]
        spans = await mongo_client.traces.find({"span_id": {"$in": span_ids}}).to_list(length=None)
        span_map = {s["span_id"]: s for s in spans}

        agent_stats: dict = {}
        for v in step_verdicts:
            span = span_map.get(v.get("span_id"), {})
            agent_id = span.get("agent_id", "unknown")
            is_flagged = bool(v.get("flags"))

            if agent_id not in agent_stats:
                agent_stats[agent_id] = {"clean": 0, "flagged": 0}

            if is_flagged:
                agent_stats[agent_id]["flagged"] += 1
            else:
                agent_stats[agent_id]["clean"] += 1

        rows = []
        for agent_id, counts in agent_stats.items():
            total = counts["clean"] + counts["flagged"]
            trust = round(counts["clean"] / total, 2) if total > 0 else 1.0
            rows.append({
                "agent": agent_id,
                "clean": counts["clean"],
                "flagged": counts["flagged"],
                "trust": str(trust),
            })

        rows.sort(key=lambda r: float(r["trust"]))
        return {"items": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contradictions")
async def get_contradictions(limit: int = 50):
    try:
        verdicts = await mongo_client.verdicts.find(
            {"verdict_type": "contradiction"}
        ).sort("evaluated_at", -1).limit(limit).to_list(length=limit)

        items = []
        for v in verdicts:
            flags = v.get("flags", [])
            if not flags:
                continue
            for v in verdicts:
                for flag in v.get("flags", []):
                    items.append({        
                        "id": v.get("verdict_id", ""),
                                "text": flag.get("reason", ""),
                        "sim": str(round(flag.get("severity", 0.0), 2)),
                    })

        return {"count": len(items), "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

