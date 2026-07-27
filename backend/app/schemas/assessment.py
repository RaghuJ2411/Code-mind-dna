from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class AssessmentResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    assessment_type: str
    difficulty: str
    time_limit_minutes: int | None = None
    passing_score: float
    total_questions: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AssessmentQuestionResponse(BaseModel):
    id: int
    question_type: str
    question_text: str
    options: list[str] | None = None
    points: int
    order_index: int

    class Config:
        from_attributes = True


class AssessmentDetailResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    assessment_type: str
    difficulty: str
    time_limit_minutes: int | None = None
    passing_score: float
    total_questions: int
    questions: list[AssessmentQuestionResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class StartAssessmentResponse(BaseModel):
    attempt_id: int
    started_at: datetime
    time_limit_minutes: int | None = None
    questions: list[AssessmentQuestionResponse] = Field(default_factory=list)


class AnswerSubmission(BaseModel):
    question_id: int
    answer: str


class SubmitAssessmentRequest(BaseModel):
    answers: list[AnswerSubmission]


class AssessmentResultResponse(BaseModel):
    attempt_id: int
    score: float
    passed: bool
    total_questions: int
    correct_answers: int
    time_taken_seconds: int | None = None
    submitted_at: datetime | None = None
    results: list[dict] = Field(default_factory=list)


class AssessmentHistoryItem(BaseModel):
    attempt_id: int
    assessment_id: int
    assessment_title: str
    score: float | None = None
    passed: bool
    started_at: datetime
    submitted_at: datetime | None = None

    class Config:
        from_attributes = True


class AssessmentHistoryResponse(BaseModel):
    items: list[AssessmentHistoryItem] = Field(default_factory=list)


class PerformanceAnalysis(BaseModel):
    total_assessments: int = 0
    average_score: float = 0.0
    pass_rate: float = 0.0
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)

