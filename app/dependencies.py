from typing import AsyncGenerator

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.db.mongo import get_database
from app.db.redis import get_redis_client
from config.settings import settings


async def get_db() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    db = await get_database()
    yield db


async def get_redis():
    redis_client = await get_redis_client()
    return redis_client
