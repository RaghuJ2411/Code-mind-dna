from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import JSON, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base


class RecommendationStatus(str, PyEnum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DISMISSED = "DISMISSED"
    EXPIRED = "EXPIRED"


class RecommendationPriority(str, PyEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class StudentRecommendation(Base):
    __tablename__ = "student_recommendations"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    recommendation_type: Mapped[str] = Column(String(100), nullable=False)
    priority: Mapped[str] = Column(String(20), nullable=False)
    title: Mapped[str] = Column(String(255), nullable=False)
    reason: Mapped[str] = Column(Text, nullable=False)
    action_json: Mapped[dict] = Column(JSON, nullable=False, default=dict)
    source_snapshot_json: Mapped[dict] = Column(JSON, nullable=False, default=dict)

    status: Mapped[str] = Column(String(20), nullable=False, default=RecommendationStatus.PENDING.value)
    generated_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    started_at: Mapped[datetime | None] = Column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = Column(DateTime(timezone=True), nullable=True)
    dismissed_at: Mapped[datetime | None] = Column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student = relationship("User")
