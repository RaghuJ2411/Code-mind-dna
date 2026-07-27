from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.ai_request_log import AIRequestLog


class AIUsageSummaryService:
    def __init__(self, db: Session):
        self.db = db

    def get_daily_usage(self, user_id: int) -> dict[str, object]:
        today = datetime.now(timezone.utc).date()
        counts = (
            self.db.query(AIRequestLog.task_type, AIRequestLog.status)
            .filter(AIRequestLog.user_id == user_id)
            .filter(AIRequestLog.created_at >= datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc))
            .all()
        )

        usage = {task: {"total": 0, "success": 0, "failed": 0} for task in ["CODE_REVIEW", "ERROR_EXPLANATION", "SKILL_GAP", "ROADMAP"]}
        for task_type, status in counts:
            if task_type not in usage:
                continue
            usage[task_type]["total"] += 1
            if status == "SUCCESS":
                usage[task_type]["success"] += 1
            else:
                usage[task_type]["failed"] += 1

        task_limit_field = {
            "CODE_REVIEW": "ai_daily_limits_code_review",
            "ERROR_EXPLANATION": "ai_daily_limits_error_explain",
            "SKILL_GAP": "ai_daily_limits_skill_gap",
            "ROADMAP": "ai_daily_limits_roadmap",
        }

        limits = {
            task: getattr(settings, task_limit_field[task])
            for task in usage
        }

        return {
            "tasks": usage,
            "limits": limits,
        }

    def get_recent_requests(self, user_id: int, limit: int = 10) -> list[dict[str, object]]:
        rows = (
            self.db.query(AIRequestLog)
            .filter(AIRequestLog.user_id == user_id)
            .order_by(AIRequestLog.created_at.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": row.id,
                "task_type": row.task_type,
                "provider": row.provider,
                "model_name": row.model,
                "status": row.status,
                "input_token_count": row.input_token_count,
                "output_token_count": row.output_token_count,
                "latency_ms": row.latency_ms,
                "error_category": row.error_category,
                "created_at": row.created_at,
            }
            for row in rows
        ]
