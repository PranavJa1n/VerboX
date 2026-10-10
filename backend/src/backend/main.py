# Fast API entrypoints

from fastapi import FastAPI
from src.backend.api.router import api_router

app = FastAPI(title="verboX Control Plane", version="1.0.0")

app.include_router(api_router, prefix="/api/v1")