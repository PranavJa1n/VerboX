import functools
import uuid
from datetime import datetime, timezone
from sdk.client.http_client import send_trace
from sdk.core.context import get_trace_id

def trace(agent_id: str):
    """
    Decorator for a tool function. Runs the real function,
    then sends a span describing what happened to verboX's /traces endpoint.
    Never affects the wrapped function's return value or
    exceptions tracing failures are swallowed inside http_client.send_trace().

    Usage:
        @trace(agent_id="tool_name")
        def function():
            ...
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            span_id = str(uuid.uuid4())
            start_time = datetime.now(timezone.utc)
            
            result = func(*args, **kwargs)

            end_time = datetime.now(timezone.utc)

            span = {
                "trace_id": get_trace_id(),
                "span_id": span_id,
                "agent_id": agent_id,
                "gen_ai.operation.name": "tool_call",
                "gen_ai.tool.name": func.__name__,
                "gen_ai.tool.call.arguments": kwargs if kwargs else {"args": args},
                "gen_ai.tool.call.result": result,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            }

            send_trace(span)
            
            return result
        
        return wrapper
    
    return decorator