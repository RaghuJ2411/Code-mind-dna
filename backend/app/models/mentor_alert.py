from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base


class MentorAlertType(str, PyEnum):
    ENGAGEMENT_DROP = "ENGAGEMENT_DROP"
    LOW_SUCCESS_RATE = "LOW_SUCCESS_RATE"
    INCONSISTENT_PRACTICE = "INCONSISTENT_PRACTICE"
    ATTENDANCE_ISSUE = "ATTENDANCE_ISSUE"


class AlertSeverity(str, PyEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class MentorAlertStatus(str, PyEnum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class MentorRiskAlert(Base):
    __tablename__ = "mentor_risk_alerts"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    mentor_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    student_id: Mapped[int | None] = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    alert_type: Mapped[str] = Column(String(100), nullable=False)
    severity: Mapped[str] = Column(String(20), nullable=False)
    message: Mapped[str] = Column(Text, nullable=False)
    status: Mapped[str] = Column(String(20), nullable=False, default=MentorAlertStatus.OPEN.value)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    mentor = relationship("User", foreign_keys=[mentor_id])
    student = relationship("User", foreign_keys=[student_id])
