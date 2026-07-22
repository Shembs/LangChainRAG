from redis.asyncio import Redis
from app.config import settings

redis_client: Redis = None  # type: ignore


async def init_redis():
    """Initialize Redis connection pool. Called at app startup."""
    global redis_client
    redis_client = Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=False,
    )


async def close_redis():
    """Close Redis connection. Called at app shutdown."""
    global redis_client
    if redis_client:
        await redis_client.close()


def get_redis() -> Redis:
    """FastAPI dependency: returns the Redis client."""
    return redis_client
