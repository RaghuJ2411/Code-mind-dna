"""AI-powered career intelligence schemas for request/response validation."""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


# ========================= SKILL GAP ANALYSIS =========================

class SkillGapRequest(BaseModel):
    """Request for AI skill gap analysis."""
    role_id: int
    include_recommendations: bool = True


class SkillGapItem(BaseModel):
    """A single skill gap entry."""
    skill: str
    current_proficiency: float = Field(ge=0, le=100)
    required_proficiency: float = Field(ge=0, le=100)
    gap: float = Field(ge=-100, le=100)
    priority: str  # CRITICAL, IMPORTANT, NICE_TO_HAVE
    description: str | None = None


class SkillGapResponse(BaseModel):
    """AI-powered skill gap analysis response."""
    role_name: str
    role_seniority: str
    overall_match_percentage: float = Field(ge=0, le=100)
    gaps: list[SkillGapItem] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    estimated_improvement_time: str | None = None
    ai_insight: str | None = None
    generated_at: datetime


# ========================= CAREER PATH PREDICTION =========================

class CareerPathStep(BaseModel):
    """A single step in a career path."""
    role_name: str
    seniority_level: str
    match_score: float = Field(ge=0, le=100)
    time_to_achieve: str | None = None
    skills_to_develop: list[str] = Field(default_factory=list)
    description: str | None = None


class CareerPathPrediction(BaseModel):
    """A single career path prediction."""
    path_name: str
    confidence: float = Field(ge=0, le=100)
    steps: list[CareerPathStep] = Field(default_factory=list)
    ai_rationale: str | None = None


class CareerPredictionRequest(BaseModel):
    """Request for AI career path prediction."""
    include_alternative_paths: bool = True


class CareerPredictionResponse(BaseModel):
    """AI-powered career path prediction response."""
    primary_path: CareerPathPrediction | None = None
    alternative_paths: list[CareerPathPrediction] = Field(default_factory=list)
    overall_readiness_score: float = Field(ge=0, le=100)
    confidence_label: str | None = None
    ai_summary: str | None = None
    generated_at: datetime


# ========================= RESUME PARSING =========================

class ResumeEntry(BaseModel):
    """A parsed resume entry."""
    section: str
    title: str
    content: str
    skills: list[str] = Field(default_factory=list)


class ResumeParseResponse(BaseModel):
    """AI-parsed resume structure."""
    parsed_entries: list[ResumeEntry] = Field(default_factory=list)
    extracted_skills: list[str] = Field(default_factory=list)
    suggested_roles: list[str] = Field(default_factory=list)
    experience_years: float | None = None
    education_level: str | None = None
    ai_summary: str | None = None


class ResumeParseRequest(BaseModel):
    """Request for AI resume parsing."""
    resume_content: str
    target_role: str | None = None


# ========================= AI INTERVIEW FEEDBACK =========================

class InterviewFeedbackResponse(BaseModel):
    """AI-generated interview feedback."""
    overall_score: float = Field(ge=0, le=100)
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    content_quality: str | None = None
    communication_clarity: str | None = None
    technical_accuracy: str | None = None
    sample_answer: str | None = None
    suggested_followups: list[str] = Field(default_factory=list)
    ai_feedback: str | None = None
    generated_at: datetime


class InterviewFeedbackRequest(BaseModel):
    """Request for AI interview feedback."""
    question: str
    answer: str
    role_name: str | None = None
    seniority_level: str | None = None

