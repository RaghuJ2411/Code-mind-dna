from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum

from pydantic import BaseModel


class RecommendationType(str, PyEnum):
    PRACTICE_TOPIC = "PRACTICE_TOPIC"
    INCREASE_DIFFICULTY = "INCREASE_DIFFICULTY"
    REVIEW_FOUNDATION = "REVIEW_FOUNDATION"
    DEBUG_ERROR_PATTERN = "DEBUG_ERROR_PATTERN"
    IMPROVE_CONSISTENCY = "IMPROVE_CONSISTENCY"
    EXPAND_TOPIC_BREADTH = "EXPAND_TOPIC_BREADTH"
    OPTIMIZATION_PRACTICE = "OPTIMIZATION_PRACTICE"
    COMPLETE_MENTOR_TASK = "COMPLETE_MENTOR_TASK"


class RecommendationPriority(str, PyEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RecommendationAction(BaseModel):
    topic: str | None = None
    difficulty: str | None = None
    problem_count: int | None = None
    problem_id: int | None = None


class StudentRecommendationResponse(BaseModel):
    id: int
    recommendation_type: RecommendationType
    priority: RecommendationPriority
    title: str
    reason: str
    action_json: dict
    status: str
    generated_at: datetime


class StudentRecommendationCreateResponse(BaseModel):
    success: bool
    message: str


class StudentRecommendationListResponse(BaseModel):
    items: list[StudentRecommendationResponse]
