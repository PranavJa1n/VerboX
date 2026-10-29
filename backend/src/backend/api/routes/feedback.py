from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from backend.schemas.feedback import SubmitLabelRequest, SubmitLabelResponse, AgreementMetricsResponse
from backend.mongo_util.mongo_client import mongo_client
from backend.utility.human_feedback import HumanFeedbackLoop

router = APIRouter()

feedback_loop = HumanFeedbackLoop(mongo_client=mongo_client)


@router.post("/label", response_model=SubmitLabelResponse)
async def submit_label(request: SubmitLabelRequest):
    """
    A human reviewer records agree/disagree/partially_correct on a
    specific verdict, with an optional correction note.
    """
    try:
        label = await feedback_loop.submit_label(
            verdict_id=request.verdict_id,
            reviewer=request.reviewer,
            reviewer_verdict=request.reviewer_verdict,
            correction_note=request.correction_note or "",
        )
        return SubmitLabelResponse(**label.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit label: {str(e)}")


@router.get("/review")
async def get_review_feed(
    flag_type: Optional[str] = Query(default=None),
    agent_id: Optional[str] = Query(default=None),
    limit: int = Query(default=100, le=500),
):
    """
    Returns verdicts for a human reviewer to browse, optionally filtered
    by flag type. No prioritization/sampling -- full feed, reviewer picks.
    """
    try:
        items = await feedback_loop.get_review_feed(flag_type=flag_type, agent_id=agent_id, limit=limit)
        return {"count": len(items), "items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch review feed: {str(e)}")


@router.get("/verdict/{verdict_id}")
async def get_verdict_context(verdict_id: str):
    """
    Full context for one verdict: the verdict itself, the span it judged,
    other steps in the same trace, and any existing human labels on it.
    """
    try:
        return await feedback_loop.get_verdict_context(verdict_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch verdict context: {str(e)}")


@router.get("/metrics", response_model=AgreementMetricsResponse)
async def get_agreement_metrics():
    """
    Judge-vs-human agreement rate, broken down by prompt_version -- the
    trend line showing whether the judge is improving over iterations.
    """
    try:
        labels = await feedback_loop.get_all_labels()

        verdict_ids = list({l["verdict_id"] for l in labels})
        verdicts_map: Dict[str, Any] = {}
        if verdict_ids:
            cursor = mongo_client.verdicts.find({"verdict_id": {"$in": verdict_ids}})
            docs = await cursor.to_list(length=None)
            verdicts_map = {d["verdict_id"]: d for d in docs}

        metrics = feedback_loop.calculate_agreement_metrics(labels, verdicts_map)
        return AgreementMetricsResponse(**metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to compute metrics: {str(e)}")