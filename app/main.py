import asyncio
import logging
from contextlib import asynccontextmanager

from app.db.database import get_db
from app.db.models import Message
from app.db.seed import init_db_and_seed
from fastapi import Depends, FastAPI, HTTPException, Request
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel, Field
from pythonjsonlogger import jsonlogger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.propagate = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    await init_db_and_seed()
    logger.info("Application ready!")
    yield


app = FastAPI(title="Observability App", lifespan=lifespan)


instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=["/metrics"],
)
instrumentator.instrument(app).expose(app)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    if request.url.path != "/metrics":
        logger.info(
            "Request processed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
            },
        )
    return response


class ProcessRequest(BaseModel):
    data: str = Field(..., description="Данные", min_length=1, max_length=500)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/message/{message_id}")
async def get_message(message_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalars().first()
    if not message:
        raise HTTPException(status_code=404, detail="Message is not found")
    return {"id": message.id, "text": message.text}


@app.post("/process")
async def process_data(request: ProcessRequest):
    await asyncio.sleep(0.5)
    return {"echo": request.data}
