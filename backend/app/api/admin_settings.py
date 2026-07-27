from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.core.database import get_db
from app.models.user import UserRole
from app.schemas.admin import AdminSettingsResponse, AdminSettingsUpdate

router = APIRouter(prefix="/admin/settings", tags=["admin-settings"])


# In-memory settings store (would be persisted in DB in production)
_settings = AdminSettingsResponse()


@router.get("", response_model=AdminSettingsResponse)
def get_admin_settings(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    return _settings


@router.put("", response_model=AdminSettingsResponse)
def update_admin_settings(
    payload: AdminSettingsUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.ADMIN.value)),
):
    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if hasattr(_settings, key) and value is not None:
            setattr(_settings, key, value)
    return _settings

