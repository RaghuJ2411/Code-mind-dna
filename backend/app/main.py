import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router
from app.api.dna import router as dna_router
from app.api.execution import router as execution_router
from app.api.goals import router as goals_router
from app.api.mentor_alerts import router as mentor_alerts_router
from app.api.admin import router as admin_router
from app.api.problems import admin_router as problems_admin_router, router as problems_router
from app.api.recommendations import router as recommendations_router
from app.api.routes import router as protected_router
from app.api.mentor_students import router as mentor_students_router
from app.api.mentor_career_reviews import router as mentor_career_reviews_router
from app.api.mentor_sessions import router as mentor_sessions_router
from app.api.mentor_assignments import router as mentor_assignments_router
from app.api.mentor_resources import router as mentor_resources_router
from app.api.mentor_notifications import router as mentor_notifications_router
from app.api.mentor_analytics import router as mentor_analytics_router
from app.api.mentor_reports import router as mentor_reports_router
from app.api.mentor_intelligence import router as mentor_intelligence_router
from app.api.mentor_messages import router as mentor_messages_router
from app.api.mentor_profile import router as mentor_profile_router
from app.api.recruiter import router as recruiter_router
from app.api.recruiter_interviews import router as recruiter_interviews_router
from app.api.recruiter_applications import router as recruiter_applications_router
from app.api.recruiter_shortlisted import router as recruiter_shortlisted_router
from app.api.recruiter_messages import router as recruiter_messages_router
from app.api.recruiter_company import router as recruiter_company_router
from app.api.recruiter_analytics import router as recruiter_analytics_router
from app.api.recruiter_reports import router as recruiter_reports_router
from app.api.recruiter_matching import router as recruiter_matching_router
from app.api.recruiter_settings import router as recruiter_settings_router
from app.api.admin_system import router as admin_system_router
from app.api.admin_analytics import router as admin_analytics_router
from app.api.admin_database import router as admin_database_router
from app.api.admin_ai_monitoring import router as admin_ai_monitoring_router
from app.api.admin_reports import router as admin_reports_router
from app.api.admin_settings import router as admin_settings_router
from app.api.admin_permissions import router as admin_permissions_router
from app.api.student import router as student_router
from app.api.student_ai import router as student_ai_router
from app.api.student_ai_extra import router as student_ai_extra_router
from app.api.student_career import router as student_career_router
from app.api.student_learning import router as student_learning_router
from app.api.student_assessments import router as student_assessments_router
from app.api.student_achievements import router as student_achievements_router
from app.api.student_messages import router as student_messages_router
from app.api.student_career_roadmap import router as student_career_roadmap_router
from app.api.student_ai_mentor import router as student_ai_mentor_router
from app.api.student_progress import router as student_progress_router
from app.api.student_ai_career import router as student_ai_career_router
from app.api.student_settings_api import router as student_settings_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.exceptions import http_exception_handler
from app.core.rate_limit import RateLimitMiddleware
from app.core.audit import AuditLogMiddleware
from app.core.middleware import (
    SecurityHeadersMiddleware,
    RequestBodySizeMiddleware,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
)
from app.core.logging import setup_logging
from app.core.security import hash_password
from app.models.audit_log import AuditLog
from app.models.user import User, UserRole
from app.models.analytics import StudentDailyAnalytics, StudentWeeklyAnalytics
from app.models.career import CareerRole, InterviewPracticeSession, StudentProject, StudentResumeEntry
from app.models.dna_profile import CodingDNAProfile
from app.models.execution import CodingEvent, CodingSession, Submission
from app.models.problem import CodeDraft, Problem, TestCase
from app.models.recruiter import JobPosting
from app.models.recruiter_extended import RecruiterInterview, RecruiterShortlist, RecruiterCompanyProfile, RecruiterReport
from app.models.student_goal import StudentGoal
from app.models.student_recommendation import StudentRecommendation

# Setup structured logging
setup_logging()
logger = logging.getLogger("codemind.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup validation
    production_warnings = settings.validate_production()
    for warning in production_warnings:
        logger.warning(f"Production configuration issue: {warning}")

    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)

# Middleware order matters - outermost first
app.add_middleware(RequestIDMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestBodySizeMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list if settings.cors_origin_list else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_middleware(RateLimitMiddleware, limit=8, window_seconds=30)

try:
    Base.metadata.create_all(bind=engine)
except Exception as exc:
    logger.error(f"Failed to create database tables: {exc}")
    pass


def ensure_demo_users() -> None:
    from sqlalchemy.orm import Session

    with Session(bind=engine) as session:
        demo_users = [
            {"full_name": "Admin User", "email": "admin@example.com", "password": "Admin123!", "role": UserRole.ADMIN},
            {"full_name": "Mentor User", "email": "mentor@example.com", "password": "Mentor123!", "role": UserRole.MENTOR},
            {"full_name": "Student User", "email": "student@example.com", "password": "Student123!", "role": UserRole.STUDENT},
        ]

        for payload in demo_users:
            existing = session.query(User).filter(User.email == payload["email"]).first()
            if existing:
                continue
            session.add(
                User(
                    full_name=payload["full_name"],
                    email=payload["email"],
                    password_hash=hash_password(payload["password"]),
                    role=payload["role"],
                )
            )

        session.commit()


ensure_demo_users()

app.include_router(auth_router, prefix="/api")
app.include_router(protected_router, prefix="/api")
app.include_router(problems_router, prefix="/api")
app.include_router(problems_admin_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(admin_system_router, prefix="/api")
app.include_router(admin_analytics_router, prefix="/api")
app.include_router(admin_database_router, prefix="/api")
app.include_router(admin_ai_monitoring_router, prefix="/api")
app.include_router(admin_reports_router, prefix="/api")
app.include_router(admin_settings_router, prefix="/api")
app.include_router(admin_permissions_router, prefix="/api")
app.include_router(execution_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(dna_router, prefix="/api")
app.include_router(recommendations_router, prefix="/api")
app.include_router(goals_router, prefix="/api")
app.include_router(mentor_alerts_router, prefix="/api")
app.include_router(mentor_students_router, prefix="/api")
app.include_router(mentor_career_reviews_router, prefix="/api")
app.include_router(mentor_sessions_router, prefix="/api")
app.include_router(mentor_assignments_router, prefix="/api")
app.include_router(mentor_resources_router, prefix="/api")
app.include_router(mentor_notifications_router, prefix="/api")
app.include_router(mentor_analytics_router, prefix="/api")
app.include_router(mentor_reports_router, prefix="/api")
app.include_router(mentor_intelligence_router, prefix="/api")
app.include_router(mentor_messages_router, prefix="/api")
app.include_router(mentor_profile_router, prefix="/api")
app.include_router(recruiter_router, prefix="/api")
app.include_router(recruiter_interviews_router, prefix="/api")
app.include_router(recruiter_applications_router, prefix="/api")
app.include_router(recruiter_shortlisted_router, prefix="/api")
app.include_router(recruiter_messages_router, prefix="/api")
app.include_router(recruiter_company_router, prefix="/api")
app.include_router(recruiter_analytics_router, prefix="/api")
app.include_router(recruiter_reports_router, prefix="/api")
app.include_router(recruiter_matching_router, prefix="/api")
app.include_router(recruiter_settings_router, prefix="/api")
app.include_router(student_router, prefix="/api")
app.include_router(student_ai_router, prefix="/api")
app.include_router(student_ai_extra_router, prefix="/api")
app.include_router(student_career_router, prefix="/api")
app.include_router(student_learning_router, prefix="/api")
app.include_router(student_assessments_router, prefix="/api")
app.include_router(student_achievements_router, prefix="/api")
app.include_router(student_messages_router, prefix="/api")
app.include_router(student_career_roadmap_router, prefix="/api")
app.include_router(student_ai_mentor_router, prefix="/api")
app.include_router(student_progress_router, prefix="/api")
app.include_router(student_settings_router, prefix="/api")
app.include_router(student_ai_career_router, prefix="/api")

app.add_middleware(AuditLogMiddleware)


@app.get("/")
def root():
    return {
        "status": "success",
        "message": "CodeMind DNA Backend is Running 🚀",
        "docs": "/docs",
        "health": "/api/health",
        "version": "1.0.0"
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": settings.app_name}


@app.get("/api/health/live")
def health_live():
    return {"status": "live"}


@app.get("/api/health/ready")
def health_ready():
    db_status = "connected"
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        session.execute(__import__("sqlalchemy").text("SELECT 1"))
        session.close()
    except Exception:
        db_status = "disconnected"
    return {"status": "ready", "database": db_status}


@app.get("/api/health/deep")
def health_deep():
    """Deep health check returning detailed service status."""
    checks = {
        "app": {"status": "ok", "name": settings.app_name},
        "database": {"status": "unknown"},
        "ai_service": {"status": "unknown"},
    }
    try:
        from app.core.database import SessionLocal
        session = SessionLocal()
        session.execute(__import__("sqlalchemy").text("SELECT 1"))
        session.close()
        checks["database"] = {"status": "ok"}
    except Exception as e:
        checks["database"] = {"status": "error", "detail": str(e)}

    if settings.ai_enabled:
        checks["ai_service"]["status"] = "configured"
    else:
        checks["ai_service"]["status"] = "disabled"

    return checks
