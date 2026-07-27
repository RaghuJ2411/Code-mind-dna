from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import decode_access_token
from app.models.audit_log import AuditLog


class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        user_email = None
        authorization = request.headers.get("authorization", "")
        if authorization.lower().startswith("bearer "):
            token = authorization[7:].strip()
            try:
                payload = decode_access_token(token)
                user_email = payload.get("sub")
            except Exception:
                user_email = None

        audit_entry = AuditLog(
            user_email=user_email,
            path=request.url.path,
            method=request.method,
            status_code=response.status_code,
            remote_addr=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_metadata_json={"query": dict(request.query_params)} if request.query_params else None,
            created_at=datetime.now(timezone.utc),
        )

        session: Session = SessionLocal()
        try:
            session.add(audit_entry)
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

        return response
