from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped

from app.core.database import Base


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    badge_icon: Mapped[str] = Column(String(500), nullable=True)
    category: Mapped[str] = Column(String(100), nullable=False)  # CODING, LEARNING, CAREER, COMMUNITY
    criteria_type: Mapped[str] = Column(String(100), nullable=False)  # problems_solved, streak_days, etc.
    criteria_value: Mapped[int] = Column(Integer, nullable=False, default=1)
    xp_reward: Mapped[int] = Column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class StudentAchievement(Base):
    __tablename__ = "student_achievements"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    achievement_id: Mapped[int] = Column(Integer, ForeignKey("achievements.id"), nullable=False)
    earned_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_displayed: Mapped[bool] = Column(Boolean, nullable=False, default=True)

    __table_args__ = (UniqueConstraint("student_id", "achievement_id", name="uq_student_achievement"),)


class CodingMilestone(Base):
    __tablename__ = "coding_milestones"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    milestone_type: Mapped[str] = Column(String(100), nullable=False)  # PROBLEMS_SOLVED, STREAK_DAYS, ETC.
    current_value: Mapped[int] = Column(Integer, nullable=False, default=0)
    target_value: Mapped[int] = Column(Integer, nullable=False)
    achieved: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    achieved_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

