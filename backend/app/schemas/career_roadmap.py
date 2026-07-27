from __future__ import annotations

from datetime import datetime, date
from pydantic import BaseModel, Field


class CareerRoadmapResponse(BaseModel):
    id: int
    career_goal: str
    company_goal: str | None = None
    target_role: str | None = None
    target_seniority: str | None = None
    timeline_months: int | None = None
    skills_required: list[str] = Field(default_factory=list)
    current_skills: list[str] = Field(default_factory=list)
    gap_analysis: dict | None = None
    ai_suggestions: dict | None = None
    milestones: list[dict] = Field(default_factory=list)
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CareerRoadmapCreate(BaseModel):
    career_goal: str
    company_goal: str | None = None
    target_role: str | None = None
    target_seniority: str | None = None
    timeline_months: int | None = None
    skills_required: list[str] = Field(default_factory=list)
    current_skills: list[str] = Field(default_factory=list)


class RoadmapMilestoneResponse(BaseModel):
    id: int
    roadmap_id: int
    title: str
    description: str | None = None
    milestone_type: str
    target_date: date | None = None
    is_completed: bool
    completed_at: datetime | None = None
    progress_pct: float
    order_index: int

    class Config:
        from_attributes = True


class RoadmapMilestoneCreate(BaseModel):
    title: str
    description: str | None = None
    milestone_type: str = "WEEKLY"
    target_date: date | None = None
    order_index: int = 0


class RoadmapMilestoneUpdate(BaseModel):
    progress_pct: float | None = None
    is_completed: bool | None = None


class WeeklyGoalCreate(BaseModel):
    title: str
    description: str | None = None
    week_start: date
    week_end: date | None = None


class WeeklyGoalResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    week_start: date
    week_end: date | None = None
    is_completed: bool
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class MonthlyGoalCreate(BaseModel):
    title: str
    description: str | None = None
    month: str


class MonthlyGoalResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    month: str
    is_completed: bool
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class AISuggestionResponse(BaseModel):
    suggestions: list[str] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)

