from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import UserRole
from app.schemas.career import (
    CareerOverviewResponse,
    CareerRoleDetailResponse,
    CareerRoleSummary,
    InterviewPracticeRequest,
    InterviewPracticeResponse,
    ProjectEntryRequest,
    ProjectEntryResponse,
    ResumeEntryRequest,
    ResumeEntryResponse,
)
from app.services.career.career_service import CareerService

router = APIRouter(prefix="/student", tags=["career"])


@router.get("/career/overview", response_model=CareerOverviewResponse)
def get_career_overview(
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> CareerOverviewResponse:
    service = CareerService(db)
    overview = service.build_career_overview(current_user.id)
    return CareerOverviewResponse(**overview)


@router.get("/career/roles", response_model=list[CareerRoleSummary])
def get_career_roles(
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> list[CareerRoleSummary]:
    service = CareerService(db)
    roles = service.get_role_catalog()
    current_overview = service.build_career_overview(current_user.id)
    return [
        CareerRoleSummary(
            id=role.id,
            name=role.name,
            seniority_level=role.seniority_level.value,
            description=role.description,
            match_score=next((item["match_score"] for item in current_overview["top_roles"] if item["id"] == role.id), 0.0),
        )
        for role in roles
    ]


@router.get("/career/roles/{role_id}", response_model=CareerRoleDetailResponse)
def get_career_role_detail(
    role_id: int,
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> CareerRoleDetailResponse:
    service = CareerService(db)
    role = service.get_role(role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Career role not found")
    return CareerRoleDetailResponse(
        id=role.id,
        name=role.name,
        seniority_level=role.seniority_level.value,
        description=role.description,
        required_skills=role.required_skills_json,
        target_score_min=role.target_score_min,
        target_score_max=role.target_score_max,
    )


@router.get("/resume", response_model=list[ResumeEntryResponse])
def list_resume_entries(
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> list[ResumeEntryResponse]:
    service = CareerService(db)
    entries = service.list_resume_entries(current_user.id)
    return [
        ResumeEntryResponse(
            id=entry.id,
            section=entry.section,
            title=entry.title,
            content=entry.content,
            skills=entry.skills_json or [],
            created_at=entry.created_at,
            updated_at=entry.updated_at,
        )
        for entry in entries
    ]


@router.post("/resume", response_model=ResumeEntryResponse)
def create_resume_entry(
    payload: ResumeEntryRequest,
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> ResumeEntryResponse:
    service = CareerService(db)
    entry = service.create_resume_entry(current_user.id, payload.model_dump())
    return ResumeEntryResponse(
        id=entry.id,
        section=entry.section,
        title=entry.title,
        content=entry.content,
        skills=entry.skills_json or [],
        created_at=entry.created_at,
        updated_at=entry.updated_at,
    )


@router.get("/projects", response_model=list[ProjectEntryResponse])
def list_projects(
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> list[ProjectEntryResponse]:
    service = CareerService(db)
    projects = service.list_projects(current_user.id)
    return [
        ProjectEntryResponse(
            id=project.id,
            title=project.title,
            description=project.description,
            technologies=project.technologies_json or [],
            outcome=project.outcome,
            project_url=project.project_url,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
        for project in projects
    ]


@router.post("/projects", response_model=ProjectEntryResponse)
def create_project(
    payload: ProjectEntryRequest,
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> ProjectEntryResponse:
    service = CareerService(db)
    project = service.create_project(current_user.id, payload.model_dump())
    return ProjectEntryResponse(
        id=project.id,
        title=project.title,
        description=project.description,
        technologies=project.technologies_json or [],
        outcome=project.outcome,
        project_url=project.project_url,
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.get("/interview/history", response_model=list[InterviewPracticeResponse])
def list_interview_history(
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> list[InterviewPracticeResponse]:
    service = CareerService(db)
    sessions = service.list_interview_sessions(current_user.id)
    return [
        InterviewPracticeResponse(
            id=session.id,
            role_name=session.role_name,
            question=session.question,
            answer=session.answer,
            feedback_score=session.feedback_score,
            feedback_text=session.feedback_text,
            created_at=session.created_at,
        )
        for session in sessions
    ]


@router.post("/interview/practice", response_model=InterviewPracticeResponse)
def practice_interview(
    payload: InterviewPracticeRequest,
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> InterviewPracticeResponse:
    service = CareerService(db)
    session = service.practice_interview(current_user.id, payload.model_dump())
    return InterviewPracticeResponse(
        id=session.id,
        role_name=session.role_name,
        question=session.question,
        answer=session.answer,
        feedback_score=session.feedback_score,
        feedback_text=session.feedback_text,
        created_at=session.created_at,
    )
