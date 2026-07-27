"""AI-powered career intelligence API endpoints."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.ai_deps import require_ai_daily_limit
from app.api.deps import get_db
from app.models.user import User, UserRole
from app.schemas.ai_career import (
    CareerPredictionRequest,
    CareerPredictionResponse,
    CareerPathPrediction,
    CareerPathStep,
    InterviewFeedbackRequest,
    InterviewFeedbackResponse,
    ResumeParseRequest,
    ResumeParseResponse,
    ResumeEntry,
    SkillGapRequest,
    SkillGapResponse,
    SkillGapItem,
)
from app.services.ai.career_ai_service import CareerAIService

router = APIRouter(prefix="/student/ai-career", tags=["student-ai-career"])


@router.post("/skill-gap", response_model=SkillGapResponse)
def analyze_skill_gap(
    payload: SkillGapRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_ai_daily_limit("SKILL_GAP", allowed_roles=[UserRole.STUDENT.value])),
) -> SkillGapResponse:
    """Analyze skill gaps between student's DNA profile and a target career role."""
    try:
        service = CareerAIService(db, current_user)
        result = service.analyze_skill_gap(
            role_id=payload.role_id,
            include_recommendations=payload.include_recommendations,
        )
        return SkillGapResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI skill gap analysis failed: {str(exc)}")


@router.post("/career-prediction", response_model=CareerPredictionResponse)
def predict_career_paths(
    payload: CareerPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_ai_daily_limit("CAREER_PREDICTION", allowed_roles=[UserRole.STUDENT.value])),
) -> CareerPredictionResponse:
    """Predict optimal career paths based on student's DNA profile."""
    try:
        service = CareerAIService(db, current_user)
        result = service.predict_career_paths(
            include_alternative_paths=payload.include_alternative_paths,
        )
        return CareerPredictionResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI career prediction failed: {str(exc)}")


@router.post("/parse-resume", response_model=ResumeParseResponse)
def parse_resume(
    payload: ResumeParseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_ai_daily_limit("RESUME_PARSE", allowed_roles=[UserRole.STUDENT.value])),
) -> ResumeParseResponse:
    """Parse resume content using AI to extract structured data."""
    try:
        service = CareerAIService(db, current_user)
        result = service.parse_resume_content(
            resume_content=payload.resume_content,
            target_role=payload.target_role,
        )
        return ResumeParseResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI resume parsing failed: {str(exc)}")


@router.post("/interview-feedback", response_model=InterviewFeedbackResponse)
def generate_interview_feedback(
    payload: InterviewFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_ai_daily_limit("INTERVIEW_FEEDBACK", allowed_roles=[UserRole.STUDENT.value])),
) -> InterviewFeedbackResponse:
    """Generate AI-powered interview feedback for a practice response."""
    try:
        service = CareerAIService(db, current_user)
        result = service.generate_interview_feedback(
            question=payload.question,
            answer=payload.answer,
            role_name=payload.role_name,
            seniority_level=payload.seniority_level,
        )
        return InterviewFeedbackResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI interview feedback failed: {str(exc)}")

