from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import UserRole
from app.schemas.recruiter_extended import RecruiterSettingsPayload
from app.services.recruiter.recruiter_extended_service import RecruiterExtendedService

router = APIRouter(prefix="/recruiter/settings", tags=["recruiter"])


@router.get("")
def get_settings(
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    settings = service.get_settings(current_user.id)
    if not settings:
        raise HTTPException(status_code=404, detail="User not found")
    return settings


@router.put("")
def update_settings(
    payload: RecruiterSettingsPayload,
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    settings = service.update_settings(current_user.id, payload.model_dump(exclude_none=True))
    if not settings:
        raise HTTPException(status_code=404, detail="User not found")
    return settings

