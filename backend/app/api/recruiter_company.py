from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import UserRole
from app.schemas.recruiter_extended import (
    RecruiterCompanyProfile,
    RecruiterCompanyProfileResponse,
)
from app.services.recruiter.recruiter_extended_service import RecruiterExtendedService

router = APIRouter(prefix="/recruiter/company", tags=["recruiter"])


@router.get("", response_model=RecruiterCompanyProfileResponse)
def get_company_profile(
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    profile = service.get_company_profile(current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Company profile not found. Please create one.")
    return profile


@router.put("", response_model=RecruiterCompanyProfileResponse)
def upsert_company_profile(
    payload: RecruiterCompanyProfile,
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    return service.upsert_company_profile(current_user.id, payload.model_dump())

