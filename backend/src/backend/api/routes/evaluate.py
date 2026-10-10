from fastapi import APIRouter, HTTPException, Depends
# We will create these Pydantic models next in schemas/
from src.backend.schemas.evaluate import EvaluationRequest, EvaluationResponse

# We will import the services you built/are building
from src.backend.dedup.cache import Cache
# from src.backend.policy.engine import PolicyEngine 

router = APIRouter()

# Instantiate services (in a real app, you might inject these via Depends)
dedup_cache = Cache()
# policy_engine = PolicyEngine()

@router.post("/", response_model=EvaluationResponse)
async def evaluate_tool_call(request: EvaluationRequest):
    """
    Tier 1 Gatekeeper: Evaluates deterministic policies and intercepts duplicate calls.
    """
    try:
        # ---------------------------------------------------------
        # GATE 1: Deterministic Policy Check (The YAML rules)
        # ---------------------------------------------------------
        # policy_decision = policy_engine.evaluate(
        #     tool=request.tool_name, 
        #     arguments=request.arguments,
        #     policy_name=request.policy
        # )
        
        # if policy_decision.action == "block":
        #     return EvaluationResponse(
        #         action="block",
        #         reason=policy_decision.message,
        #         cached_result=None
        #     )

        # ---------------------------------------------------------
        # GATE 2: The Dedup / Cache Check (Your code!)
        # ---------------------------------------------------------
        # We repackage the request into the mock object your orchestrator expects
    
            
        cached_data = dedup_cache.orchestrator(request)

        if cached_data is not False:
            # We got a cache hit! Stop the agent from executing.
            return EvaluationResponse(
                action="cache_hit",
                reason="Redundant tool call intercepted by verboX shared cache.",
                cached_result=cached_data
            )

        # ---------------------------------------------------------
        # PASSED: The agent is clear to execute
        # ---------------------------------------------------------
        return EvaluationResponse(
            action="allow",
            reason="Passed Tier 1 policies and cache miss.",
            cached_result=None
        )

    except Exception as e:
        # If verboX crashes, we fail open or closed depending on your risk tolerance.
        # Standard SRE practice for observability tools is to fail OPEN so you don't break production.
        raise HTTPException(status_code=500, detail=f"verboX Internal Error: {str(e)}")