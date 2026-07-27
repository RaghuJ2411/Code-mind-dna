from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class RecruiterInterviewCreate(BaseModel):
    candidate_id: int
    job_id: int
    interviewer: str
    slot: str
    mode: str = "Zoom"
    link: str | None = None
    notes: str | None = None


class RecruiterInterviewResponse(BaseModel):
    id: int
    candidate_id: int
    candidate_name: str = ""
    job_id: int
    job_title: str = ""
    interviewer: str
    slot: str
    mode: str
    link: str | None = None
    notes: str | None = None
    status: str = "SCHEDULED"
    created_at: datetime
    updated_at: datetime


class RecruiterMessageCreate(BaseModel):
    recipient_id: int
    subject: str
    body: str


class RecruiterMessageResponse(BaseModel):
    id: int
    sender_id: int
    sender_name: str = ""
    recipient_id: int
    recipient_name: str = ""
    subject: str
    body: str
    is_read: bool = False
    created_at: datetime


class RecruiterApplicationResponse(BaseModel):
    id: int
    student_id: int
    student_name: str = ""
    student_email: str = ""
    job_id: int
    job_title: str = ""
    job_company: str = ""
    status: str
    applied_at: datetime
    fit_score: float | None = None


class RecruiterApplicationUpdate(BaseModel):
    status: str


class RecruiterShortlistCreate(BaseModel):
    candidate_id: int
    job_id: int
    rating: float | None = None
    notes: str | None = None


class RecruiterShortlistResponse(BaseModel):
    id: int
    candidate_id: int
    candidate_name: str = ""
    candidate_email: str = ""
    job_id: int
    job_title: str = ""
    rating: float | None = None
    notes: str | None = None
    created_at: datetime


class RecruiterCompanyProfile(BaseModel):
    company_name: str
    description: str = ""
    industry: str = ""
    website: str = ""
    employees: str = ""
    location: str = ""


class RecruiterCompanyProfileResponse(BaseModel):
    id: int
    recruiter_id: int
    company_name: str
    description: str = ""
    industry: str = ""
    website: str = ""
    employees: str = ""
    location: str = ""
    updated_at: datetime | None = None


class RecruiterSettingsPayload(BaseModel):
    full_name: str | None = None
    email: str | None = None
    password: str | None = None
    notifications: bool = True
    theme: str = "light"
    language: str = "English"


class RecruiterHiringAnalyticsResponse(BaseModel):
    total_jobs: int = 0
    active_jobs: int = 0
    total_applications: int = 0
    total_interviews: int = 0
    total_shortlisted: int = 0
    offer_conversion_rate: float = 0.0
    hiring_funnel: dict[str, int] = Field(default_factory=lambda: {"applied": 0, "shortlisted": 0, "interviewed": 0, "offered": 0, "hired": 0})
    top_skills_demand: list[dict[str, object]] = Field(default_factory=list)
    monthly_hires: int = 0


class RecruiterReportResponse(BaseModel):
    id: int
    title: str
    description: str
    report_type: str
    generated_at: datetime
    data: dict[str, object] = Field(default_factory=dict)


class RecruiterCandidateRankingResponse(BaseModel):
    id: int
    full_name: str
    email: str
    fit_score: float
    readiness_label: str
    resume_strength: float
    interview_readiness: float
    skills: list[str] = Field(default_factory=list)
    top_role_match: str = ""
    rank: int
    is_best_fit: bool = False


class RecruiterAIMatchResponse(BaseModel):
    candidate_id: int
    candidate_name: str
    job_id: int
    job_title: str
    match_score: float
    match_rationale: str = ""
    skill_gaps: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    recommendation: str = ""

