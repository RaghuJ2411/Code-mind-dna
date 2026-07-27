from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.career import CareerRole, MentorCareerReview
from app.models.user import User, UserRole
from app.schemas.career import CareerRoleResponse
from app.schemas.mentor_career import (
    MentorCareerReviewListResponse,
    MentorCareerReviewRequest,
    MentorCareerReviewResponse,
)
from app.services.career.career_service import CareerService

router = APIRouter(prefix="/mentor/career-reviews", tags=["mentor_career_reviews"])


def _to_response(review: MentorCareerReview) -> MentorCareerReviewResponse:
    return MentorCareerReviewResponse(
        id=review.id,
        mentor_id=review.mentor_id,
        student_id=review.student_id,
        role_id=review.role_id,
        review_type=review.review_type,
        note=review.note,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


@router.post("", response_model=MentorCareerReviewResponse)
def create_career_review(
    payload: MentorCareerReviewRequest,
    current_user=Depends(require_role(UserRole.MENTOR.value)),
    db: Session = Depends(get_db),
) -> MentorCareerReviewResponse:
    role = None
    if payload.role_id is not None:
        role = db.query(CareerRole).filter(CareerRole.id == payload.role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Career role not found")

    student = db.query(User).filter(User.id == payload.student_id, User.role == UserRole.STUDENT).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    review = MentorCareerReview(
        mentor_id=current_user.id,
        student_id=payload.student_id,
        role_id=payload.role_id,
        review_type=payload.review_type.value,
        note=payload.note,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return _to_response(review)


@router.get("", response_model=MentorCareerReviewListResponse)
def list_career_reviews(
    current_user=Depends(require_role(UserRole.MENTOR.value)),
    db: Session = Depends(get_db),
) -> MentorCareerReviewListResponse:
    reviews = (
        db.query(MentorCareerReview)
        .filter(MentorCareerReview.mentor_id == current_user.id)
        .order_by(MentorCareerReview.created_at.desc())
        .all()
    )
    return MentorCareerReviewListResponse(items=[_to_response(review) for review in reviews])


@router.get("/roles", response_model=list[CareerRoleResponse])
def list_career_roles(
    current_user=Depends(require_role(UserRole.MENTOR.value)),
    db: Session = Depends(get_db),
) -> list[CareerRoleResponse]:
    CareerService(db).ensure_default_roles()
    roles = db.query(CareerRole).order_by(CareerRole.name.asc()).all()
    return [
        CareerRoleResponse(
            id=role.id,
            name=role.name,
            seniority_level=role.seniority_level.value,
            description=role.description,
        )
        for role in roles
    ]
