from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import UserRole
from app.schemas.recruiter_extended import (
    RecruiterMessageCreate,
    RecruiterMessageResponse,
)
from app.services.recruiter.recruiter_extended_service import RecruiterExtendedService

router = APIRouter(prefix="/recruiter/messages", tags=["recruiter"])


@router.get("/conversations", response_model=list)
def list_conversations(
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    return service.list_conversations(current_user.id)


@router.post("", response_model=RecruiterMessageResponse)
def send_message(
    payload: RecruiterMessageCreate,
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    return service.send_message(current_user.id, payload.model_dump())

