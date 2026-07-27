from __future__ import annotations

from datetime import datetime, date, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped

from app.core.database import Base


class CareerRoadmap(Base):
    __tablename__ = "career_roadmaps"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    career_goal: Mapped[str] = Column(String(255), nullable=False)
    company_goal: Mapped[str] = Column(String(255), nullable=True)
    target_role: Mapped[str] = Column(String(255), nullable=True)
    target_seniority: Mapped[str] = Column(String(50), nullable=True)
    timeline_months: Mapped[int] = Column(Integer, nullable=True)
    skills_required: Mapped[list] = Column(JSON, nullable=False, default=list)
    current_skills: Mapped[list] = Column(JSON, nullable=False, default=list)
    gap_analysis: Mapped[dict] = Column(JSON, nullable=True)
    ai_suggestions: Mapped[dict] = Column(JSON, nullable=True)
    is_active: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class RoadmapMilestone(Base):
    __tablename__ = "roadmap_milestones"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    roadmap_id: Mapped[int] = Column(Integer, ForeignKey("career_roadmaps.id"), nullable=False)
    title: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    milestone_type: Mapped[str] = Column(String(50), nullable=False)  # WEEKLY, MONTHLY, SKILL, PROJECT
    target_date: Mapped[date] = Column(Date, nullable=True)
    is_completed: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    completed_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)
    progress_pct: Mapped[float] = Column(Float, nullable=False, default=0.0)
    order_index: Mapped[int] = Column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class WeeklyGoal(Base):
    __tablename__ = "weekly_goals"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    roadmap_id: Mapped[int] = Column(Integer, ForeignKey("career_roadmaps.id"), nullable=True)
    title: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    week_start: Mapped[date] = Column(Date, nullable=False)
    week_end: Mapped[date] = Column(Date, nullable=True)
    is_completed: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    completed_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class MonthlyGoal(Base):
    __tablename__ = "monthly_goals"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    roadmap_id: Mapped[int] = Column(Integer, ForeignKey("career_roadmaps.id"), nullable=True)
    title: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    month: Mapped[str] = Column(String(7), nullable=False)  # YYYY-MM
    is_completed: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    completed_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

