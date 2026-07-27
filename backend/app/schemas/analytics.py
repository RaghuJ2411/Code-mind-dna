"""Analytics API schemas for request/response validation."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


# ========================= DAILY ANALYTICS SCHEMAS =========================

class DailyAnalyticsBase(BaseModel):
    """Base daily analytics data."""

    analytics_date: date
    problems_attempted: int = Field(ge=0)
    problems_solved: int = Field(ge=0)
    submissions_count: int = Field(ge=0)
    runs_count: int = Field(ge=0)
    active_minutes: int = Field(ge=0)
    wrong_answer_count: int = Field(ge=0)
    compilation_error_count: int = Field(ge=0)
    runtime_error_count: int = Field(ge=0)
    time_limit_count: int = Field(ge=0)
    easy_attempted: int = Field(ge=0)
    easy_solved: int = Field(ge=0)
    medium_attempted: int = Field(ge=0)
    medium_solved: int = Field(ge=0)
    hard_attempted: int = Field(ge=0)
    hard_solved: int = Field(ge=0)
    unique_topics_attempted: int = Field(ge=0)


class DailyAnalyticsResponse(DailyAnalyticsBase):
    """Daily analytics response."""

    id: int
    student_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========================= WEEKLY ANALYTICS SCHEMAS =========================

class WeeklyAnalyticsBase(BaseModel):
    """Base weekly analytics data."""

    week_start: date
    week_end: date
    problems_attempted: int = Field(ge=0)
    problems_solved: int = Field(ge=0)
    solve_rate: float = Field(ge=0, le=1)
    submissions_count: int = Field(ge=0)
    runs_count: int = Field(ge=0)
    active_minutes: int = Field(ge=0)
    active_days: int = Field(ge=0, le=7)
    average_attempts_to_solve: float = Field(ge=0)
    average_solve_time_minutes: float = Field(ge=0)
    error_recovery_rate: float = Field(ge=0, le=1)
    easy_solve_rate: float = Field(ge=0, le=1)
    medium_solve_rate: float = Field(ge=0, le=1)
    hard_solve_rate: float = Field(ge=0, le=1)
    unique_topics_attempted: int = Field(ge=0)
    difficulty_progression_delta: float


class WeeklyAnalyticsResponse(WeeklyAnalyticsBase):
    """Weekly analytics response."""

    id: int
    student_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========================= BEHAVIOR PROFILE SCHEMAS =========================

class ActivityMetrics(BaseModel):
    """Activity-level metrics."""

    problems_attempted: int
    problems_solved: int
    total_submissions: int
    total_runs: int
    active_minutes: int
    active_days: int


class SuccessMetrics(BaseModel):
    """Success-level metrics."""

    solve_rate: float
    first_attempt_acceptance_rate: float
    average_attempts_to_solve: float
    median_attempts_to_solve: float


class DebuggingMetrics(BaseModel):
    """Debugging behavior metrics."""

    total_wrong_answers: int
    total_compilation_errors: int
    total_runtime_errors: int
    total_time_limit_errors: int
    error_recovery_rate: float
    repeated_error_rate: float


class DifficultyMetric(BaseModel):
    """Per-difficulty metrics."""

    attempted: int
    solved: int
    solve_rate: float
    average_attempts: float


class DifficultyMetrics(BaseModel):
    """Difficulty-level metrics."""

    easy: DifficultyMetric
    medium: DifficultyMetric
    hard: DifficultyMetric
    weighted_difficulty: float


class TopicMetric(BaseModel):
    """Per-topic performance."""

    topic: str
    attempted: int
    solved: int
    solve_rate: float
    average_attempts: float
    classification: str  # INSUFFICIENT_DATA, WEAK_CANDIDATE, DEVELOPING, STRONG_CANDIDATE


class ConsistencyMetrics(BaseModel):
    """Consistency/streak metrics."""

    active_days_last_7: int
    active_days_last_30: int
    current_streak: int
    longest_streak: int
    weekly_consistency_ratio: float


class ProgressionMetrics(BaseModel):
    """Learning velocity and progression."""

    attempt_efficiency_delta: float
    solve_rate_delta: float
    solve_time_improvement_minutes: float
    difficulty_progression_delta: float


class BehaviorProfile(BaseModel):
    """Complete behavior profile for a student."""

    student_id: int
    date_range_days: int
    evidence_status: str  # NO_DATA, LIMITED_DATA, SUFFICIENT_DATA
    activity: ActivityMetrics
    success: SuccessMetrics
    debugging: DebuggingMetrics
    difficulty: DifficultyMetrics
    topics: list[TopicMetric]
    consistency: ConsistencyMetrics
    progression: ProgressionMetrics
    generated_at: datetime


# ========================= DATA QUALITY SCHEMAS =========================

class ValidationIssue(BaseModel):
    """A validation issue found in analytics data."""

    field: str | None = None
    message: str


class DailyValidationResult(BaseModel):
    """Daily analytics validation result."""

    valid: bool
    issues: list[str]
    warnings: list[str]


class WeeklyValidationResult(BaseModel):
    """Weekly analytics validation result."""

    valid: bool
    issues: list[str]
    warnings: list[str]


class AnomalyRecord(BaseModel):
    """An anomaly detected in analytics data."""

    date: str
    type: str
    value: float | None = None
    avg: float | None = None


class StudentQualityReport(BaseModel):
    """Quality report for a specific student."""

    student_id: int
    valid: bool
    daily_issues: list[dict]
    daily_warnings: list[dict]
    weekly_issues: list[dict]
    weekly_warnings: list[dict]
    anomalies: list[AnomalyRecord]


class SystemQualityReport(BaseModel):
    """System-wide data quality report."""

    timestamp: datetime
    daily_records: dict
    weekly_records: dict


# ========================= AGGREGATION SCHEMAS =========================

class AggregationResult(BaseModel):
    """Result of aggregation operation."""

    daily_aggregated: int
    weekly_aggregated: int


# ========================= PAGINATION SCHEMAS =========================

class PaginatedDailyAnalytics(BaseModel):
    """Paginated daily analytics response."""

    total: int
    page: int
    page_size: int
    data: list[DailyAnalyticsResponse]


class PaginatedWeeklyAnalytics(BaseModel):
    """Paginated weekly analytics response."""

    total: int
    page: int
    page_size: int
    data: list[WeeklyAnalyticsResponse]
