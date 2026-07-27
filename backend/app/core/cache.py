"""Simple in-memory cache utility for read-heavy endpoints."""

import time
import threading
from typing import Any, Callable, Optional


class TimedCache:
    """Thread-safe in-memory cache with TTL support."""

    def __init__(self, default_ttl_seconds: int = 60):
        self._default_ttl = default_ttl_seconds
        self._cache: dict[str, tuple[Any, float]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache. Returns None if missing or expired."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            value, expiry = entry
            if time.time() > expiry:
                del self._cache[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """Set a value in cache with optional TTL."""
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        expiry = time.time() + ttl
        with self._lock:
            self._cache[key] = (value, expiry)

    def delete(self, key: str) -> None:
        """Remove a key from cache."""
        with self._lock:
            self._cache.pop(key, None)

    def clear(self) -> None:
        """Clear all cached entries."""
        with self._lock:
            self._cache.clear()

    def get_or_set(self, key: str, factory: Callable[[], Any], ttl_seconds: Optional[int] = None) -> Any:
        """Get from cache or compute and store."""
        value = self.get(key)
        if value is not None:
            return value
        value = factory()
        self.set(key, value, ttl_seconds)
        return value


# Global cache instance
response_cache = TimedCache(default_ttl_seconds=60)


def cached(ttl_seconds: int = 60):
    """Decorator to cache function results.

    Usage:
        @cached(ttl_seconds=120)
        def get_expensive_data():
            ...
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            # Build a cache key from function name and args
            key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            return response_cache.get_or_set(key, lambda: func(*args, **kwargs), ttl_seconds)
        return wrapper
    return decorator
