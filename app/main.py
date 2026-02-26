import asyncio

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Observability App")


class ProcessRequest(BaseModel):
    data: str = Field(..., description="Data to research")


@app.get("/health")
async def health_check():
    "Simple healthcheck"
    return {"status": "healthy"}


@app.post("/process")
async def process_data(request: ProcessRequest):
    "Heavy process simulation for metrics"
    await asyncio.sleep(0.5)
    return {"echo": request.data}
