from fastapi import APIRouter
from .routes import evaluate, traces, metrics, feedback

api_router = APIRouter()

# Attach the sub-routers
api_router.include_router(evaluate.router, prefix="/evaluate", tags=["Evaluation"])
api_router.include_router(traces.router, prefix="/traces", tags=["Telemetry"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["Dashboard"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Human Feedback"])