from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import UserRole
from app.schemas.recruiter_extended import RecruiterReportResponse
from app.services.recruiter.recruiter_extended_service import RecruiterExtendedService

router = APIRouter(prefix="/recruiter/reports", tags=["recruiter"])


@router.post("/generate", response_model=RecruiterReportResponse)
def generate_report(
    report_type: str = Query(..., description="Type: recruitment, hiring, or candidate"),
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    return service.generate_report(current_user.id, report_type)


@router.get("", response_model=list[RecruiterReportResponse])
def list_reports(
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    return service.list_reports(current_user.id)

