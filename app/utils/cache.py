"""Redis caching utilities for high-performance data access."""

import json
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.config import settings

# Global Redis connection pool (reused across requests)
_redis_pool: Optional[Redis] = None

F = TypeVar("F", bound=Callable[..., Any])


async def get_redis() -> Redis:
    """Get Redis connection from pool."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = await aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,  # Connection pool size
            socket_connect_timeout=5,
            socket_keepalive=True,
            health_check_interval=30,
        )
    return _redis_pool


async def close_redis() -> None:
    """Close Redis connection pool."""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.close()
        _redis_pool = None


class Cache:
    """High-performance caching utilities."""

    @staticmethod
    async def get(key: str) -> Optional[Any]:
        """Get value from cache."""
        redis_client = await get_redis()
        value = await redis_client.get(key)
        if value:
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        return None

    @staticmethod
    async def set(
        key: str,
        value: Any,
        ttl: int = 3600,
        serialize: bool = True,
    ) -> bool:
        """Set value in cache with TTL."""
        redis_client = await get_redis()
        if serialize:
            value = json.dumps(value)
        return await redis_client.setex(key, ttl, value)

    @staticmethod
    async def delete(key: str) -> bool:
        """Delete key from cache."""
        redis_client = await get_redis()
        return await redis_client.delete(key) > 0

    @staticmethod
    async def delete_pattern(pattern: str) -> int:
        """Delete all keys matching pattern."""
        redis_client = await get_redis()
        keys = []
        async for key in redis_client.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            return await redis_client.delete(*keys)
        return 0

    @staticmethod
    async def exists(key: str) -> bool:
        """Check if key exists."""
        redis_client = await get_redis()
        return await redis_client.exists(key) > 0

    @staticmethod
    async def increment(key: str, amount: int = 1) -> int:
        """Increment counter."""
        redis_client = await get_redis()
        return await redis_client.incrby(key, amount)

    @staticmethod
    async def get_or_set(
        key: str,
        callable_func: Callable[[], Any],
        ttl: int = 3600,
    ) -> Any:
        """Get from cache or compute and cache."""
        value = await Cache.get(key)
        if value is None:
            if callable_func:
                value = await callable_func() if callable_func.__code__.co_flags & 0x80 else callable_func()
            await Cache.set(key, value, ttl=ttl)
        return value


def cached(ttl: int = 3600, key_prefix: str = ""):
    """Decorator to cache function results."""

    def decorator(func: F) -> F:
        import inspect
        
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                # Generate cache key
                cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # Try cache first
                cached_value = await Cache.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # Compute and cache
                result = await func(*args, **kwargs)
                await Cache.set(cache_key, result, ttl=ttl)
                return result
            
            return async_wrapper  # type: ignore
        else:
            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                # Generate cache key
                cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                # For sync functions, we'd need sync Redis client
                # For now, just execute without caching
                # TODO: Add sync Redis support if needed
                return func(*args, **kwargs)
            
            return sync_wrapper  # type: ignore

    return decorator
