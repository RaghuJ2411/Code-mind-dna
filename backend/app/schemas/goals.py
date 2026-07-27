from __future__ import annotations

from datetime import date, datetime
from enum import Enum as PyEnum

from pydantic import BaseModel, Field


class GoalType(str, PyEnum):
    SOLVE_PROBLEMS = "SOLVE_PROBLEMS"
    ACTIVE_DAYS = "ACTIVE_DAYS"
    PRACTICE_TOPIC = "PRACTICE_TOPIC"
    COMPLETE_MENTOR_TASKS = "COMPLETE_MENTOR_TASKS"


class GoalStatus(str, PyEnum):
    ACTIVE = "ACTIVE"
    ACHIEVED = "ACHIEVED"
    CANCELLED = "CANCELLED"


class StudentGoalCreate(BaseModel):
    goal_type: GoalType
    title: str
    description: str | None = None
    target_value: int = Field(gt=0)
    period_start: date
    period_end: date


class StudentGoalResponse(BaseModel):
    id: int
    goal_type: GoalType
    title: str
    description: str | None = None
    target_value: int
    current_value: int
    period_start: date
    period_end: date
    status: GoalStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
