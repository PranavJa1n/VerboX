import asyncio
from dataclasses import asdict
from fastapi import APIRouter, BackgroundTasks, status
from backend.schemas.trace import TraceSpan, TraceIngestionResponse
from backend.mongo_util.mongo_client import mongo_client
from backend.judge.judge import evaluate
from backend.dedup.cache import Cache
from backend.schemas.evaluate import EvaluationRequest
from backend.contradiction_detection.engine import AgnosticContradictionEngine
import uuid
from backend.judge.judge import Verdict, Flag
from backend.judge.prompt import PROMPT_VERSION
from datetime import datetime

dedup_cache = Cache()
router = APIRouter()
contradiction_engine = AgnosticContradictionEngine()

async def process_and_store_trace(span: TraceSpan):
    """
    This function runs entirely in the background after the HTTP connection closes.
    If it crashes, it drops the trace, but the agent's workflow is never interrupted.
    """
    try:
        if span.tool_result:
            mock_request = EvaluationRequest(
                        agent_id=span.agent_id,
                        tool_name=span.tool_name,
                        arguments=span.tool_arguments,
                        policy="system_defaults"
                )
            dedup_cache.save_result(mock_request, span.tool_result)
        
        # Convert the Pydantic model to a dict, using the OTel alias names
        span_data = span.model_dump(by_alias=True)
        await mongo_client.save_span(span_data)
        print(f"Background: Successfully saved span {span.span_id} for trace {span.trace_id}")
        
        # now trigger the tier 2 LLM judge.
        step = {
            "trace_id": span.trace_id,
            "span_id": span.span_id,
            "tool_name": span.tool_name,
            "arguments": span.tool_arguments,
            "result": span.tool_result,
        }
        verdict = await asyncio.to_thread(evaluate, step)

        await mongo_client.save_verdict(verdict.model_dump())
        
        print(f"Background: Verdict stored for span {span.span_id} ({len(verdict.flags)} flags)")
    
    except Exception as e:
        
        # We log the failure internally, but the agent never sees this error.
        print(f"Background: Dropped trace {span.span_id} due to error: {e}")

@router.post("/", response_model=TraceIngestionResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_trace(span: TraceSpan, background_tasks: BackgroundTasks):
    """
    Fire-and-forget telemetry endpoint.
    Accepts GenAI OTel spans and queues them for asynchronous DB storage and Tier 2 evaluation.
    """
    
    # 1. Instantly offload the heavy lifting to the FastAPI background thread pool
    background_tasks.add_task(process_and_store_trace, span)

    # 2. Return success to the SDK in less than 5 milliseconds
    return TraceIngestionResponse(
        status="accepted",
        span_id=span.span_id,
        message="Span buffered for asynchronous processing."
    )

async def run_batch_deep_pass(trace_id: str):
    """Runs when the swarm finishes a task (The Batch Deep Pass)."""
    try:
        print(f"\n🧠 [Module 2] Starting Batch Deep Pass for Swarm Trace: {trace_id}")
        
        all_spans = await mongo_client.get_spans_by_trace(trace_id)
        
        swarm_claims = []
        for span in all_spans:
            if span.get("reasoning_snippet"):
                swarm_claims.append(span["reasoning_snippet"])
            if span.get("gen_ai.tool.call.result"):
                swarm_claims.append(str(span["gen_ai.tool.call.result"]))
        
        print(f"📊 [Module 2] Extracted {len(swarm_claims)} claims. Running Stage 1 & 2 Pairwise Combinatorics...")
        
        contradictions = await asyncio.to_thread(contradiction_engine.analyze_swarm_claims, swarm_claims)
        
        if contradictions:
            print(f"🚨 [Module 2] CONTRADICTIONS DETECTED! 🚨")
            for c in contradictions:
                print(f"   Conflict: '{c['statement_a']}' VS '{c['statement_b']}'")
                print(f"   Severity: {c['severity']} | Reason: {c['reasoning']}")
                
            # await mongo_client.save_verdict({
            #     "trace_id": trace_id,
            #     "flags": [{
            #         "type": "multi_agent_contradiction",
            #         "severity": c["severity"],
            #         "reason": c["reasoning"]
            #     } for c in contradictions]
            # })

            verdict = Verdict(
                verdict_id=str(uuid.uuid4()),
                verdict_type="contradiction",
                trace_id=trace_id,
                span_id=None,
                flags=[
                    Flag(
                        type="multi_agent_contradiction",
                        severity=c["severity"],
                        reason=c["reasoning"],
                    )
                    for c in contradictions
                ],
                judge_model="gpt-4o",
                prompt_version=PROMPT_VERSION,
                evaluated_at=datetime.now(),
            )

            await mongo_client.save_verdict(verdict.model_dump())
            print(f"💾 [Module 2] Contradiction Verdict saved to Cosmos DB.")
        else:
            print(f"✅ [Module 2] Swarm is logically consistent. No contradictions found.")

    except Exception as e:
        print(f"❌ Batch Deep Pass failed: {e}")

@router.post("/{trace_id}/complete", status_code=202)
async def complete_trace(trace_id: str, background_tasks: BackgroundTasks):
    """Endpoint called by the SDK when the LangGraph thread finishes."""
    background_tasks.add_task(run_batch_deep_pass, trace_id)
    return {"message": "Batch deep pass initiated for swarm trace."}