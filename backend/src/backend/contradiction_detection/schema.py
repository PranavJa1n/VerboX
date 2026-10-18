import os

from pydantic import BaseModel, Field

class ContradictionReport(BaseModel):
    is_contradictory : bool = Field(
        description="True if statement A and statement B conflict, False otherwise."
    )
    confidence_score : float = Field(
        description="Confidence score from 0.0 to 1.0"
    )
    reasoning : str = Field(
        description="Step-by-step breakdown of why a contradiction exists or doesn't exist."
    )
