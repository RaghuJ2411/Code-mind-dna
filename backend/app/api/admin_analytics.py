from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.models.analytics import StudentDailyAnalytics, StudentWeeklyAnalytics
from app.models.audit_log import AuditLog
from app.models.execution import Submission
from app.models.problem import Problem
from app.models.user import User, UserRole
from app.schemas.admin import (
    EngagementMetrics,
    PlatformAnalyticsOverview,
    PlatformUsageMetrics,
)

router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])


@router.get("/overview", response_model=PlatformAnalyticsOverview)
def platform_analytics_overview(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    total_users = db.scalar(select(func.count(User.id))) or 0
    total_problems = db.scalar(select(func.count(Problem.id))) or 0
    total_submissions = db.scalar(select(func.count(Submission.id))) or 0

    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)

    active_7d = db.scalar(
        select(func.count(func.distinct(AuditLog.user_email))).where(AuditLog.created_at >= seven_days_ago)
    ) or 0
    active_30d = db.scalar(
        select(func.count(func.distinct(AuditLog.user_email))).where(AuditLog.created_at >= thirty_days_ago)
    ) or 0

    new_users_7d = db.scalar(
        select(func.count(User.id)).where(User.created_at >= seven_days_ago)
    ) or 0
    new_users_30d = db.scalar(
        select(func.count(User.id)).where(User.created_at >= thirty_days_ago)
    ) or 0

    return PlatformAnalyticsOverview(
        total_users=total_users,
        total_problems=total_problems,
        total_submissions=total_submissions,
        total_sessions=0,
        avg_solve_rate=0,
        active_users_last_7d=active_7d,
        active_users_last_30d=active_30d,
        new_users_last_7d=new_users_7d,
        new_users_last_30d=new_users_30d,
    )


@router.get("/engagement", response_model=EngagementMetrics)
def platform_engagement(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)

    daily_logs = (
        db.query(
            func.date(AuditLog.created_at).label("date"),
            func.count(func.distinct(AuditLog.user_email)).label("active_users"),
            func.count(AuditLog.id).label("requests"),
        )
        .where(AuditLog.created_at >= start_date)
        .group_by(func.date(AuditLog.created_at))
        .order_by(func.date(AuditLog.created_at))
        .all()
    )

    daily_active = [
        {"date": str(row.date), "active_users": row.active_users, "requests": row.requests}
        for row in daily_logs
    ]

    return EngagementMetrics(
        daily_active_users=daily_active,
        weekly_active_users=[],
        submissions_per_day=[],
    )


@router.get("/usage", response_model=PlatformUsageMetrics)
def platform_usage(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    role_counts = {
        role.value: db.scalar(select(func.count(User.id)).where(User.role == role)) or 0
        for role in UserRole
    }

    difficulty_counts = (
        db.query(Problem.difficulty, func.count(Problem.id))
        .group_by(Problem.difficulty)
        .all()
    )
    problems_by_difficulty = {str(d): c for d, c in difficulty_counts}

    topic_counts = (
        db.query(Problem.topic, func.count(Problem.id))
        .group_by(Problem.topic)
        .all()
    )
    problems_by_topic = {str(t): c for t, c in topic_counts}

    top_users = (
        db.query(
            AuditLog.user_email,
            func.count(AuditLog.id).label("request_count"),
        )
        .where(AuditLog.user_email.isnot(None))
        .group_by(AuditLog.user_email)
        .order_by(func.count(AuditLog.id).desc())
        .limit(10)
        .all()
    )
    top_active = [
        {"email": row.user_email, "requests": row.request_count}
        for row in top_users
    ]

    return PlatformUsageMetrics(
        users_by_role=role_counts,
        problems_by_difficulty=problems_by_difficulty,
        problems_by_topic=problems_by_topic,
        top_active_users=top_active,
    )

