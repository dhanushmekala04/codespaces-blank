import logging
import time

from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from config.settings import settings

logger = logging.getLogger(__name__)

_client: Redis | None = None
_failed_at: float | None = None          # timestamp of last failed init
_RETRY_COOLDOWN: float = 30.0            # seconds before retrying a failed connection


async def init_redis() -> None:
    global _client, _failed_at

    if _client is not None:
        return

    # Back-off: don't hammer a down Redis on every request
    if _failed_at is not None and (time.monotonic() - _failed_at) < _RETRY_COOLDOWN:
        return

    # Use rediss:// (TLS) for any host that isn't localhost / 127.x
    url = settings.redis_url
    if "localhost" not in url and "127.0.0.1" not in url and not url.startswith("rediss://"):
        url = url.replace("redis://", "rediss://", 1)

    _client = Redis.from_url(url, decode_responses=True)
    try:
        await _client.ping()
        _failed_at = None
        logger.info("Redis connected at %s", url)
    except (RedisConnectionError, OSError, Exception) as exc:
        logger.warning(
            "Redis unavailable (%s) — caching disabled, server will still start.", exc
        )
        await _client.aclose()
        _client = None
        _failed_at = time.monotonic()


async def close_redis() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


async def get_redis_client() -> Redis | None:
    if _client is None:
        # Skip re-init if we're still inside the backoff window
        if _failed_at is None or (time.monotonic() - _failed_at) >= _RETRY_COOLDOWN:
            await init_redis()
    return _client
