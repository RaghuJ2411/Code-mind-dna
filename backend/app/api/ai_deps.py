from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.ai.usage_limits import enforce_daily_limit


def require_ai_daily_limit(task_type: str, allowed_roles: list[str] | None = None):
    def dependency(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> User:
        if allowed_roles is not None and current_user.role.value not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        enforce_daily_limit(db, current_user.id, task_type)
        return current_user

    return dependency
