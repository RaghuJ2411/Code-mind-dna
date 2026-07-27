from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum

from pydantic import BaseModel


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


class MentorRiskAlertResponse(BaseModel):
    id: int
    mentor_id: int
    student_id: int | None
    alert_type: MentorAlertType
    severity: AlertSeverity
    message: str
    status: MentorAlertStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MentorRiskAlertCreate(BaseModel):
    student_id: int | None = None
    alert_type: MentorAlertType
    severity: AlertSeverity
    message: str


class MentorRiskAlertListResponse(BaseModel):
    items: list[MentorRiskAlertResponse]
