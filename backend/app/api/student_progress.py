from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.analytics import StudentDailyAnalytics, StudentWeeklyAnalytics
from app.models.execution import Submission, SubmissionVerdict
from app.models.problem import Problem
from app.models.student_goal import StudentGoal
from app.models.user import User, UserRole

router = APIRouter(prefix="/student/progress", tags=["student-progress"])


@router.get("/daily")
def get_daily_progress(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    start_date = date.today() - timedelta(days=days)
    records = (
        db.query(StudentDailyAnalytics)
        .filter(
            StudentDailyAnalytics.student_id == current_user.id,
            StudentDailyAnalytics.analytics_date >= start_date,
        )
        .order_by(StudentDailyAnalytics.analytics_date.asc())
        .all()
    )

    return {
        "data": [
            {
                "date": r.analytics_date,
                "problems_attempted": r.problems_attempted,
                "problems_solved": r.problems_solved,
                "submissions_count": r.submissions_count,
                "runs_count": r.runs_count,
                "active_minutes": r.active_minutes,
            }
            for r in records
        ],
        "total_days": len(records),
    }


@router.get("/weekly")
def get_weekly_progress(
    weeks: int = Query(12, ge=1, le=52),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    start_date = date.today() - timedelta(weeks=weeks)
    records = (
        db.query(StudentWeeklyAnalytics)
        .filter(
            StudentWeeklyAnalytics.student_id == current_user.id,
            StudentWeeklyAnalytics.week_start >= start_date,
        )
        .order_by(StudentWeeklyAnalytics.week_start.asc())
        .all()
    )

    return {
        "data": [
            {
                "week_start": r.week_start,
                "week_end": r.week_end,
                "problems_attempted": r.problems_attempted,
                "problems_solved": r.problems_solved,
                "solve_rate": r.solve_rate,
                "active_days": r.active_days,
                "submissions_count": r.submissions_count,
            }
            for r in records
        ],
        "total_weeks": len(records),
    }


@router.get("/monthly")
def get_monthly_progress(
    months: int = Query(12, ge=1, le=24),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=months * 30)

    submissions = (
        db.query(
            func.strftime("%Y-%m", Submission.created_at).label("month"),
            func.count(Submission.id).label("total_submissions"),
            func.sum(
                func.cast(Submission.verdict == SubmissionVerdict.ACCEPTED.value, __import__("sqlalchemy").Integer)
            ).label("accepted"),
        )
        .filter(
            Submission.student_id == current_user.id,
            Submission.created_at >= start_date,
        )
        .group_by("month")
        .order_by("month")
        .all()
    )

    return {
        "data": [
            {
                "month": row.month,
                "total_submissions": row.total_submissions,
                "accepted": row.accepted or 0,
                "solve_rate": round((row.accepted or 0) / max(row.total_submissions, 1) * 100, 2),
            }
            for row in submissions
        ],
        "total_months": len(submissions),
    }


@router.get("/heatmap")
def get_coding_heatmap(
    year: int | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    target_year = year or date.today().year
    start_date = date(target_year, 1, 1)
    end_date = date(target_year, 12, 31)

    records = (
        db.query(
            StudentDailyAnalytics.analytics_date,
            StudentDailyAnalytics.active_minutes,
            StudentDailyAnalytics.problems_solved,
            StudentDailyAnalytics.submissions_count,
        )
        .filter(
            StudentDailyAnalytics.student_id == current_user.id,
            StudentDailyAnalytics.analytics_date >= start_date,
            StudentDailyAnalytics.analytics_date <= end_date,
        )
        .all()
    )

    heatmap_data = {}
    for r in records:
        date_str = str(r.analytics_date)
        heatmap_data[date_str] = {
            "active_minutes": r.active_minutes,
            "problems_solved": r.problems_solved,
            "submissions_count": r.submissions_count,
        }

    return {
        "year": target_year,
        "total_active_days": len(records),
        "data": heatmap_data,
    }


@router.get("/skill-growth")
def get_skill_growth(
    days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)

    # Get weekly snapshots of skill metrics
    weekly_data = (
        db.query(
            StudentWeeklyAnalytics.week_start,
            StudentWeeklyAnalytics.solve_rate,
            StudentWeeklyAnalytics.easy_solve_rate,
            StudentWeeklyAnalytics.medium_solve_rate,
            StudentWeeklyAnalytics.hard_solve_rate,
            StudentWeeklyAnalytics.difficulty_progression_delta,
        )
        .filter(
            StudentWeeklyAnalytics.student_id == current_user.id,
            StudentWeeklyAnalytics.week_start >= start_date,
        )
        .order_by(StudentWeeklyAnalytics.week_start.asc())
        .all()
    )

    return {
        "data": [
            {
                "week_start": str(r.week_start),
                "solve_rate": r.solve_rate,
                "easy_solve_rate": r.easy_solve_rate,
                "medium_solve_rate": r.medium_solve_rate,
                "hard_solve_rate": r.hard_solve_rate,
                "difficulty_progression": r.difficulty_progression_delta,
            }
            for r in weekly_data
        ],
        "total_weeks": len(weekly_data),
    }


@router.get("/goals")
def get_goal_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    goals = (
        db.query(StudentGoal)
        .filter(StudentGoal.student_id == current_user.id)
        .order_by(StudentGoal.created_at.desc())
        .all()
    )

    return {
        "data": [
            {
                "id": g.id,
                "title": g.title,
                "goal_type": g.goal_type,
                "target_value": g.target_value,
                "current_value": g.current_value,
                "progress_pct": round((g.current_value / max(g.target_value, 1)) * 100, 2),
                "status": g.status,
                "period_start": str(g.period_start) if g.period_start else None,
                "period_end": str(g.period_end) if g.period_end else None,
            }
            for g in goals
        ],
        "total_goals": len(goals),
    }


@router.get("/overview")
def get_progress_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    now = datetime.now(timezone.utc)
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    # Daily stats
    daily = (
        db.query(StudentDailyAnalytics)
        .filter(
            StudentDailyAnalytics.student_id == current_user.id,
            StudentDailyAnalytics.analytics_date == today,
        )
        .first()
    )

    # Weekly stats
    weekly = (
        db.query(StudentWeeklyAnalytics)
        .filter(
            StudentWeeklyAnalytics.student_id == current_user.id,
            StudentWeeklyAnalytics.week_start == week_start,
        )
        .first()
    )

    # Total stats
    total_solved = (
        db.query(Submission)
        .filter(
            Submission.student_id == current_user.id,
            Submission.verdict == SubmissionVerdict.ACCEPTED,
        )
        .count()
    )
    total_attempted = (
        db.query(Submission)
        .filter(Submission.student_id == current_user.id)
        .count()
    )

    # Streak calculation
    streak = 0
    check_date = today
    while True:
        day_data = (
            db.query(StudentDailyAnalytics)
            .filter(
                StudentDailyAnalytics.student_id == current_user.id,
                StudentDailyAnalytics.analytics_date == check_date,
            )
            .first()
        )
        if day_data and day_data.submissions_count > 0:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    return {
        "daily": {
            "date": str(today),
            "problems_attempted": daily.problems_attempted if daily else 0,
            "problems_solved": daily.problems_solved if daily else 0,
            "active_minutes": daily.active_minutes if daily else 0,
        },
        "weekly": {
            "week_start": str(week_start),
            "problems_attempted": weekly.problems_attempted if weekly else 0,
            "problems_solved": weekly.problems_solved if weekly else 0,
            "solve_rate": weekly.solve_rate if weekly else 0.0,
            "active_days": weekly.active_days if weekly else 0,
        },
        "total": {
            "problems_solved": total_solved,
            "problems_attempted": total_attempted,
            "solve_rate": round(total_solved / max(total_attempted, 1) * 100, 2),
        },
        "current_streak": streak,
    }

