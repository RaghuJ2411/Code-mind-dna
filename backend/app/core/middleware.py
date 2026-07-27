"""Security headers, request body size limiting, and request ID tracing middleware."""

import uuid
import time
import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings

logger = logging.getLogger("codemind.middleware")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        if settings.security_headers_enabled:
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = (
                f"max-age={settings.hsts_max_age_seconds}; includeSubDomains"
            )
            response.headers["Content-Security-Policy"] = settings.content_security_policy
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = (
                "camera=(), microphone=(), geolocation=(), interest-cohort=()"
            )
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"
        return response


class RequestBodySizeMiddleware(BaseHTTPMiddleware):
    """Limit the maximum request body size."""

    async def dispatch(self, request: Request, call_next: Callable):
        content_length = request.headers.get("content-length")
        if content_length:
            size_bytes = int(content_length)
            max_bytes = settings.max_request_body_size_mb * 1024 * 1024
            if size_bytes > max_bytes:
                return JSONResponse(
                    status_code=413,
                    content={
                        "detail": f"Request body too large. Max: {settings.max_request_body_size_mb}MB"
                    },
                )
        return await call_next(request)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add a unique request ID for tracing."""

    async def dispatch(self, request: Request, call_next: Callable):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-MS"] = f"{process_time * 1000:.1f}"
        logger.debug(
            "Request processed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_ms": round(process_time * 1000, 1),
            },
        )
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with structured context."""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        if response.status_code >= 400:
            logger.warning(
                "Request failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "client_host": request.client.host if request.client else None,
                },
            )
        else:
            logger.info(
                "Request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                },
            )
        return response

