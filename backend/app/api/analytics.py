"""Analytics API endpoints."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.analytics import StudentDailyAnalytics, StudentWeeklyAnalytics
from app.models.user import User
from app.schemas.analytics import (
    AggregationResult,
    BehaviorProfile,
    DailyAnalyticsResponse,
    DailyValidationResult,
    PaginatedDailyAnalytics,
    PaginatedWeeklyAnalytics,
    StudentQualityReport,
    SystemQualityReport,
    WeeklyAnalyticsResponse,
    WeeklyValidationResult,
)
from app.services.analytics import (
    AggregationService,
    BehaviorFeatureService,
    DataQualityService,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


# ========================= BEHAVIOR PROFILE ENDPOINTS =========================

@router.get("/profile", response_model=BehaviorProfile)
async def get_behavior_profile(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> BehaviorProfile:
    """Get complete behavior profile for current user."""
    if current_user.role.value != "STUDENT":
        raise HTTPException(status_code=403, detail="Only students have behavior profiles")

    feature_service = BehaviorFeatureService(db)
    profile = feature_service.build_behavior_profile(current_user.id, date_range_days=days)

    return BehaviorProfile(
        student_id=current_user.id,
        date_range_days=days,
        evidence_status=profile["evidence_status"],
        activity=profile["activity"],
        success=profile["success"],
        debugging=profile["debugging"],
        difficulty=profile["difficulty"],
        topics=profile["topics"],
        consistency=profile["consistency"],
        progression=profile["progression"],
        generated_at=datetime.now(timezone.utc),
    )


# ========================= DAILY ANALYTICS ENDPOINTS =========================

@router.get("/daily", response_model=PaginatedDailyAnalytics)
async def get_daily_analytics(
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginatedDailyAnalytics:
    """Get daily analytics for current user."""
    if current_user.role.value != "STUDENT":
        raise HTTPException(status_code=403, detail="Only students have analytics")

    query = db.query(StudentDailyAnalytics).filter(
        StudentDailyAnalytics.student_id == current_user.id
    )

    if start_date:
        query = query.filter(StudentDailyAnalytics.analytics_date >= start_date)
    if end_date:
        query = query.filter(StudentDailyAnalytics.analytics_date <= end_date)

    total = query.count()

    records = (
        query.order_by(StudentDailyAnalytics.analytics_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedDailyAnalytics(
        total=total,
        page=page,
        page_size=page_size,
        data=[DailyAnalyticsResponse.from_orm(r) for r in records],
    )


@router.get("/daily/{analytics_date}", response_model=DailyAnalyticsResponse)
async def get_daily_analytics_for_date(
    analytics_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DailyAnalyticsResponse:
    """Get daily analytics for a specific date."""
    if current_user.role.value != "STUDENT":
        raise HTTPException(status_code=403, detail="Only students have analytics")

    record = (
        db.query(StudentDailyAnalytics)
        .filter(
            StudentDailyAnalytics.student_id == current_user.id,
            StudentDailyAnalytics.analytics_date == analytics_date,
        )
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="No analytics data for this date")

    return DailyAnalyticsResponse.from_orm(record)


# ========================= WEEKLY ANALYTICS ENDPOINTS =========================

@router.get("/weekly", response_model=PaginatedWeeklyAnalytics)
async def get_weekly_analytics(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=52),
    start_week: date | None = Query(None),
    end_week: date | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PaginatedWeeklyAnalytics:
    """Get weekly analytics for current user."""
    if current_user.role.value != "STUDENT":
        raise HTTPException(status_code=403, detail="Only students have analytics")

    query = db.query(StudentWeeklyAnalytics).filter(
        StudentWeeklyAnalytics.student_id == current_user.id
    )

    if start_week:
        query = query.filter(StudentWeeklyAnalytics.week_start >= start_week)
    if end_week:
        query = query.filter(StudentWeeklyAnalytics.week_start <= end_week)

    total = query.count()

    records = (
        query.order_by(StudentWeeklyAnalytics.week_start.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedWeeklyAnalytics(
        total=total,
        page=page,
        page_size=page_size,
        data=[WeeklyAnalyticsResponse.from_orm(r) for r in records],
    )


@router.get("/weekly/{week_start}", response_model=WeeklyAnalyticsResponse)
async def get_weekly_analytics_for_week(
    week_start: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WeeklyAnalyticsResponse:
    """Get weekly analytics for a specific week."""
    if current_user.role.value != "STUDENT":
        raise HTTPException(status_code=403, detail="Only students have analytics")

    record = (
        db.query(StudentWeeklyAnalytics)
        .filter(
            StudentWeeklyAnalytics.student_id == current_user.id,
            StudentWeeklyAnalytics.week_start == week_start,
        )
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="No analytics data for this week")

    return WeeklyAnalyticsResponse.from_orm(record)


# ========================= VALIDATION ENDPOINTS =========================

@router.get("/validate/daily/{analytics_date}", response_model=DailyValidationResult)
async def validate_daily_analytics(
    analytics_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DailyValidationResult:
    """Validate daily analytics for a specific date."""
    if current_user.role.value != "STUDENT":
        raise HTTPException(status_code=403, detail="Only students have analytics")

    record = (
        db.query(StudentDailyAnalytics)
        .filter(
            StudentDailyAnalytics.student_id == current_user.id,
            StudentDailyAnalytics.analytics_date == analytics_date,
        )
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="No analytics data for this date")

    quality_service = DataQualityService(db)
    result = quality_service.validate_daily_analytics(record)

    return DailyValidationResult(**result)


@router.get("/validate/weekly/{week_start}", response_model=WeeklyValidationResult)
async def validate_weekly_analytics(
    week_start: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WeeklyValidationResult:
    """Validate weekly analytics for a specific week."""
    if current_user.role.value != "STUDENT":
        raise HTTPException(status_code=403, detail="Only students have analytics")

    record = (
        db.query(StudentWeeklyAnalytics)
        .filter(
            StudentWeeklyAnalytics.student_id == current_user.id,
            StudentWeeklyAnalytics.week_start == week_start,
        )
        .first()
    )

    if not record:
        raise HTTPException(status_code=404, detail="No analytics data for this week")

    quality_service = DataQualityService(db)
    result = quality_service.validate_weekly_analytics(record)

    return WeeklyValidationResult(**result)


@router.get("/quality-report", response_model=StudentQualityReport)
async def get_student_quality_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StudentQualityReport:
    """Get data quality report for current user."""
    if current_user.role.value != "STUDENT":
        raise HTTPException(status_code=403, detail="Only students have analytics")

    quality_service = DataQualityService(db)
    report = quality_service.validate_all_student_analytics(current_user.id)

    return StudentQualityReport(
        student_id=current_user.id,
        valid=report["valid"],
        daily_issues=report["daily_issues"],
        daily_warnings=report["daily_warnings"],
        weekly_issues=report["weekly_issues"],
        weekly_warnings=report["weekly_warnings"],
        anomalies=report["anomalies"],
    )


# ========================= AGGREGATION ENDPOINTS (ADMIN ONLY) =========================

@router.post("/aggregate/daily/{student_id}", response_model=DailyAnalyticsResponse)
async def aggregate_daily_for_student(
    student_id: int,
    analytics_date: date | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> DailyAnalyticsResponse:
    """Aggregate daily analytics for a specific student and date (admin only)."""
    if current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admins can trigger aggregation")

    if analytics_date is None:
        analytics_date = date.today()

    aggregation_service = AggregationService(db)
    record = aggregation_service.aggregate_daily_analytics(student_id, analytics_date)

    return DailyAnalyticsResponse.from_orm(record)


@router.post("/aggregate/weekly/{student_id}", response_model=WeeklyAnalyticsResponse)
async def aggregate_weekly_for_student(
    student_id: int,
    week_start: date | None = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WeeklyAnalyticsResponse:
    """Aggregate weekly analytics for a specific student and week (admin only)."""
    if current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admins can trigger aggregation")

    if week_start is None:
        # Get current week start (Monday)
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

    aggregation_service = AggregationService(db)
    record = aggregation_service.aggregate_weekly_analytics(student_id, week_start)

    return WeeklyAnalyticsResponse.from_orm(record)


@router.post("/aggregate/range/{student_id}", response_model=AggregationResult)
async def rebuild_student_analytics_range(
    student_id: int,
    start_date: date,
    end_date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AggregationResult:
    """Rebuild all analytics for a student over a date range (admin only)."""
    if current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admins can trigger aggregation")

    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")

    aggregation_service = AggregationService(db)
    result = aggregation_service.rebuild_student_analytics(student_id, start_date, end_date)

    return AggregationResult(**result)


# ========================= SYSTEM ENDPOINTS (ADMIN ONLY) =========================

@router.get("/quality-report/system", response_model=SystemQualityReport)
async def get_system_quality_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SystemQualityReport:
    """Get system-wide data quality report (admin only)."""
    if current_user.role.value != "ADMIN":
        raise HTTPException(status_code=403, detail="Only admins can view system reports")

    quality_service = DataQualityService(db)
    report = quality_service.generate_quality_report()

    return SystemQualityReport(**report)
