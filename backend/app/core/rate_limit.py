from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings


class InMemoryRateLimiter:
    def __init__(self, limit: int, window_seconds: int):
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: dict[tuple[str, str], list[float]] = defaultdict(list)
        self._lock = Lock()

    def allow(self, key: str, endpoint: str) -> bool:
        now = time.time()
        bucket_key = (key, endpoint)
        with self._lock:
            timestamps = self._requests[bucket_key]
            timestamps[:] = [ts for ts in timestamps if now - ts < self.window_seconds]
            if len(timestamps) >= self.limit:
                return False
            timestamps.append(now)
            return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, *, limit: int = 8, window_seconds: int = 30):
        super().__init__(app)
        self.limiter = InMemoryRateLimiter(limit=limit, window_seconds=window_seconds)
        self.auth_limiter = InMemoryRateLimiter(
            limit=settings.auth_rate_limit_attempts,
            window_seconds=settings.auth_rate_limit_window_seconds,
        )
        self.execution_limiter = InMemoryRateLimiter(limit=limit, window_seconds=window_seconds)

    async def dispatch(self, request: Request, call_next):
        client_key = request.client.host if request.client else "unknown"

        # Auth endpoints get stricter rate limiting
        if request.url.path in {"/api/auth/login", "/api/auth/register"} and request.method == "POST":
            if not self.auth_limiter.allow(client_key, request.url.path):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many authentication attempts. Please try again later."},
                )

        # Execution endpoints get separate rate limiting
        if request.url.path in {"/api/execution/run", "/api/execution/submit"}:
            if not self.execution_limiter.allow(client_key, request.url.path):
                return JSONResponse(status_code=429, content={"detail": "Too many execution requests"})

        return await call_next(request)
