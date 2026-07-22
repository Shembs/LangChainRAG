"""Redis-based three-tier caching for RAG queries."""
import hashlib
import json
from typing import Optional

from app.core.redis_client import get_redis


async def get_exact_cache(query: str) -> Optional[dict]:
    """L1: Exact match cache using MD5 hash of the query.

    Args:
        query: The user's exact question.

    Returns:
        Cached response dict or None if not found.
    """
    redis = get_redis()
    if not redis:
        return None

    key = f"cache:exact:{hashlib.md5(query.encode()).hexdigest()}"
    try:
        data = await redis.get(key)
        if data:
            return json.loads(data)
    except Exception:
        pass
    return None


async def set_exact_cache(query: str, response: dict, ttl: int = 3600) -> None:
    """Store an exact match cache entry.

    Args:
        query: The user's exact question.
        response: The full response dict to cache.
        ttl: Time-to-live in seconds (default 1 hour).
    """
    redis = get_redis()
    if not redis:
        return

    key = f"cache:exact:{hashlib.md5(query.encode()).hexdigest()}"
    try:
        await redis.setex(key, ttl, json.dumps(response, ensure_ascii=False))
    except Exception:
        pass


async def get_semantic_cache(query_embedding: list, threshold: float = 0.92) -> Optional[dict]:
    """L2: Semantic similarity cache.

    NOTE: This requires Redis Stack (RedisVL) or custom vector similarity in Redis.
    For simplicity, we implement a basic approach using a separate collection.
    In production, use Redis Stack with vector similarity search.

    Args:
        query_embedding: The query embedding vector.
        threshold: Minimum cosine similarity (0-1) for cache hit.

    Returns:
        Cached response dict or None if not found.
    """
    # Semantic cache is a more advanced feature
    # For now, return None (miss) to use L1 only
    # Full implementation would use Redis Stack's VSS or RedisVL
    return None


async def set_semantic_cache(query_embedding: list, response: dict, ttl: int = 3600) -> None:
    """Store a semantic cache entry.

    NOTE: Requires Redis Stack for full vector similarity.
    """
    pass  # Placeholder for Redis Stack vector similarity


async def get_session_context(session_id: str) -> Optional[dict]:
    """L3: Get cached session context (recent conversation).

    Args:
        session_id: The conversation session ID.

    Returns:
        Session context dict or None.
    """
    redis = get_redis()
    if not redis:
        return None

    key = f"session:{session_id}"
    try:
        data = await redis.get(key)
        if data:
            return json.loads(data)
    except Exception:
        pass
    return None


async def set_session_context(session_id: str, context: dict, ttl: int = 1800) -> None:
    """Cache session context with sliding TTL.

    Args:
        session_id: The conversation session ID.
        context: Session context to cache.
        ttl: Time-to-live in seconds (default 30 minutes).
    """
    redis = get_redis()
    if not redis:
        return

    key = f"session:{session_id}"
    try:
        await redis.setex(key, ttl, json.dumps(context, ensure_ascii=False))
    except Exception:
        pass


async def clear_cache() -> int:
    """Clear all query caches. Returns number of keys deleted."""
    redis = get_redis()
    if not redis:
        return 0

    try:
        keys = []
        async for key in redis.scan_iter("cache:*"):
            keys.append(key)
        if keys:
            return await redis.delete(*keys)
    except Exception:
        pass
    return 0


async def check_rate_limit(user_id: str, max_requests: int = 30, window: int = 60) -> bool:
    """Check if user has exceeded rate limit.

    Args:
        user_id: The user's ID.
        max_requests: Max requests allowed in the window.
        window: Time window in seconds.

    Returns:
        True if allowed, False if rate limited.
    """
    redis = get_redis()
    if not redis:
        return True  # Allow if Redis is down

    key = f"rate_limit:user:{user_id}"
    try:
        current = await redis.get(key)
        if current and int(current) >= max_requests:
            return False

        pipe = redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, window)
        await pipe.execute()
        return True
    except Exception:
        return True
