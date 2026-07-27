from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import UserRole
from app.schemas.recruiter_extended import RecruiterHiringAnalyticsResponse
from app.services.recruiter.recruiter_extended_service import RecruiterExtendedService

router = APIRouter(prefix="/recruiter/analytics", tags=["recruiter"])


@router.get("/hiring", response_model=RecruiterHiringAnalyticsResponse)
def get_hiring_analytics(
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    return service.get_hiring_analytics(current_user.id)

