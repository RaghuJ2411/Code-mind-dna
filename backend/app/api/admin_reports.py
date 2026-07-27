from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.models.execution import Submission
from app.models.problem import Problem
from app.models.user import User, UserRole
from app.schemas.admin import (
    AdminReportGenerateRequest,
    AdminReportItem,
    AdminReportListResponse,
)

router = APIRouter(prefix="/admin/reports", tags=["admin-reports"])


_reports_store: list[dict] = []
_report_counter = 0


@router.get("", response_model=AdminReportListResponse)
def list_admin_reports(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    items = []
    for r in _reports_store:
        items.append(AdminReportItem(**r))
    return AdminReportListResponse(items=items, total=len(items))


@router.post("/generate")
def generate_admin_report(
    payload: AdminReportGenerateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    global _report_counter
    _report_counter += 1

    now = datetime.now(timezone.utc)
    title = payload.title or f"{payload.report_type.replace('_', ' ').title()} Report #{_report_counter}"

    content = {}

    if payload.report_type == "user_summary":
        total_users = db.scalar(select(func.count(User.id))) or 0
        active_users = db.scalar(select(func.count(User.id)).where(User.is_active.is_(True))) or 0
        role_counts = {
            role.value: db.scalar(select(func.count(User.id)).where(User.role == role)) or 0
            for role in UserRole
        }
        content = {
            "total_users": total_users,
            "active_users": active_users,
            "role_counts": role_counts,
        }
    elif payload.report_type == "problem_stats":
        total = db.scalar(select(func.count(Problem.id))) or 0
        active = db.scalar(select(func.count(Problem.id)).where(Problem.is_active.is_(True))) or 0
        content = {
            "total_problems": total,
            "active_problems": active,
        }
    elif payload.report_type == "platform_overview":
        total_users = db.scalar(select(func.count(User.id))) or 0
        total_problems = db.scalar(select(func.count(Problem.id))) or 0
        total_submissions = db.scalar(select(func.count(Submission.id))) or 0
        total_audit = db.scalar(select(func.count(AuditLog.id))) or 0
        content = {
            "total_users": total_users,
            "total_problems": total_problems,
            "total_submissions": total_submissions,
            "total_audit_events": total_audit,
        }
    elif payload.report_type == "ai_usage":
        from app.models.ai_request_log import AIRequestLog
        total = db.scalar(select(func.count(AIRequestLog.id))) or 0
        success = db.scalar(
            select(func.count(AIRequestLog.id)).where(AIRequestLog.status == "success")
        ) or 0
        content = {
            "total_ai_requests": total,
            "successful_requests": success,
            "failed_requests": total - success,
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown report type: {payload.report_type}",
        )

    report_entry = {
        "id": _report_counter,
        "report_type": payload.report_type,
        "title": title,
        "status": "completed",
        "created_at": now,
        "content_json": content,
    }
    _reports_store.append(report_entry)

    return AdminReportItem(**report_entry)


@router.get("/{report_id}", response_model=AdminReportItem)
def get_admin_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    for r in _reports_store:
        if r["id"] == report_id:
            return AdminReportItem(**r)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

