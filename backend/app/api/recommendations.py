from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import UserRole
from app.schemas.recommendations import (
    StudentRecommendationListResponse,
    StudentRecommendationResponse,
)
from app.services.recommendations.recommendation_service import RecommendationService
from app.models.student_recommendation import StudentRecommendation

router = APIRouter(prefix="/student/recommendations", tags=["recommendations"])


def _to_response(record: StudentRecommendation) -> StudentRecommendationResponse:
    return StudentRecommendationResponse(
        id=record.id,
        recommendation_type=record.recommendation_type,
        priority=record.priority,
        title=record.title,
        reason=record.reason,
        action_json=record.action_json,
        status=record.status,
        generated_at=record.generated_at,
    )


@router.get("", response_model=StudentRecommendationListResponse)
def list_recommendations(
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> StudentRecommendationListResponse:
    service = RecommendationService(db)
    items = service.list_student_recommendations(current_user.id)
    return StudentRecommendationListResponse(items=[_to_response(item) for item in items])


@router.post("/refresh", response_model=StudentRecommendationListResponse)
def refresh_recommendations(
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> StudentRecommendationListResponse:
    service = RecommendationService(db)
    service.generate_student_recommendations(current_user.id)
    items = service.list_student_recommendations(current_user.id)
    return StudentRecommendationListResponse(items=[_to_response(item) for item in items])


@router.post("/{recommendation_id}/start", response_model=StudentRecommendationResponse)
def start_recommendation(
    recommendation_id: int,
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> StudentRecommendationResponse:
    service = RecommendationService(db)
    record = service.update_recommendation_status(current_user.id, recommendation_id, "IN_PROGRESS")
    if not record:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return _to_response(record)


@router.post("/{recommendation_id}/complete", response_model=StudentRecommendationResponse)
def complete_recommendation(
    recommendation_id: int,
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> StudentRecommendationResponse:
    service = RecommendationService(db)
    record = service.update_recommendation_status(current_user.id, recommendation_id, "COMPLETED")
    if not record:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return _to_response(record)


@router.post("/{recommendation_id}/dismiss", response_model=StudentRecommendationResponse)
def dismiss_recommendation(
    recommendation_id: int,
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> StudentRecommendationResponse:
    service = RecommendationService(db)
    record = service.update_recommendation_status(current_user.id, recommendation_id, "DISMISSED")
    if not record:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return _to_response(record)
