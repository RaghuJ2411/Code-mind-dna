from fastapi import APIRouter, Depends
from sqlalchemy import func, inspect, select, text
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import engine, get_db
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole
from app.schemas.admin import (
    DatabaseHealthResponse,
    DatabaseTableInfo,
    DatabaseTablesResponse,
)

router = APIRouter(prefix="/admin/database", tags=["admin-database"])


@router.get("/health", response_model=DatabaseHealthResponse)
def database_health(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    try:
        db.execute(text("SELECT 1"))
        status = "healthy"
    except Exception:
        status = "degraded"

    total_audit = db.scalar(select(func.count(AuditLog.id))) or 0

    return DatabaseHealthResponse(
        status=status,
        size_mb=0,
        connection_count=1,
        max_connections=100,
        active_queries=0,
        cache_hit_ratio=None,
        slow_queries_last_24h=total_audit,
    )


@router.get("/tables", response_model=DatabaseTablesResponse)
def database_tables(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    tables = []
    for name in table_names:
        row_count = db.scalar(select(func.count()).select_from(text(name))) or 0
        tables.append(
            DatabaseTableInfo(
                table_name=name,
                row_count=row_count,
                size_mb=0,
                index_count=len(inspector.get_indexes(name)),
                last_vacuum=None,
            )
        )

    tables.sort(key=lambda t: t.row_count, reverse=True)
    return DatabaseTablesResponse(tables=tables)

