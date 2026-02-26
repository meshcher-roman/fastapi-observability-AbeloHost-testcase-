import asyncio
from contextlib import asynccontextmanager

from app.db.database import get_db
from app.db.models import Message
from app.db.seed import init_db_and_seed
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_and_seed()
    yield


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


@app.get("/message/{message_id}")
async def get_message(message_id: int, db: AsyncSession = Depends(get_db)):
    "Gets a message from the database by ID"
    result = await db.execute(select(Message).where(Message.id == message_id))
    message = result.scalars().first()

    if not message:
        raise HTTPException(status_code=404, detail="Message is not found")
    return {"id": message.id, "text": message.text}
