from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_role
from app.models.user import UserRole
from app.schemas.dna import (
    DNAExplanationResponse,
    DNAHistoryResponse,
    DNAProfileResponse,
    DNARecalculationResponse,
)
from app.services.dna.profile_service import CodingDNAProfileService

router = APIRouter(prefix="/dna", tags=["dna"])


@router.get("/profile", response_model=DNAProfileResponse)
def get_dna_profile(
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> DNAProfileResponse:
    service = CodingDNAProfileService(db)
    profile = service.get_latest_profile(current_user.id)
    if not profile:
        return DNAProfileResponse(profile_status="NOT_GENERATED")

    response = service.build_profile_record_response(profile)
    return DNAProfileResponse(**response)


@router.post("/profile/recalculate", response_model=DNARecalculationResponse)
def recalculate_dna_profile(
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> DNARecalculationResponse:
    service = CodingDNAProfileService(db)
    service.recalculate_profile(current_user.id)
    return DNARecalculationResponse(success=True, message="DNA profile recalculated successfully.")


@router.get("/profile/history", response_model=DNAHistoryResponse)
def get_dna_profile_history(
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> DNAHistoryResponse:
    service = CodingDNAProfileService(db)
    records = service.get_profile_history(current_user.id)
    return DNAHistoryResponse(
        total=len(records),
        data=[
            {
                "overall_score": record.overall_score,
                "overall_confidence": record.overall_confidence,
                "scoring_version": record.scoring_version,
                "calculated_at": record.calculated_at,
            }
            for record in records
        ],
    )


@router.get("/profile/dimension/{dimension_name}", response_model=DNAExplanationResponse)
def get_dna_dimension_explanation(
    dimension_name: str,
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> DNAExplanationResponse:
    service = CodingDNAProfileService(db)
    profile = service.get_latest_profile(current_user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="DNA profile not generated")

    dimension_data = profile.explanation_snapshot_json.get(dimension_name)
    if not dimension_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dimension not found")

    return DNAExplanationResponse(
        dimension=dimension_name,
        explanation=dimension_data,
        contributions=[],
    )
