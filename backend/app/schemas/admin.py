from __future__ import annotations
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.user import UserRole


class AdminDashboardResponse(BaseModel):
    total_users: int
    active_users: int
    role_counts: dict[str, int] = Field(default_factory=dict)
    total_problems: int
    active_problems: int
    total_audit_events: int


class UserAdminResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    items: list[UserAdminResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class UserUpdateRequest(BaseModel):
    role: UserRole | None = None
    is_active: bool | None = None


class AuditLogResponse(BaseModel):
    id: int
    user_email: str | None
    path: str
    method: str
    status_code: int
    remote_addr: str | None
    user_agent: str | None
    request_metadata_json: dict[str, Any] | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


# ─── System Monitoring ───────────────────────────────────────────

class SystemOverviewResponse(BaseModel):
    uptime_seconds: float = 0
    cpu_percent: float = 0
    memory_percent: float = 0
    disk_percent: float = 0
    active_requests: int = 0
    database_size_mb: float = 0
    last_checked: datetime = Field(default_factory=datetime.utcnow)


class SystemServiceItem(BaseModel):
    name: str
    status: str  # healthy | degraded | down
    uptime_seconds: float | None = None
    last_checked: datetime = Field(default_factory=datetime.utcnow)


class SystemServicesResponse(BaseModel):
    services: list[SystemServiceItem]


class SystemLogEntry(BaseModel):
    id: int
    level: str
    message: str
    source: str | None = None
    created_at: datetime


class SystemLogListResponse(BaseModel):
    items: list[SystemLogEntry]
    total: int
    page: int
    page_size: int
    total_pages: int


# ─── Platform Analytics ──────────────────────────────────────────

class PlatformAnalyticsOverview(BaseModel):
    total_users: int = 0
    total_problems: int = 0
    total_submissions: int = 0
    total_sessions: int = 0
    avg_solve_rate: float = 0
    active_users_last_7d: int = 0
    active_users_last_30d: int = 0
    new_users_last_7d: int = 0
    new_users_last_30d: int = 0


class EngagementMetrics(BaseModel):
    daily_active_users: list[dict[str, Any]] = Field(default_factory=list)
    weekly_active_users: list[dict[str, Any]] = Field(default_factory=list)
    submissions_per_day: list[dict[str, Any]] = Field(default_factory=list)


class PlatformUsageMetrics(BaseModel):
    users_by_role: dict[str, int] = Field(default_factory=dict)
    problems_by_difficulty: dict[str, int] = Field(default_factory=dict)
    problems_by_topic: dict[str, int] = Field(default_factory=dict)
    top_active_users: list[dict[str, Any]] = Field(default_factory=list)


# ─── Database Health ─────────────────────────────────────────────

class DatabaseHealthResponse(BaseModel):
    status: str = "healthy"
    size_mb: float = 0
    connection_count: int = 0
    max_connections: int = 100
    active_queries: int = 0
    cache_hit_ratio: float | None = None
    slow_queries_last_24h: int = 0


class DatabaseTableInfo(BaseModel):
    table_name: str
    row_count: int
    size_mb: float
    index_count: int
    last_vacuum: datetime | None = None


class DatabaseTablesResponse(BaseModel):
    tables: list[DatabaseTableInfo]


# ─── AI Monitoring ───────────────────────────────────────────────

class AIUsageOverview(BaseModel):
    total_requests: int = 0
    success_count: int = 0
    failed_count: int = 0
    total_tokens_input: int = 0
    total_tokens_output: int = 0
    avg_latency_ms: float = 0
    requests_today: int = 0
    requests_this_week: int = 0


class AIRequestDetail(BaseModel):
    id: int
    user_id: int | None = None
    task_type: str
    provider: str | None = None
    model: str | None = None
    status: str
    input_token_count: int | None = None
    output_token_count: int | None = None
    latency_ms: int | None = None
    error_category: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class AIRequestListResponse(BaseModel):
    items: list[AIRequestDetail]
    total: int
    page: int
    page_size: int
    total_pages: int


class AILimitsUpdate(BaseModel):
    code_review: int | None = None
    error_explanation: int | None = None
    skill_gap: int | None = None
    roadmap: int | None = None


# ─── Admin Reports ───────────────────────────────────────────────

class AdminReportItem(BaseModel):
    id: int
    report_type: str
    title: str
    status: str
    created_at: datetime | None = None
    content_json: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)


class AdminReportListResponse(BaseModel):
    items: list[AdminReportItem]
    total: int


class AdminReportGenerateRequest(BaseModel):
    report_type: str  # user_summary, problem_stats, platform_overview, ai_usage
    title: str | None = None


# ─── Admin Settings ──────────────────────────────────────────────

class AdminSettingsResponse(BaseModel):
    allow_registration: bool = True
    default_role: str = "STUDENT"
    session_timeout_minutes: int = 1440
    max_login_attempts: int = 5
    maintenance_mode: bool = False
    ai_features_enabled: bool = True
    daily_ai_limits: dict[str, int] = Field(default_factory=lambda: {
        "code_review": 10,
        "error_explanation": 15,
        "skill_gap": 10,
        "roadmap": 2,
    })


class AdminSettingsUpdate(BaseModel):
    allow_registration: bool | None = None
    default_role: str | None = None
    session_timeout_minutes: int | None = None
    max_login_attempts: int | None = None
    maintenance_mode: bool | None = None
    ai_features_enabled: bool | None = None
    daily_ai_limits: dict[str, int] | None = None


# ─── Permissions / RBAC ──────────────────────────────────────────

class RolePermissionItem(BaseModel):
    role: str
    permissions: list[str] = Field(default_factory=list)
    description: str | None = None


class PermissionsListResponse(BaseModel):
    roles: list[RolePermissionItem]
    all_permissions: list[str] = Field(default_factory=list)


class PermissionsUpdateRequest(BaseModel):
    permissions: list[str]
