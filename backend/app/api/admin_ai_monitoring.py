from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.core.config import settings
from app.models.ai_request_log import AIRequestLog
from app.models.user import UserRole
from app.schemas.admin import (
    AIRequestDetail,
    AIRequestListResponse,
    AIUsageOverview,
    AILimitsUpdate,
)

router = APIRouter(prefix="/admin/ai", tags=["admin-ai-monitoring"])


@router.get("/usage", response_model=AIUsageOverview)
def ai_usage_overview(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    total = db.scalar(select(func.count(AIRequestLog.id))) or 0
    success = db.scalar(
        select(func.count(AIRequestLog.id)).where(AIRequestLog.status == "success")
    ) or 0
    failed = db.scalar(
        select(func.count(AIRequestLog.id)).where(AIRequestLog.status == "failed")
    ) or 0

    input_tokens = db.scalar(select(func.sum(AIRequestLog.input_token_count))) or 0
    output_tokens = db.scalar(select(func.sum(AIRequestLog.output_token_count))) or 0
    avg_latency = db.scalar(select(func.avg(AIRequestLog.latency_ms))) or 0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())

    today_count = db.scalar(
        select(func.count(AIRequestLog.id)).where(AIRequestLog.created_at >= today_start)
    ) or 0
    week_count = db.scalar(
        select(func.count(AIRequestLog.id)).where(AIRequestLog.created_at >= week_start)
    ) or 0

    return AIUsageOverview(
        total_requests=total,
        success_count=success,
        failed_count=failed,
        total_tokens_input=input_tokens,
        total_tokens_output=output_tokens,
        avg_latency_ms=float(avg_latency),
        requests_today=today_count,
        requests_this_week=week_count,
    )


@router.get("/requests", response_model=AIRequestListResponse)
def ai_request_list(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    task_type: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    page = max(page, 1)
    page_size = max(min(page_size, 100), 1)
    query = db.query(AIRequestLog)

    if task_type:
        query = query.filter(AIRequestLog.task_type == task_type)
    if status:
        query = query.filter(AIRequestLog.status == status)

    total = query.count()
    items = query.order_by(AIRequestLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return AIRequestListResponse(
        items=[AIRequestDetail.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=max((total + page_size - 1) // page_size, 1),
    )


@router.get("/limits")
def ai_current_limits(
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    return {
        "code_review": settings.ai_daily_limits_code_review,
        "error_explanation": settings.ai_daily_limits_error_explain,
        "skill_gap": settings.ai_daily_limits_skill_gap,
        "roadmap": settings.ai_daily_limits_roadmap,
    }


@router.put("/limits")
def ai_update_limits(
    payload: AILimitsUpdate,
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    # Update would persist to DB in production; for now return updated values
    return {
        "code_review": payload.code_review or settings.ai_daily_limits_code_review,
        "error_explanation": payload.error_explanation or settings.ai_daily_limits_error_explain,
        "skill_gap": payload.skill_gap or settings.ai_daily_limits_skill_gap,
        "roadmap": payload.roadmap or settings.ai_daily_limits_roadmap,
    }

