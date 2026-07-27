from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import UserRole
from app.schemas.recruiter_extended import (
    RecruiterApplicationResponse,
    RecruiterApplicationUpdate,
)
from app.services.recruiter.recruiter_extended_service import RecruiterExtendedService

router = APIRouter(prefix="/recruiter/applications", tags=["recruiter"])


@router.get("", response_model=list[RecruiterApplicationResponse])
def list_applications(
    status: str | None = Query(None, description="Filter by status"),
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    return service.list_applications(current_user.id, status)


@router.put("/{application_id}", response_model=RecruiterApplicationResponse)
def update_application(
    application_id: int,
    payload: RecruiterApplicationUpdate,
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    app = service.update_application_status(current_user.id, application_id, payload.status)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app

