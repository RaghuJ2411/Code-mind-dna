from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.problem import DifficultyLevel, TopicType


class ProblemBase(BaseModel):
    title: str
    description: str
    difficulty: DifficultyLevel
    topic: TopicType
    constraints: str
    input_format: str
    output_format: str
    starter_code: dict[str, str] = Field(default_factory=dict)
    time_limit_ms: int = 1000
    memory_limit_mb: int = 256

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Title is required")
        return value.strip()

    @field_validator("starter_code")
    @classmethod
    def validate_starter_code(cls, value: dict[str, str]) -> dict[str, str]:
        if not value:
            raise ValueError("Starter code must include at least one language")
        if not any(code and str(code).strip() for code in value.values()):
            raise ValueError("Starter code must include at least one non-empty language")
        return value


class ProblemCreate(ProblemBase):
    slug: str

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        normalized = value.strip().lower().replace(" ", "-")
        if not normalized:
            raise ValueError("Slug is required")
        return normalized


class ProblemUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    description: str | None = None
    difficulty: DifficultyLevel | None = None
    topic: TopicType | None = None
    constraints: str | None = None
    input_format: str | None = None
    output_format: str | None = None
    starter_code: dict[str, str] | None = None
    time_limit_ms: int | None = None
    memory_limit_mb: int | None = None
    is_active: bool | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.strip().lower().replace(" ", "-")
        if not normalized:
            raise ValueError("Slug is required")
        return normalized


class ProblemListItem(BaseModel):
    id: int
    title: str
    slug: str
    difficulty: DifficultyLevel
    topic: TopicType
    status: str | None = None
    attempt_count: int | None = None
    accepted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TestCaseCreate(BaseModel):
    input_data: str
    expected_output: str
    explanation: str | None = None
    is_sample: bool = False
    order_index: int = 1


class SampleTestCaseResponse(BaseModel):
    id: int
    input_data: str
    expected_output: str
    explanation: str | None = None
    is_sample: bool
    order_index: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProblemDetailResponse(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    difficulty: DifficultyLevel
    topic: TopicType
    constraints: str
    input_format: str
    output_format: str
    starter_code: dict[str, str]
    time_limit_ms: int
    memory_limit_mb: int
    sample_test_cases: list[SampleTestCaseResponse]

    model_config = ConfigDict(from_attributes=True)


class CodeDraftSave(BaseModel):
    language: str
    code: str


class CodeDraftResponse(BaseModel):
    id: int
    student_id: int
    problem_id: int
    language: str
    code: str
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
