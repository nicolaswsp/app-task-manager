from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel

from app.api.task_routes import router as task_router

app = FastAPI(title="Task Management Micro-API", version="0.1.0")
app.include_router(task_router)


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow()
    )
