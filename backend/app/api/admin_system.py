from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole
from app.schemas.admin import (
    SystemLogListResponse,
    SystemLogEntry,
    SystemOverviewResponse,
    SystemServicesResponse,
    SystemServiceItem,
)

router = APIRouter(prefix="/admin/system", tags=["admin-system"])


@router.get("/overview", response_model=SystemOverviewResponse)
def system_overview(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    total_users = db.scalar(select(func.count(User.id))) or 0
    active_users = db.scalar(select(func.count(User.id)).where(User.is_active.is_(True))) or 0
    total_audit = db.scalar(select(func.count(AuditLog.id))) or 0

    return SystemOverviewResponse(
        uptime_seconds=0,
        cpu_percent=0,
        memory_percent=0,
        disk_percent=0,
        active_requests=total_audit,
        database_size_mb=0,
    )


@router.get("/services", response_model=SystemServicesResponse)
def system_services(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    services = [
        SystemServiceItem(name="API Server", status="healthy"),
        SystemServiceItem(name="Database", status="healthy"),
        SystemServiceItem(name="Authentication", status="healthy"),
        SystemServiceItem(name="Code Execution", status="healthy" if False else "degraded"),
    ]
    return SystemServicesResponse(services=services)


@router.get("/logs", response_model=SystemLogListResponse)
def system_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    level: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    page = max(page, 1)
    page_size = max(min(page_size, 100), 1)
    query = db.query(AuditLog)
    if level:
        if level.upper() == "ERROR":
            query = query.filter(AuditLog.status_code >= 500)
        elif level.upper() == "WARN":
            query = query.filter(AuditLog.status_code >= 400, AuditLog.status_code < 500)

    total = query.count()
    items = query.order_by(AuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    log_entries = [
        SystemLogEntry(
            id=item.id,
            level="ERROR" if item.status_code >= 500 else "WARN" if item.status_code >= 400 else "INFO",
            message=f"{item.method} {item.path} → {item.status_code}",
            source=item.user_email or "system",
            created_at=item.created_at,
        )
        for item in items
    ]

    return SystemLogListResponse(
        items=log_entries,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max((total + page_size - 1) // page_size, 1),
    )

