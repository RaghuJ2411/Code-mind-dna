from __future__ import annotations

from datetime import datetime, date, timezone
from enum import Enum as PyEnum

from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base


class GoalType(str, PyEnum):
    SOLVE_PROBLEMS = "SOLVE_PROBLEMS"
    ACTIVE_DAYS = "ACTIVE_DAYS"
    PRACTICE_TOPIC = "PRACTICE_TOPIC"
    COMPLETE_MENTOR_TASKS = "COMPLETE_MENTOR_TASKS"


class GoalStatus(str, PyEnum):
    ACTIVE = "ACTIVE"
    ACHIEVED = "ACHIEVED"
    CANCELLED = "CANCELLED"


class StudentGoal(Base):
    __tablename__ = "student_goals"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    goal_type: Mapped[str] = Column(String(50), nullable=False)
    target_value: Mapped[int] = Column(Integer, nullable=False)
    current_value: Mapped[int] = Column(Integer, nullable=False, default=0)
    period_start: Mapped[date] = Column(Date, nullable=False)
    period_end: Mapped[date] = Column(Date, nullable=False)
    status: Mapped[str] = Column(String(20), nullable=False, default=GoalStatus.ACTIVE.value)
    title: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)

    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student = relationship("User")
