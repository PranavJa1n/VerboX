# Fast API entrypoints

from fastapi import FastAPI
from backend.api.router import api_router

app = FastAPI(title="verboX Control Plane", version="1.0.0")


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api/v1")