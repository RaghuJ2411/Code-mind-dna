from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class RecruiterJobPostingCreate(BaseModel):
    title: str
    company: str
    location: str
    seniority_level: str
    description: str
    requirements: list[str] = Field(default_factory=list)
    is_active: bool = True


class RecruiterJobPostingResponse(BaseModel):
    id: int
    recruiter_id: int
    title: str
    company: str
    location: str
    seniority_level: str
    description: str
    requirements: list[str] = Field(default_factory=list)
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RecruiterCandidateProfile(BaseModel):
    id: int
    full_name: str
    email: str


class RecruiterRoleMatch(BaseModel):
    id: int
    name: str
    seniority_level: str
    description: str
    match_score: float


class RecruiterCandidateCard(BaseModel):
    id: int
    full_name: str
    email: str
    fit_score: float
    is_best_fit: bool = False
    readiness_label: str


class RecruiterCandidateSummary(BaseModel):
    id: int
    full_name: str
    email: str
    readiness_score: float
    readiness_label: str
    resume_strength: float
    project_alignment: float
    interview_readiness: float
    fit_score: float
    is_best_fit: bool = False
    top_roles: list[RecruiterRoleMatch] = Field(default_factory=list)
    evidence_highlights: list[str] = Field(default_factory=list)
    signal_summary: str = ""


class RecruiterCandidateDetailResponse(BaseModel):
    id: int
    full_name: str
    email: str
    profile_status: str
    overall_score: float | None = None
    overall_confidence: float | None = None
    confidence_label: str
    readiness_score: float
    readiness_label: str
    resume_strength: float
    project_alignment: float
    interview_readiness: float
    fit_score: float
    is_best_fit: bool = False
    skills: list[str] = Field(default_factory=list)
    top_roles: list[RecruiterRoleMatch] = Field(default_factory=list)
    resume_entry_count: int
    project_count: int
    interview_session_count: int
    evidence_highlights: list[str] = Field(default_factory=list)
    signal_summary: str = ""


class RecruiterDashboardResponse(BaseModel):
    total_open_jobs: int
    total_candidates: int
    job_counts_by_seniority: dict[str, int] = Field(default_factory=dict)
    best_fit_candidate: RecruiterCandidateSummary | None = None
    top_open_job: RecruiterJobPostingResponse | None = None
    recent_jobs: list[RecruiterJobPostingResponse] = Field(default_factory=list)
    recent_candidates: list[RecruiterCandidateProfile] = Field(default_factory=list)
