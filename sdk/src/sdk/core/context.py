import contextvars
import uuid

_trace_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("verbox_trace_id", default=None)

def set_trace_id(trace_id: str) -> None:
    """
    This function is used to set the trace ID. Call once per run before dispatching to any agent
    """
    _trace_id_var.set(trace_id)

def new_trace_id() -> str:
    """
    Generate and register a new trace ID. Use at the start of every run
    """
    trace_id = str(uuid.uuid4())
    set_trace_id(trace_id)
    return trace_id

def get_trace_id() -> str:
    """
    Return the active trace ID. If no trace ID is active the generate and register a new trace ID instead of crashing.
    """
    trace_id = _trace_id_var.get()
    if trace_id is None:
        trace_id = new_trace_id()
    return trace_id