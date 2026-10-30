import functools
from sdk.client.http_client import check_evaluation

class PolicyBlokedError(Exception):
    """Raised when verboX's Tier 1 policy check blocks a tool call."""
    pass

def guard(agent_id: str):
    """
    Decorator for a tool function. Before the real tool runs, calls verboX's /evaluate endpoint:
      - "block"     -> raises PolicyBlockedError, real tool never runs.
      - "cache_hit" -> returns the cached result directly, real tool never runs.
      - "allow"     -> runs the real tool normally.
    Usage:
        @guard(agent_id="tool_name")
        def function():
            ...
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tool_name = func.__name__
            arguments = kwargs if kwargs else {"args": args}

            decision = check_evaluation(agent_id=agent_id, tool_name=tool_name, arguments=arguments)
            action = decision.get("action")

            if action == "block":
                raise PolicyBlokedError(decision.get("reason", "Blocked by verboX policy"))

            if action == "cache_hit":
                return decision.get("cached_result")

            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator