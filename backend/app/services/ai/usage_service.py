from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.ai_request_log import AIRequestLog


def record_ai_request(db: Session, user_id: int, task_type: str, provider: str, model: str, prompt_version: str, status: str, latency_ms: int | None = None, input_tokens: int | None = None, output_tokens: int | None = None, error_category: str | None = None, meta: dict | None = None) -> AIRequestLog:
    entry = AIRequestLog(
        user_id=user_id,
        task_type=task_type,
        provider=provider,
        model=model,
        prompt_version=prompt_version,
        status=status,
        input_token_count=input_tokens,
        output_token_count=output_tokens,
        latency_ms=latency_ms,
        error_category=error_category,
        request_metadata_json=meta or {},
        created_at=datetime.now(timezone.utc),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
