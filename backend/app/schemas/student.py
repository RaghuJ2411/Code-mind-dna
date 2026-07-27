from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProfileSummary(BaseModel):
    full_name: str
    profile_status: str


class DimensionSummary(BaseModel):
    name: str
    score: float | None


class CodingDNASummary(BaseModel):
    overall_score: float | None
    overall_confidence: float | None
    confidence_label: str | None
    calculated_at: datetime | None
    strongest_dimension: DimensionSummary | None
    development_dimension: DimensionSummary | None


class ActivitySummary(BaseModel):
    problems_attempted: int
    problems_solved: int
    solve_rate: float
    active_days_last_7: int
    active_days_last_30: int
    current_streak: int


class RecentProgressSummary(BaseModel):
    overall_dna_delta: float
    solve_rate_delta: float
    attempt_efficiency_delta: float
    difficulty_progression_delta: float


from app.schemas.ai_usage import AIUsageSummary


class PracticeSummary(BaseModel):
    pending_recommendations: int
    pending_mentor_tasks: int
    active_goals: int


class StudentDashboardOverviewResponse(BaseModel):
    profile: ProfileSummary
    evidence_status: str
    coding_dna: CodingDNASummary
    activity: ActivitySummary
    recent_progress: RecentProgressSummary
    practice: PracticeSummary
    ai_usage: AIUsageSummary


class PracticeQueueItem(BaseModel):
    source: str
    title: str
    reason: str
    recommendation_id: int | None = None
    problem_id: int | None = None
    problem_slug: str | None = None
    difficulty: str | None = None
    topic: str | None = None


class PracticeQueueResponse(BaseModel):
    items: list[PracticeQueueItem] = Field(default_factory=list)


class RecentActivityItem(BaseModel):
    event_type: str
    title: str
    description: str
    occurred_at: datetime
    metadata: dict[str, object] = Field(default_factory=dict)


class RecentActivityResponse(BaseModel):
    items: list[RecentActivityItem] = Field(default_factory=list)


class StudentJobResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    seniority_level: str
    description: str
    requirements: list[str] = Field(default_factory=list)
    is_active: bool
    created_at: datetime


class StudentJobApplicationResponse(BaseModel):
    id: int
    job_id: int
    status: str
    applied_at: datetime
