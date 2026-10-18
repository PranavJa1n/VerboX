from fastapi import APIRouter, HTTPException, Depends
from backend.schemas.evaluate import EvaluationRequest, EvaluationResponse
from backend.dedup.cache import Cache
from backend.policy.evaluator import evaluate
from backend.policy.schema import PolicyRule
from backend.api.dependencies import get_policy_rules

router = APIRouter()

dedup_cache = Cache()


@router.post("/", response_model=EvaluationResponse)
async def evaluate_tool_call(request: EvaluationRequest, rules_by_tool: dict[str, list[PolicyRule]] = Depends(get_policy_rules),):
    """
    Tier 1 Gatekeeper: Evaluates deterministic policies and intercepts duplicate calls.
    """
    try:
        # GATE 1: Deterministic Policy Check (the YAML rules)
        policy_decision = evaluate(
            tool_name=request.tool_name,
            arguments=request.arguments,
            rules_by_tool=rules_by_tool,
        )
 
        if policy_decision.decision == "block":
            return EvaluationResponse(
                action="block",
                reason=policy_decision.message or "Blocked by policy.",
                cached_result=None,
            )
 
        # GATE 2: The Dedup / Cache Check
        cached_data = dedup_cache.orchestrator(request)
 
        if cached_data is not False:
            # cache hit Stop the agent from executing.
            return EvaluationResponse(
                action="cache_hit",
                reason="Redundant tool call intercepted by verboX shared cache.",
                cached_result=cached_data,
            )
        
        # PASSED: The agent is clear to execute
        
        return EvaluationResponse(
            action="allow",
            reason="Passed Tier 1 policies and cache miss.",
            cached_result=None,
        )
 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"verboX Internal Error: {str(e)}")