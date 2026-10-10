from pydantic import BaseModel, Field
from typing import Any, Dict, Optional, Literal

class EvaluationRequest(BaseModel):
    agent_id : str = Field(
        ...,
        description = "The unique identifier of the agent in the swarm (e.g., 'pixos_telemetry_agent')."
    )
    tool_name: str = Field(
        ..., 
        description="The exact name of the registered tool the agent is attempting to call."
    )
    arguments: Dict[str, Any] = Field(
        default_factory=dict, 
        description="The JSON payload/arguments the agent generated for the tool."
    )
    policy: str = Field(
        default="system_defaults", 
        description="The name of the YAML policy ruleset to evaluate this action against."
    )

class EvaluationResponse(BaseModel):
    action: Literal["allow", "block", "cache_hit"] = Field(
        ..., 
        description="The definitive Tier 1 decision. 'allow' proceeds to execution, 'block' stops it, 'cache_hit' returns data."
    )
    reason: str = Field(
        ..., 
        description="The human-readable explanation for the decision, fed back to the agent's context."
    )
    cached_result: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="The resolved tool payload if a duplicate intent was intercepted."
    )