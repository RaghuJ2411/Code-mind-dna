from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.recruiter import JobPosting, StudentJobApplication
from app.models.user import UserRole
from app.schemas.student import (
    PracticeQueueResponse,
    RecentActivityResponse,
    StudentDashboardOverviewResponse,
    StudentJobApplicationResponse,
    StudentJobResponse,
)
from app.services.student.dashboard_service import StudentDashboardService

router = APIRouter(prefix="/student", tags=["student"])


@router.get("/dashboard/overview", response_model=StudentDashboardOverviewResponse)
def get_student_dashboard_overview(
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> StudentDashboardOverviewResponse:
    service = StudentDashboardService(db)
    overview = service.build_overview(current_user)
    return StudentDashboardOverviewResponse(**overview)


@router.get("/practice-queue", response_model=PracticeQueueResponse)
def get_student_practice_queue(
    limit: int = Query(8, ge=1, le=20),
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> PracticeQueueResponse:
    service = StudentDashboardService(db)
    return PracticeQueueResponse(items=service.build_practice_queue(current_user.id, limit=limit))


@router.get("/activity/recent", response_model=RecentActivityResponse)
def get_student_recent_activity(
    limit: int = Query(10, ge=1, le=25),
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> RecentActivityResponse:
    service = StudentDashboardService(db)
    return RecentActivityResponse(items=service.build_recent_activity(current_user.id, limit=limit))


@router.get("/jobs", response_model=list[StudentJobResponse])
def list_student_jobs(
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> list[StudentJobResponse]:
    jobs = (
        db.query(JobPosting)
        .filter(JobPosting.is_active.is_(True))
        .order_by(JobPosting.created_at.desc())
        .all()
    )
    return [
        StudentJobResponse(
            id=job.id,
            title=job.title,
            company=job.company,
            location=job.location,
            seniority_level=job.seniority_level.value,
            description=job.description,
            requirements=job.requirements_json or [],
            is_active=job.is_active,
            created_at=job.created_at,
        )
        for job in jobs
    ]


@router.post("/jobs/{job_id}/apply", response_model=StudentJobApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_to_job(
    job_id: int,
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> StudentJobApplicationResponse:
    job = db.query(JobPosting).filter(JobPosting.id == job_id).first()
    if not job or not job.is_active:
        raise HTTPException(status_code=404, detail="Job posting not found")

    existing = (
        db.query(StudentJobApplication)
        .filter(StudentJobApplication.student_id == current_user.id, StudentJobApplication.job_id == job_id)
        .first()
    )
    if existing:
        return StudentJobApplicationResponse(
            id=existing.id,
            job_id=existing.job_id,
            status=existing.status,
            applied_at=existing.applied_at,
        )

    application = StudentJobApplication(student_id=current_user.id, job_id=job_id)
    db.add(application)
    db.commit()
    db.refresh(application)
    return StudentJobApplicationResponse(
        id=application.id,
        job_id=application.job_id,
        status=application.status,
        applied_at=application.applied_at,
    )


@router.get("/applications", response_model=list[StudentJobApplicationResponse])
def list_student_applications(
    current_user=Depends(require_role(UserRole.STUDENT.value)),
    db: Session = Depends(get_db),
) -> list[StudentJobApplicationResponse]:
    applications = (
        db.query(StudentJobApplication)
        .filter(StudentJobApplication.student_id == current_user.id)
        .order_by(StudentJobApplication.applied_at.desc())
        .all()
    )
    return [
        StudentJobApplicationResponse(
            id=application.id,
            job_id=application.job_id,
            status=application.status,
            applied_at=application.applied_at,
        )
        for application in applications
    ]
