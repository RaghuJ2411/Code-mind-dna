from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import UserRole
from app.schemas.recruiter_extended import (
    RecruiterShortlistCreate,
    RecruiterShortlistResponse,
)
from app.services.recruiter.recruiter_extended_service import RecruiterExtendedService

router = APIRouter(prefix="/recruiter/shortlisted", tags=["recruiter"])


@router.get("", response_model=list[RecruiterShortlistResponse])
def list_shortlisted(
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    return service.list_shortlisted(current_user.id)


@router.post("", response_model=RecruiterShortlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_shortlist(
    payload: RecruiterShortlistCreate,
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    return service.add_to_shortlist(current_user.id, payload.model_dump())


@router.delete("/{shortlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_shortlist(
    shortlist_id: int,
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    success = service.remove_from_shortlist(current_user.id, shortlist_id)
    if not success:
        raise HTTPException(status_code=404, detail="Shortlist item not found")

