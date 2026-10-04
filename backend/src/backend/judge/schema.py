from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel, Field

@dataclass
class Flag:
    type: str
    severity: float
    reason: str

@dataclass
class Verdict:
    verdict_id: str
    trace_id: str
    span_id: str
    flags: list[Flag]
    judge_model: str
    prompt_version: str
    evaluated_at: datetime

class FlagOutput(BaseModel):
    type: str = Field(description="e.g. 'risky', 'redundant', 'policy_violation'")
    severity: float = Field(description="0.0 to 1.0, how serious this flag is")
    reason: str = Field(description="Why this flag was raised")

class VerdictOutput(BaseModel):
    flags: list[FlagOutput] = Field(
        default_factory=list,
        description="Empty list if the step is clean, with no issues found.",
    )