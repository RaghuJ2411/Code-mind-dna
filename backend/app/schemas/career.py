from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class CareerRoleSummary(BaseModel):
    id: int
    name: str
    seniority_level: str
    description: str
    match_score: float


class CareerRoleResponse(BaseModel):
    id: int
    name: str
    seniority_level: str
    description: str


class CareerRoleDetailResponse(BaseModel):
    id: int
    name: str
    seniority_level: str
    description: str
    required_skills: list[str] = Field(default_factory=list)
    target_score_min: int
    target_score_max: int


class CareerOverviewResponse(BaseModel):
    readiness_score: float
    readiness_label: str
    confidence_label: str
    resume_strength: float
    project_alignment: float
    interview_readiness: float
    top_roles: list[CareerRoleSummary] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    resume_entry_count: int
    project_count: int
    interview_session_count: int


class ResumeEntryRequest(BaseModel):
    section: str
    title: str
    content: str
    skills: list[str] = Field(default_factory=list)


class ResumeEntryResponse(BaseModel):
    id: int
    section: str
    title: str
    content: str
    skills: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class ProjectEntryRequest(BaseModel):
    title: str
    description: str
    technologies: list[str] = Field(default_factory=list)
    outcome: str | None = None
    project_url: str | None = None


class ProjectEntryResponse(BaseModel):
    id: int
    title: str
    description: str
    technologies: list[str] = Field(default_factory=list)
    outcome: str | None = None
    project_url: str | None = None
    created_at: datetime
    updated_at: datetime


class InterviewPracticeRequest(BaseModel):
    role_name: str | None = None
    question: str
    answer: str


class InterviewPracticeResponse(BaseModel):
    id: int
    role_name: str | None = None
    question: str
    answer: str
    feedback_score: int
    feedback_text: str
    created_at: datetime
