import logging

from app.db.database import AsyncSessionLocal, Base, engine
from app.db.models import Message
from sqlalchemy import select

logger = logging.getLogger(__name__)


async def init_db_and_seed():
    "Creates tables and populates them with test data"
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Message).limit(1))
        first_msg = result.scalars().first()

        if not first_msg:
            logger.info("The database is empty. Adding mock messages...")
            messages = [
                Message(text=f"This is test message number {i} for API testing")
                for i in range(1, 16)
            ]
            session.add_all(messages)
            await session.commit()
            logger.info("Mock data added successfully")
        else:
            logger.info("The data already exists, skip the seed")
