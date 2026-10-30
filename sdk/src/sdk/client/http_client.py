import logging
import requests
from sdk.core.config import config

logger = logging.getLogger("verbox_sdk")

def check_evaluation(agent_id: str, tool_name: str, arguments: dict) -> dict:
    """
    Calls POST /evaluate. Returns a dict with action/reason/cached_result.
    On a backend error:
      - if config.fail_open: returns a synthetic "allow" so the agent isn't blocked by a verboX-side outage.
    """
    
    url = f"{config.backend_base_url}/evaluate/"
    payload= {
        "agent_id"  : agent_id,
        "tool_name" : tool_name,
        "arguments" : arguments,
        "policy"    : "system_defaults"
    }
    
    try:
        response = requests.post(url=url, json=payload, timeout=config.timeout_seconds)
        response.raise_for_status()
        return response.json()
    
    except requests.RequestException as exc:
        if config.fail_mode:
            logger.warning("Verbox backend unreachable for /evaluate (%s) - fail open, allowing '%s'", exc, tool_name)
            return {
                "action": "allow",
                "reason": f"verboX unreachable, failed open: {exc}",
                "cached_result": None
            }
        raise

def send_trace(span: dict) -> dict | None:
    """
    Calls POST /traces. Fire-and-forget in spirit: failures are logged and swallowed, never raised, since tracing should never break the agent's actual workflow.
    """
    url = f"{config.backend_base_url}/traces/"
    
    try:
        response = requests.post(url=url, json=span, timeout=config.timeout_seconds)
        response.raise_for_status()
        return response.json()
    
    except requests.RequestException as exc:
        logger.warning("Verbox backend unreachable for /traces (%s) - span dropped", exc)
        return None

def complete_trace(trace_id: str) -> dict | None:
    """
    Calls POST /traces/{trace_id}/complete, triggering the Module 2 batch contradiction pass. Call once per run, when the orchestrator finishes.
    """
    url = f"{config.backend_base_url}/traces/{trace_id}/complete"
    
    try:
        response = requests.post(url=url, timeout=config.timeout_seconds)
        response.raise_for_status()
        return response.json()
    
    except requests.RequestException as exc:
        logger.warning("Verbox backend unreachable for /traces/complete (%s).", exc)
        return None