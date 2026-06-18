from redis.asyncio import Redis

from config.settings import settings

_client: Redis | None = None


async def init_redis() -> None:
    global _client
    if _client is None:
        _client = Redis.from_url(settings.redis_url, decode_responses=True)
        await _client.ping()


async def close_redis() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None


async def get_redis_client() -> Redis:
    if _client is None:
        await init_redis()
    return _client
