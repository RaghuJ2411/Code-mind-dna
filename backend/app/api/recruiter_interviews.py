from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import UserRole
from app.schemas.recruiter_extended import (
    RecruiterInterviewCreate,
    RecruiterInterviewResponse,
)
from app.services.recruiter.recruiter_extended_service import RecruiterExtendedService

router = APIRouter(prefix="/recruiter/interviews", tags=["recruiter"])


@router.get("", response_model=list[RecruiterInterviewResponse])
def list_interviews(
    status: str | None = Query(None, description="Filter by status (SCHEDULED, COMPLETED, CANCELLED)"),
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    return service.list_interviews(current_user.id, status)


@router.post("", response_model=RecruiterInterviewResponse, status_code=status.HTTP_201_CREATED)
def create_interview(
    payload: RecruiterInterviewCreate,
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    return service.create_interview(current_user.id, payload.model_dump())


@router.get("/{interview_id}", response_model=RecruiterInterviewResponse)
def get_interview(
    interview_id: int,
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    interview = service.get_interview(current_user.id, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview


@router.put("/{interview_id}", response_model=RecruiterInterviewResponse)
def update_interview(
    interview_id: int,
    payload: RecruiterInterviewCreate,
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    interview = service.update_interview(current_user.id, interview_id, payload.model_dump())
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview

