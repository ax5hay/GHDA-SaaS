"""Performance optimization utilities."""

import time
from functools import wraps
from typing import Any, Callable, TypeVar

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

F = TypeVar("F", bound=Callable[..., Any])


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to add performance headers and logging."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """Add performance headers to response."""
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(round(process_time, 4))
        response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "unknown")
        
        # Log slow requests (>1 second)
        if process_time > 1.0:
            print(f"⚠️  Slow request: {request.method} {request.url.path} took {process_time:.2f}s")
        
        return response


def measure_time(func: F) -> F:
    """Decorator to measure function execution time."""
    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.time()
        result = await func(*args, **kwargs)
        duration = time.time() - start
        if duration > 0.5:  # Log slow operations
            print(f"⏱️  {func.__name__} took {duration:.3f}s")
        return result
    
    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        if duration > 0.5:  # Log slow operations
            print(f"⏱️  {func.__name__} took {duration:.3f}s")
        return result
    
    # Return appropriate wrapper based on function type
    import inspect
    if inspect.iscoroutinefunction(func):
        return async_wrapper  # type: ignore
    return sync_wrapper  # type: ignore


class QueryOptimizer:
    """Utilities for optimizing database queries."""
    
    @staticmethod
    def limit_fields(fields: list[str], max_fields: int = 20) -> list[str]:
        """Limit number of fields to prevent large queries."""
        return fields[:max_fields]
    
    @staticmethod
    def paginate_query(offset: int, limit: int, max_limit: int = 100) -> tuple[int, int]:
        """Validate and limit pagination parameters."""
        offset = max(0, offset)
        limit = min(max_limit, max(1, limit))
        return offset, limit
