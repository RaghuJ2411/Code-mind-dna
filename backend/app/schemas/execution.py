from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ExecutionRequest(BaseModel):
    problem_id: int
    language: str
    source_code: str


class TestExecutionResult(BaseModel):
    test_case_number: int
    passed: bool
    status: str
    input: str
    expected_output: str
    actual_output: str
    runtime_ms: int | None = None
    memory_kb: int | None = None
    error_message: str | None = None


class RunCodeResponse(BaseModel):
    overall_status: str
    passed: int
    total: int
    results: list[TestExecutionResult]


class SubmitCodeResponse(BaseModel):
    submission_id: int
    verdict: str
    passed_test_cases: int
    total_test_cases: int
    runtime_ms: int | None = None
    memory_kb: int | None = None
    attempt_number: int
    message: str


class SubmissionListItem(BaseModel):
    submission_id: int
    problem_id: int
    problem_title: str
    language: str
    verdict: str
    passed_test_cases: int
    total_test_cases: int
    runtime_ms: int | None = None
    memory_kb: int | None = None
    attempt_number: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SubmissionDetailResponse(BaseModel):
    submission_id: int
    problem_id: int
    problem_title: str
    language: str
    verdict: str
    passed_test_cases: int
    total_test_cases: int
    runtime_ms: int | None = None
    memory_kb: int | None = None
    attempt_number: int
    source_code: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CodingSessionStartResponse(BaseModel):
    session_id: int
    started_at: datetime
    resumed: bool
