from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class SubmitLabelRequest(BaseModel):
    verdict_id: str
    reviewer: str
    reviewer_verdict: str = Field(..., description="'agree', 'disagree', or 'partially_correct'")
    correction_note: Optional[str] = ""

class SubmitLabelResponse(BaseModel):
    label_id: str
    verdict_id: str
    reviewer: str
    reviewer_verdict: str
    correction_note: Optional[str] = ""
    reviewed_at: str

class ReviewFeedItem(BaseModel):
    model_config = {"extra": "allow"}  # verdict docs vary in shape (step vs contradiction)

class AgreementMetricsResponse(BaseModel):
    total: int
    agree: int = 0
    disagree: int = 0
    partially_correct: int = 0
    agreement_rate_pct: float = 0.0
    by_version: Dict[str, Any] = {}