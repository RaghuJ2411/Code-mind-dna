from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel
from typing import Dict


class AIUsageTaskSummary(BaseModel):
    total: int
    success: int
    failed: int


class AIUsageLimits(BaseModel):
    CODE_REVIEW: int
    ERROR_EXPLANATION: int
    SKILL_GAP: int
    ROADMAP: int


class AIUsageSummary(BaseModel):
    tasks: Dict[str, AIUsageTaskSummary]
    limits: AIUsageLimits


class AIUsageRequestItem(BaseModel):
    id: int
    task_type: str
    provider: str | None = None
    model_name: str | None = None
    status: str
    input_token_count: int | None = None
    output_token_count: int | None = None
    latency_ms: int | None = None
    error_category: str | None = None
    created_at: datetime


class AIUsageHistoryResponse(BaseModel):
    daily_summary: AIUsageSummary
    recent_requests: list[AIUsageRequestItem] = []
