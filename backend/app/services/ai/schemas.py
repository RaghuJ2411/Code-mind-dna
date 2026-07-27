from __future__ import annotations
from pydantic import BaseModel
from typing import List, Literal


class ComplexityEstimate(BaseModel):
    time_complexity: str
    space_complexity: str
    confidence: Literal["LOW", "MEDIUM", "HIGH"]


class Improvement(BaseModel):
    title: str
    reason: str
    priority: Literal["LOW", "MEDIUM", "HIGH"]


class CodeReviewResponse(BaseModel):
    summary: str
    correctness_observations: List[str]
    code_quality_observations: List[str]
    complexity: ComplexityEstimate
    improvements: List[Improvement]
    learning_points: List[str]


class ErrorExplanationResponse(BaseModel):
    summary: str
    root_cause: str
    suggested_fix: str
    confidence: Literal["LOW", "MEDIUM", "HIGH"]
    learning_resources: List[str]


class SkillGapResponse(BaseModel):
    summary: str
    missing_skills: List[str]
    improvement_steps: List[str]
    recommended_topics: List[str]


class RoadmapMilestone(BaseModel):
    milestone: str
    goal: str
    estimated_weeks: int


class LearningRoadmapResponse(BaseModel):
    summary: str
    milestones: List[RoadmapMilestone]
    estimated_total_weeks: int
    recommendations: List[str]
