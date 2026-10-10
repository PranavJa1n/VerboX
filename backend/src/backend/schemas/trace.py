# backend/src/backend/schemas/trace.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict, Optional
from datetime import datetime

class TraceSpan(BaseModel):
    """
    Represents a single agent action/tool execution following OpenTelemetry GenAI semantic conventions.
    """
    trace_id: str = Field(
        ..., 
        description="Shared thread_id across all agents working on the same task."
    )
    span_id: str = Field(
        ..., 
        description="Unique identifier for this specific tool execution event."
    )
    parent_span_id: Optional[str] = Field(
        default=None, 
        description="The ID of the parent span, used to reconstruct the execution tree."
    )
    agent_id: str = Field(
        ..., 
        description="The identifier of the agent executing the action (e.g., 'remediation_engineer')."
    )

    # OpenTelemetry (OTel) Semantic Fields
    # We use Pydantic aliases because Python variables cannot contain dots.
    operation_name: str = Field(
        default="tool_call",
        alias="gen_ai.operation.name",
        description="The type of operation (e.g., 'tool_call', 'agent_reasoning')."
    )
    tool_name: str = Field(
        ...,
        alias="gen_ai.tool.name",
        description="The executed tool's name."
    )
    tool_arguments: Dict[str, Any] = Field(
        default_factory=dict,
        alias="gen_ai.tool.call.arguments",
        description="The payload passed to the tool."
    )
    tool_result: Optional[Dict[str, Any]] = Field(
        default=None,
        alias="gen_ai.tool.call.result",
        description="The output returned by the tool."
    )

    reasoning_snippet: Optional[str] = Field(
        default=None,
        description="The LLM's thought process or scratchpad leading to this action."
    )
    start_time: datetime = Field(
        ..., 
        description="When the tool execution began."
    )
    end_time: datetime = Field(
        ..., 
        description="When the tool execution completed."
    )

    # Config to allow SDKs and internal code to use snake_case 
    # while parsing/serializing the dotted OTel JSON keys.
    model_config = ConfigDict(populate_by_name=True)

class TraceIngestionResponse(BaseModel):
    status: str = Field(default="accepted")
    span_id: str
    message: str = Field(default="Span queued for Tier 2 evaluation.")