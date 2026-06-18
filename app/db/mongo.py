from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config.settings import settings

_client: AsyncIOMotorClient | None = None


async def init_mongo() -> None:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.mongo_uri)


async def close_mongo() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None


async def get_database() -> AsyncIOMotorDatabase:
    if _client is None:
        await init_mongo()
    return _client[settings.mongo_db]
