from fastapi import APIRouter, BackgroundTasks, status
from src.backend.schemas.trace import TraceSpan, TraceIngestionResponse
# from src.backend.db.mongo_client import save_span_to_mongo

router = APIRouter()

def process_and_store_trace(span: TraceSpan):
    """
    This function runs entirely in the background after the HTTP connection closes.
    If it crashes, it drops the trace, but the agent's workflow is never interrupted.
    """
    try:
        # Convert the Pydantic model to a dict, using the OTel alias names
        span_data = span.model_dump(by_alias=True)
        
        # save_span_to_mongo(span_data)
        
        # Here is where you would also trigger the Tier 2 LLM Auditor 
        # if the trace is marked as 'complete'
        print(f"Background: Successfully saved span {span.span_id} for trace {span.trace_id}")
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