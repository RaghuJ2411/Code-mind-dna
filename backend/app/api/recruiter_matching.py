from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import UserRole
from app.schemas.recruiter_extended import (
    RecruiterAIMatchResponse,
    RecruiterCandidateRankingResponse,
)
from app.services.recruiter.recruiter_extended_service import RecruiterExtendedService

router = APIRouter(prefix="/recruiter/matching", tags=["recruiter"])


@router.get("/rankings", response_model=list[RecruiterCandidateRankingResponse])
def rank_candidates(
    limit: int = Query(20, ge=1, le=50),
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    return service.rank_candidates(current_user.id, limit)


@router.get("/match/{candidate_id}/{job_id}", response_model=RecruiterAIMatchResponse)
def get_ai_match(
    candidate_id: int,
    job_id: int,
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
):
    service = RecruiterExtendedService(db)
    match = service.get_ai_match(current_user.id, candidate_id, job_id)
    if not match:
        raise HTTPException(status_code=404, detail="Candidate or job not found")
    return match

