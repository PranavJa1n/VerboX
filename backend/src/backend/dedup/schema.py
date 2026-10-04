from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CacheEntry(BaseModel):
    key: str
    trace_id: str
    result: Optional[dict]
    claimed_by: str
    claimed_at: datetime
    status : str

class ContradictionFlag(BaseModel):
    pass