from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.analytics import StudentDailyAnalytics, StudentWeeklyAnalytics
from app.models.execution import Submission, SubmissionVerdict
from app.models.mentor_alert import MentorRiskAlert
from app.models.user import User, UserRole
from app.schemas.mentor import MentorAnalyticsResponse

router = APIRouter(prefix="/mentor/analytics", tags=["mentor-analytics"])


@router.get("/overview", response_model=MentorAnalyticsResponse)
def get_analytics_overview(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    students = db.query(User).filter(User.role == UserRole.STUDENT).all()
    total_students = len(students)

    # Active students (submissions in last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    active_student_ids = (
        db.query(Submission.student_id)
        .filter(Submission.created_at >= thirty_days_ago)
        .distinct()
        .all()
    )
    active_students = len(active_student_ids)

    # Average solve rate
    solve_rates = []
    dna_scores = []
    for student in students:
        submissions = db.query(Submission).filter(
            Submission.student_id == student.id
        ).count()
        if submissions > 0:
            accepted = db.query(Submission).filter(
                Submission.student_id == student.id,
                Submission.verdict == SubmissionVerdict.ACCEPTED,
            ).count()
            solve_rates.append(accepted / submissions)

    avg_solve_rate = (sum(solve_rates) / len(solve_rates) * 100) if solve_rates else 0.0

    # Alerts stats
    total_alerts = db.query(MentorRiskAlert).filter(
        MentorRiskAlert.mentor_id == current_user.id
    ).count()
    resolved_alerts = db.query(MentorRiskAlert).filter(
        MentorRiskAlert.mentor_id == current_user.id,
        MentorRiskAlert.status == "RESOLVED",
    ).count()

    # Student breakdown
    student_breakdown = []
    for student in students[:10]:
        student_submissions = db.query(Submission).filter(
            Submission.student_id == student.id
        ).count()
        student_accepted = db.query(Submission).filter(
            Submission.student_id == student.id,
            Submission.verdict == SubmissionVerdict.ACCEPTED,
        ).count()
        solve_rate = (student_accepted / max(student_submissions, 1)) * 100

        student_alerts = db.query(MentorRiskAlert).filter(
            MentorRiskAlert.student_id == student.id,
            MentorRiskAlert.status == "OPEN",
        ).count()

        student_breakdown.append({
            "student_id": student.id,
            "student_name": student.full_name,
            "problems_solved": student_accepted,
            "solve_rate": round(solve_rate, 2),
            "open_alerts": student_alerts,
        })

    # Weekly trends
    today = date.today()
    weekly_trends = []
    for i in range(8):
        week_start = today - timedelta(weeks=i)
        week_end = week_start + timedelta(days=6)
        week_data = db.query(StudentWeeklyAnalytics).filter(
            StudentWeeklyAnalytics.week_start == week_start
        ).all()
        weekly_trends.append({
            "week_start": str(week_start),
            "active_students": len(week_data),
            "total_solved": sum(w.problems_solved for w in week_data),
        })

    return MentorAnalyticsResponse(
        total_students=total_students,
        active_students=active_students,
        avg_solve_rate=round(avg_solve_rate, 2),
        avg_dna_score=0.0,
        sessions_conducted=0,
        assignments_graded=0,
        alerts_generated=total_alerts,
        alerts_resolved=resolved_alerts,
        student_breakdown=student_breakdown,
        weekly_trends=weekly_trends,
    )


@router.get("/student/{student_id}")
def get_student_analytics(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.MENTOR.value)),
):
    student = db.query(User).filter(
        User.id == student_id,
        User.role == UserRole.STUDENT,
    ).first()
    if not student:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Student not found")

    # Problem stats
    total_submissions = db.query(Submission).filter(
        Submission.student_id == student_id
    ).count()
    accepted = db.query(Submission).filter(
        Submission.student_id == student_id,
        Submission.verdict == SubmissionVerdict.ACCEPTED,
    ).count()

    # Daily activity
    thirty_days_ago = date.today() - timedelta(days=30)
    daily_records = db.query(StudentDailyAnalytics).filter(
        StudentDailyAnalytics.student_id == student_id,
        StudentDailyAnalytics.analytics_date >= thirty_days_ago,
    ).order_by(StudentDailyAnalytics.analytics_date.asc()).all()

    # Active alerts
    alerts = db.query(MentorRiskAlert).filter(
        MentorRiskAlert.student_id == student_id,
        MentorRiskAlert.status == "OPEN",
    ).count()

    return {
        "student_id": student.id,
        "student_name": student.full_name,
        "total_submissions": total_submissions,
        "problems_solved": accepted,
        "solve_rate": round((accepted / max(total_submissions, 1)) * 100, 2),
        "active_alerts": alerts,
        "daily_activity": [
            {
                "date": str(r.analytics_date),
                "problems_attempted": r.problems_attempted,
                "problems_solved": r.problems_solved,
                "active_minutes": r.active_minutes,
            }
            for r in daily_records
        ],
    }

