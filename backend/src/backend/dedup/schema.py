from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CacheEntry(BaseModel):
    key: str
    trace_id: str
    result: Optional[dict] = None
    claimed_by: str
    claimed_at: datetime
    status : str

class ContradictionFlag(BaseModel):
    trace_id: str
    tool_name: str
    arguments: dict
    cached_result: Optional[dict] = None
    new_result: Optional[dict] = None
    reason: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)