"""FastAPI dependency providers for database clients."""

from typing import AsyncGenerator

from motor.motor_asyncio import AsyncIOMotorDatabase
from redis.asyncio import Redis

from app.db.mongo import get_database
from app.db.redis import get_redis_client


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """Yield a MongoDB database instance for use in route handlers."""
    db = await get_database()
    yield db


async def get_redis() -> Redis:
    """Return the shared Redis client."""
    return await get_redis_client()
