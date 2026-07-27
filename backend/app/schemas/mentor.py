from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class MentorSessionBase(BaseModel):
    title: str
    description: str | None = None
    session_type: str = "ONE_ON_ONE"  # ONE_ON_ONE, GROUP, WORKSHOP
    student_ids: list[int] = Field(default_factory=list)
    scheduled_at: datetime
    duration_minutes: int = 60
    meeting_link: str | None = None
    status: str = "SCHEDULED"  # SCHEDULED, COMPLETED, CANCELLED
    notes: str | None = None


class MentorSessionCreate(MentorSessionBase):
    pass


class MentorSessionUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    session_type: str | None = None
    student_ids: list[int] | None = None
    scheduled_at: datetime | None = None
    duration_minutes: int | None = None
    meeting_link: str | None = None
    status: str | None = None
    notes: str | None = None


class MentorSessionResponse(MentorSessionBase):
    id: int
    mentor_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MentorAssignmentBase(BaseModel):
    title: str
    description: str | None = None
    assignment_type: str = "CODING"  # CODING, READING, PROJECT, QUIZ
    student_ids: list[int] = Field(default_factory=list)
    due_date: date | None = None
    content_json: dict = Field(default_factory=dict)
    max_score: int = 100
    passing_score: int = 60


class MentorAssignmentCreate(MentorAssignmentBase):
    pass


class MentorAssignmentUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignment_type: str | None = None
    student_ids: list[int] | None = None
    due_date: date | None = None
    content_json: dict | None = None
    max_score: int | None = None
    passing_score: int | None = None
    is_active: bool | None = None


class MentorAssignmentResponse(MentorAssignmentBase):
    id: int
    mentor_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MentorResourceBase(BaseModel):
    title: str
    description: str | None = None
    resource_type: str = "ARTICLE"  # ARTICLE, VIDEO, COURSE, BOOK, TOOL
    url: str | None = None
    content: str | None = None
    tags: list[str] = Field(default_factory=list)
    difficulty: str = "INTERMEDIATE"  # BEGINNER, INTERMEDIATE, ADVANCED
    category: str = "GENERAL"


class MentorResourceCreate(MentorResourceBase):
    pass


class MentorResourceUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    resource_type: str | None = None
    url: str | None = None
    content: str | None = None
    tags: list[str] | None = None
    difficulty: str | None = None
    category: str | None = None
    is_active: bool | None = None


class MentorResourceResponse(MentorResourceBase):
    id: int
    mentor_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MentorNotificationBase(BaseModel):
    title: str
    message: str
    notification_type: str = "SYSTEM"  # SYSTEM, STUDENT_ALERT, SESSION_REMINDER, ASSIGNMENT
    student_id: int | None = None
    priority: str = "NORMAL"  # LOW, NORMAL, HIGH, URGENT


class MentorNotificationCreate(MentorNotificationBase):
    pass


class MentorNotificationResponse(MentorNotificationBase):
    id: int
    mentor_id: int
    is_read: bool
    read_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class MentorProfileBase(BaseModel):
    title: str | None = None
    department: str | None = None
    specialization: str | None = None
    bio: str | None = None
    phone: str | None = None
    photo_url: str | None = None
    experience_years: int | None = None


class MentorProfileCreate(MentorProfileBase):
    pass


class MentorProfileUpdate(BaseModel):
    title: str | None = None
    department: str | None = None
    specialization: str | None = None
    bio: str | None = None
    phone: str | None = None
    photo_url: str | None = None
    experience_years: int | None = None


class MentorProfileResponse(MentorProfileBase):
    id: int
    mentor_id: int
    full_name: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MentorDashboardDetailResponse(BaseModel):
    total_students: int
    active_sessions_today: int
    pending_assignments: int
    open_alerts: int
    unread_messages: int
    upcoming_sessions: list[dict[str, Any]] = Field(default_factory=list)
    recent_activity: list[dict[str, Any]] = Field(default_factory=list)


class MentorStudentDetailResponse(BaseModel):
    id: int
    full_name: str
    email: str
    profile: dict[str, Any] = Field(default_factory=dict)
    recent_sessions: list[dict[str, Any]] = Field(default_factory=list)
    pending_assignments: list[dict[str, Any]] = Field(default_factory=list)
    active_alerts: list[dict[str, Any]] = Field(default_factory=list)
    progress_summary: dict[str, Any] = Field(default_factory=dict)
    career_roadmap: dict[str, Any] | None = None


class MentorIntelligenceResponse(BaseModel):
    student_id: int
    student_name: str
    coding_dna_score: float | None = None
    solve_rate: float | None = None
    skill_gaps: list[str] = Field(default_factory=list)
    weak_topics: list[str] = Field(default_factory=list)
    strong_topics: list[str] = Field(default_factory=list)
    engagement_level: str = "MODERATE"
    risk_score: float | None = None
    recommended_actions: list[str] = Field(default_factory=list)
    last_active: datetime | None = None


class MentorAnalyticsResponse(BaseModel):
    total_students: int
    active_students: int
    avg_solve_rate: float = 0.0
    avg_dna_score: float = 0.0
    sessions_conducted: int
    assignments_graded: int
    alerts_generated: int
    alerts_resolved: int
    student_breakdown: list[dict[str, Any]] = Field(default_factory=list)
    weekly_trends: list[dict[str, Any]] = Field(default_factory=list)


class MentorReportResponse(BaseModel):
    id: str
    title: str
    report_type: str
    generated_at: datetime
    data: dict[str, Any] = Field(default_factory=dict)

