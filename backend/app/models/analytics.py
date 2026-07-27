from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base


class StudentDailyAnalytics(Base):
    __tablename__ = "student_daily_analytics"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    analytics_date: Mapped[date] = Column(Date, nullable=False, index=True)

    problems_attempted: Mapped[int] = Column(Integer, nullable=False, default=0)
    problems_solved: Mapped[int] = Column(Integer, nullable=False, default=0)
    submissions_count: Mapped[int] = Column(Integer, nullable=False, default=0)
    runs_count: Mapped[int] = Column(Integer, nullable=False, default=0)
    active_minutes: Mapped[int] = Column(Integer, nullable=False, default=0)

    wrong_answer_count: Mapped[int] = Column(Integer, nullable=False, default=0)
    compilation_error_count: Mapped[int] = Column(Integer, nullable=False, default=0)
    runtime_error_count: Mapped[int] = Column(Integer, nullable=False, default=0)
    time_limit_count: Mapped[int] = Column(Integer, nullable=False, default=0)

    easy_attempted: Mapped[int] = Column(Integer, nullable=False, default=0)
    easy_solved: Mapped[int] = Column(Integer, nullable=False, default=0)
    medium_attempted: Mapped[int] = Column(Integer, nullable=False, default=0)
    medium_solved: Mapped[int] = Column(Integer, nullable=False, default=0)
    hard_attempted: Mapped[int] = Column(Integer, nullable=False, default=0)
    hard_solved: Mapped[int] = Column(Integer, nullable=False, default=0)

    unique_topics_attempted: Mapped[int] = Column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (UniqueConstraint("student_id", "analytics_date", name="uq_daily_analytics_student_date"),)


class StudentWeeklyAnalytics(Base):
    __tablename__ = "student_weekly_analytics"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    week_start: Mapped[date] = Column(Date, nullable=False, index=True)
    week_end: Mapped[date] = Column(Date, nullable=False)

    problems_attempted: Mapped[int] = Column(Integer, nullable=False, default=0)
    problems_solved: Mapped[int] = Column(Integer, nullable=False, default=0)
    solve_rate: Mapped[float] = Column(Float, nullable=False, default=0.0)

    submissions_count: Mapped[int] = Column(Integer, nullable=False, default=0)
    runs_count: Mapped[int] = Column(Integer, nullable=False, default=0)
    active_minutes: Mapped[int] = Column(Integer, nullable=False, default=0)
    active_days: Mapped[int] = Column(Integer, nullable=False, default=0)

    average_attempts_to_solve: Mapped[float] = Column(Float, nullable=False, default=0.0)
    average_solve_time_minutes: Mapped[float] = Column(Float, nullable=False, default=0.0)
    error_recovery_rate: Mapped[float] = Column(Float, nullable=False, default=0.0)

    easy_solve_rate: Mapped[float] = Column(Float, nullable=False, default=0.0)
    medium_solve_rate: Mapped[float] = Column(Float, nullable=False, default=0.0)
    hard_solve_rate: Mapped[float] = Column(Float, nullable=False, default=0.0)

    unique_topics_attempted: Mapped[int] = Column(Integer, nullable=False, default=0)
    difficulty_progression_delta: Mapped[float] = Column(Float, nullable=False, default=0.0)

    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (UniqueConstraint("student_id", "week_start", name="uq_weekly_analytics_student_week"),)
