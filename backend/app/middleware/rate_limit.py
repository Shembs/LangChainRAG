"""Redis-based rate limiting middleware."""
import time
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.redis_client import get_redis


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple sliding-window rate limiter using Redis."""

    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path == "/api/v1/system/health":
            return await call_next(request)

        redis = get_redis()
        if redis is None:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}:{request.url.path}"

        try:
            current = await redis.get(key)
            if current and int(current) >= self.max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="请求过于频繁，请稍后再试",
                )

            pipe = redis.pipeline()
            pipe.incr(key)
            pipe.expire(key, self.window_seconds)
            await pipe.execute()
        except HTTPException:
            raise
        except Exception:
            # If Redis is down, allow the request through
            pass

        return await call_next(request)
