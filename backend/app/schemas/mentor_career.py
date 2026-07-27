from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum

from pydantic import BaseModel, ConfigDict, Field


class MentorCareerReviewType(str, PyEnum):
    CAREER = "CAREER"


class MentorCareerReviewRequest(BaseModel):
    student_id: int
    role_id: int | None = None
    note: str
    review_type: MentorCareerReviewType = MentorCareerReviewType.CAREER


class MentorCareerReviewResponse(BaseModel):
    id: int
    mentor_id: int
    student_id: int
    role_id: int | None = None
    review_type: MentorCareerReviewType
    note: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MentorCareerReviewListResponse(BaseModel):
    items: list[MentorCareerReviewResponse] = Field(default_factory=list)
