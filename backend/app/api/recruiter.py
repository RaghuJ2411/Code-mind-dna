from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import UserRole
from app.schemas.recruiter import (
    RecruiterCandidateCard,
    RecruiterCandidateDetailResponse,
    RecruiterCandidateProfile,
    RecruiterDashboardResponse,
    RecruiterJobPostingCreate,
    RecruiterJobPostingResponse,
)
from app.schemas.user import UserOut
from app.services.recruiter.recruiter_service import RecruiterService

router = APIRouter(prefix="/recruiter", tags=["recruiter"])


def _build_job_response(job: object) -> RecruiterJobPostingResponse:
    return RecruiterJobPostingResponse(
        id=job.id,
        recruiter_id=job.recruiter_id,
        title=job.title,
        company=job.company,
        location=job.location,
        seniority_level=job.seniority_level.value,
        description=job.description,
        requirements=job.requirements_json or [],
        is_active=job.is_active,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


@router.get("/dashboard", response_model=RecruiterDashboardResponse)
def get_recruiter_dashboard(
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
) -> RecruiterDashboardResponse:
    service = RecruiterService(db)
    dashboard = service.get_dashboard_data(current_user.id)
    return RecruiterDashboardResponse(
        total_open_jobs=dashboard["total_open_jobs"],
        total_candidates=dashboard["total_candidates"],
        job_counts_by_seniority=dashboard.get("job_counts_by_seniority", {}),
        best_fit_candidate=dashboard.get("best_fit_candidate"),
        top_open_job=_build_job_response(dashboard["top_open_job"]) if dashboard.get("top_open_job") else None,
        recent_jobs=[_build_job_response(job) for job in dashboard["recent_jobs"]],
        recent_candidates=[
            RecruiterCandidateProfile(id=candidate.id, full_name=candidate.full_name, email=candidate.email)
            for candidate in dashboard["recent_candidates"]
        ],
    )


@router.get("/jobs", response_model=list[RecruiterJobPostingResponse])
def list_jobs(
    query: str | None = Query(None, description="Search term for job title, company, location, or description"),
    seniority_level: str | None = Query(None, description="Filter jobs by seniority level"),
    location: str | None = Query(None, description="Filter jobs by location"),
    company: str | None = Query(None, description="Filter jobs by company"),
    active_only: bool = Query(True, description="Only include active job postings"),
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
) -> list[RecruiterJobPostingResponse]:
    service = RecruiterService(db)
    jobs = service.search_job_postings(
        current_user.id,
        query=query,
        seniority_level=seniority_level,
        location=location,
        company=company,
        is_active=active_only,
    )
    return [_build_job_response(job) for job in jobs]


@router.post("/jobs", response_model=RecruiterJobPostingResponse, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: RecruiterJobPostingCreate,
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
) -> RecruiterJobPostingResponse:
    service = RecruiterService(db)
    job = service.create_job_posting(current_user.id, payload.model_dump())
    return _build_job_response(job)


@router.get("/jobs/{job_id}", response_model=RecruiterJobPostingResponse)
def get_job_detail(
    job_id: int,
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
) -> RecruiterJobPostingResponse:
    service = RecruiterService(db)
    job = service.get_job_posting(current_user.id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return _build_job_response(job)


@router.get("/candidates", response_model=list[RecruiterCandidateCard])
def list_candidates(
    query: str | None = Query(None, description="Search term for candidate full name or email"),
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
) -> list[RecruiterCandidateCard]:
    service = RecruiterService(db)
    candidates = service.search_candidate_profiles_summary(query=query)
    return [
        RecruiterCandidateCard(
            id=candidate["id"],
            full_name=candidate["full_name"],
            email=candidate["email"],
            fit_score=candidate["fit_score"],
            is_best_fit=candidate["is_best_fit"],
            readiness_label=candidate["readiness_label"],
        )
        for candidate in candidates
    ]


@router.get("/candidates/{student_id}", response_model=RecruiterCandidateDetailResponse)
def get_candidate_detail(
    student_id: int,
    current_user=Depends(require_role(UserRole.RECRUITER.value)),
    db: Session = Depends(get_db),
) -> RecruiterCandidateDetailResponse:
    service = RecruiterService(db)
    candidate = service.get_candidate_profile_summary(student_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return RecruiterCandidateDetailResponse(**candidate)
