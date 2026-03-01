import asyncio
import logging
import time
from contextlib import asynccontextmanager
from crypt import methods

from app.db.database import get_db
from app.db.models import Message
from app.db.seed import init_db_and_seed
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field
from pythonjsonlogger import jsonlogger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
logHandler.setFormatter(formatter)
logger.propagate = False

REQUESTS_TOTAL = Counter(
    "fastapi_requests_total", "Total number of requests", ["method", "endpoint"]
)
REQUEST_LATENCY = Histogram(
    "fastapi_request_latency_seconds",
    "Request latency in seconds",
    ["method", "endpoint"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    await init_db_and_seed()
    logger.info("Application ready")
    yield


app = FastAPI(title="Observability App", lifespan=lifespan)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    if request.url.path != "/metrics":
        REQUESTS_TOTAL.labels(method=request.method, endpoint=request.url.path).inc()
        REQUEST_LATENCY.labels(
            method=request.method, endpoint=request.url.path
        ).observe(process_time)
    return response


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


@app.get("/message/{message_id}")
async def get_message(message_id: int, db: AsyncSession = Depends(get_db)):
    "Gets a message from the database by ID"
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalars().first()

    if not message:
        raise HTTPException(status_code=404, detail="Message is not found")
    return {"id": message.id, "text": message.text}


@app.get("/metrics")
async def get_metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
