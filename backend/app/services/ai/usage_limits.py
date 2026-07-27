from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.ai_request_log import AIRequestLog
from fastapi import HTTPException, status


TASK_LIMIT_MAP = {
    "CODE_REVIEW": lambda s: s.ai_daily_limits_code_review,
    "ERROR_EXPLANATION": lambda s: s.ai_daily_limits_error_explain,
    "SKILL_GAP": lambda s: s.ai_daily_limits_skill_gap,
    "ROADMAP": lambda s: s.ai_daily_limits_roadmap,
    "CAREER_SKILL_GAP": lambda s: s.ai_daily_limits_skill_gap,
    "CAREER_PREDICTION": lambda s: s.ai_daily_limits_roadmap,
    "RESUME_PARSE": lambda s: s.ai_daily_limits_skill_gap,
    "INTERVIEW_FEEDBACK": lambda s: s.ai_daily_limits_skill_gap,
}


def enforce_daily_limit(db: Session, user_id: int, task_type: str):
    """Raise HTTPException 429 if user exceeded daily limit for task_type."""
    limit_getter = TASK_LIMIT_MAP.get(task_type)
    if not limit_getter:
        return

    limit = limit_getter(settings)
    if limit is None or limit <= 0:
        return

    today = datetime.now(timezone.utc).date()
    count = (
        db.query(AIRequestLog)
        .filter(AIRequestLog.user_id == user_id)
        .filter(AIRequestLog.task_type == task_type)
        .filter(AIRequestLog.created_at >= datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc))
        .count()
    )
    if count >= limit:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="AI daily limit exceeded")
