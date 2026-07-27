from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.analytics import StudentDailyAnalytics, StudentWeeklyAnalytics
from app.models.execution import Submission, SubmissionVerdict
from app.models.mentor_alert import MentorRiskAlert
from app.models.user import User, UserRole
from app.schemas.mentor import MentorReportResponse

router = APIRouter(prefix="/mentor/reports", tags=["mentor-reports"])


@router.get("/student-progress", response_model=MentorReportResponse)
def generate_student_progress_report(
    student_id: int | None = Query(None),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    students = db.query(User).filter(User.role == UserRole.STUDENT)
    if student_id:
        students = students.filter(User.id == student_id)

    student_list = students.all()
    report_data: list[dict[str, Any]] = []

    for student in student_list:
        submissions = db.query(Submission).filter(
            Submission.student_id == student.id,
            Submission.created_at >= datetime.now(timezone.utc) - timedelta(days=days),
        ).all()

        accepted = sum(1 for s in submissions if s.verdict == SubmissionVerdict.ACCEPTED)
        unique_problems = len(set(s.problem_id for s in submissions if s.problem_id))

        report_data.append({
            "student_id": student.id,
            "student_name": student.full_name,
            "email": student.email,
            "total_submissions": len(submissions),
            "accepted": accepted,
            "solve_rate": round((accepted / max(len(submissions), 1)) * 100, 2),
            "unique_problems_attempted": unique_problems,
        })

    return MentorReportResponse(
        id=f"progress-{datetime.now(timezone.utc).timestamp()}",
        title="Student Progress Report",
        report_type="STUDENT_PROGRESS",
        generated_at=datetime.now(timezone.utc),
        data={
            "period_days": days,
            "generated_by": current_user.full_name,
            "total_students": len(report_data),
            "students": report_data,
        },
    )


@router.get("/alerts-summary", response_model=MentorReportResponse)
def generate_alerts_summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    alerts = db.query(MentorRiskAlert).filter(
        MentorRiskAlert.mentor_id == current_user.id,
        MentorRiskAlert.created_at >= since,
    ).all()

    by_severity: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for alert in alerts:
        by_severity[alert.severity] = by_severity.get(alert.severity, 0) + 1
        by_status[alert.status] = by_status.get(alert.status, 0) + 1

    return MentorReportResponse(
        id=f"alerts-{datetime.now(timezone.utc).timestamp()}",
        title="Alerts Summary Report",
        report_type="ALERTS_SUMMARY",
        generated_at=datetime.now(timezone.utc),
        data={
            "period_days": days,
            "total_alerts": len(alerts),
            "by_severity": by_severity,
            "by_status": by_status,
            "generated_by": current_user.full_name,
        },
    )


@router.get("/engagement", response_model=MentorReportResponse)
def generate_engagement_report(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    students = db.query(User).filter(User.role == UserRole.STUDENT).all()

    engagement_data: list[dict[str, Any]] = []
    for student in students:
        activity_days = db.query(StudentDailyAnalytics).filter(
            StudentDailyAnalytics.student_id == student.id,
            StudentDailyAnalytics.analytics_date >= since.date(),
            StudentDailyAnalytics.submissions_count > 0,
        ).count()

        total_submissions = db.query(Submission).filter(
            Submission.student_id == student.id,
            Submission.created_at >= since,
        ).count()

        engagement_data.append({
            "student_id": student.id,
            "student_name": student.full_name,
            "active_days": activity_days,
            "total_submissions": total_submissions,
            "engagement_level": "HIGH" if activity_days >= days * 0.5 else "MODERATE" if activity_days >= days * 0.2 else "LOW",
        })

    return MentorReportResponse(
        id=f"engagement-{datetime.now(timezone.utc).timestamp()}",
        title="Student Engagement Report",
        report_type="ENGAGEMENT",
        generated_at=datetime.now(timezone.utc),
        data={
            "period_days": days,
            "total_students": len(engagement_data),
            "students": engagement_data,
            "generated_by": current_user.full_name,
        },
    )

