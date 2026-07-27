from __future__ import annotations

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.career import InterviewPracticeSession, StudentProject, StudentResumeEntry
from app.models.recruiter import JobPosting, JobSeniority
from app.models.user import User, UserRole
from app.services.career.career_service import CareerService


class RecruiterService:
    def __init__(self, db: Session):
        self.db = db
        self.career_service = CareerService(db)

    def create_job_posting(self, recruiter_id: int, payload: dict[str, object]) -> JobPosting:
        job = JobPosting(
            recruiter_id=recruiter_id,
            title=payload["title"].strip(),
            company=payload["company"].strip(),
            location=payload["location"].strip(),
            seniority_level=JobSeniority(payload["seniority_level"]),
            description=payload["description"].strip(),
            requirements_json=[req.strip() for req in payload.get("requirements", []) if req.strip()],
            is_active=payload.get("is_active", True),
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def list_job_postings(self, recruiter_id: int) -> list[JobPosting]:
        return (
            self.db.query(JobPosting)
            .filter(JobPosting.recruiter_id == recruiter_id)
            .order_by(JobPosting.created_at.desc())
            .all()
        )

    def search_job_postings(
        self,
        recruiter_id: int,
        query: str | None = None,
        seniority_level: str | None = None,
        location: str | None = None,
        company: str | None = None,
        is_active: bool | None = True,
    ) -> list[JobPosting]:
        job_query = self.db.query(JobPosting).filter(JobPosting.recruiter_id == recruiter_id)

        if is_active is not None:
            job_query = job_query.filter(JobPosting.is_active == is_active)

        if seniority_level:
            job_query = job_query.filter(JobPosting.seniority_level == JobSeniority(seniority_level))

        if location:
            job_query = job_query.filter(JobPosting.location.ilike(f"%{location.strip()}%"))

        if company:
            job_query = job_query.filter(JobPosting.company.ilike(f"%{company.strip()}%"))

        if query and query.strip():
            term = f"%{query.strip()}%"
            job_query = job_query.filter(
                or_(
                    JobPosting.title.ilike(term),
                    JobPosting.company.ilike(term),
                    JobPosting.location.ilike(term),
                    JobPosting.description.ilike(term),
                )
            )

        return job_query.order_by(JobPosting.created_at.desc()).all()

    def get_job_posting(self, recruiter_id: int, job_id: int) -> JobPosting | None:
        return (
            self.db.query(JobPosting)
            .filter(JobPosting.id == job_id, JobPosting.recruiter_id == recruiter_id)
            .first()
        )

    def list_open_job_postings(self, recruiter_id: int) -> list[JobPosting]:
        return (
            self.db.query(JobPosting)
            .filter(JobPosting.recruiter_id == recruiter_id, JobPosting.is_active == True)
            .order_by(JobPosting.created_at.desc())
            .all()
        )

    def list_candidate_profiles(self, limit: int = 10) -> list[User]:
        return (
            self.db.query(User)
            .filter(User.role == UserRole.STUDENT)
            .order_by(User.full_name.asc())
            .limit(limit)
            .all()
        )

    def _build_candidate_summary(self, candidate: User) -> dict[str, object]:
        profile = self.career_service._get_latest_profile(candidate.id)
        student_skills = self.career_service._build_student_skills(candidate.id)
        readiness_score, readiness_label, confidence_label = self.career_service._calculate_readiness(candidate.id)
        resume_strength = self.career_service._calculate_resume_strength(candidate.id, student_skills)
        project_alignment = self.career_service._calculate_project_alignment(candidate.id, student_skills)
        interview_readiness = self.career_service._calculate_interview_readiness(candidate.id, readiness_score)

        role_matches = [
            {
                "id": role.id,
                "name": role.name,
                "seniority_level": role.seniority_level.value,
                "description": role.description,
                "match_score": self.career_service._calculate_role_match_score(role, student_skills, readiness_score),
            }
            for role in self.career_service.get_role_catalog()
        ]
        role_matches.sort(key=lambda item: item["match_score"], reverse=True)

        summary = {
            "id": candidate.id,
            "full_name": candidate.full_name,
            "email": candidate.email,
            "profile_status": "AVAILABLE" if profile else "NOT_GENERATED",
            "overall_score": profile.overall_score if profile else None,
            "overall_confidence": profile.overall_confidence if profile else None,
            "confidence_label": confidence_label,
            "readiness_score": readiness_score,
            "readiness_label": readiness_label,
            "resume_strength": resume_strength,
            "project_alignment": project_alignment,
            "interview_readiness": interview_readiness,
            "skills": sorted(list(student_skills)),
            "top_roles": role_matches[:5],
            "resume_entry_count": self.db.query(StudentResumeEntry).filter(StudentResumeEntry.student_id == candidate.id).count(),
            "project_count": self.db.query(StudentProject).filter(StudentProject.student_id == candidate.id).count(),
            "interview_session_count": self.db.query(InterviewPracticeSession).filter(InterviewPracticeSession.student_id == candidate.id).count(),
        }
        summary["fit_score"] = self._calculate_candidate_fit_score(summary)
        summary["evidence_highlights"] = self._build_evidence_highlights(summary, role_matches[:5])
        summary["signal_summary"] = self._build_signal_summary(summary, role_matches[:5])
        return summary

    def _build_evidence_highlights(self, candidate_summary: dict[str, object], role_matches: list[dict[str, object]]) -> list[str]:
        highlights: list[str] = []
        if candidate_summary.get("readiness_label"):
            highlights.append(f"Readiness is {candidate_summary['readiness_label']} with a score of {candidate_summary['readiness_score']}.")
        if candidate_summary.get("resume_strength") is not None:
            highlights.append(
                f"Resume strength is {candidate_summary['resume_strength']} with {candidate_summary['resume_entry_count']} resume entries."
            )
        if candidate_summary.get("project_alignment") is not None:
            highlights.append(
                f"Project alignment is {candidate_summary['project_alignment']} with {candidate_summary['project_count']} project entries."
            )
        if candidate_summary.get("interview_readiness") is not None:
            highlights.append(
                f"Interview readiness is {candidate_summary['interview_readiness']} and {candidate_summary['interview_session_count']} practice sessions are on record."
            )
        if role_matches:
            top_role = role_matches[0]
            highlights.append(f"The strongest role match is {top_role['name']} with a fit score of {top_role['match_score']:.0f}.")
        return highlights

    def _build_signal_summary(self, candidate_summary: dict[str, object], role_matches: list[dict[str, object]]) -> str:
        if role_matches:
            top_role = role_matches[0]
            return (
                f"This candidate shows {candidate_summary['readiness_label'].lower()} readiness and a strong fit for {top_role['name']}."
            )
        return "This candidate is still being evaluated for hiring readiness and fit."

    def get_candidate_profile_summary(self, candidate_id: int) -> dict[str, object] | None:
        candidate = self.get_candidate_profile(candidate_id)
        if not candidate:
            return None

        summary = self._build_candidate_summary(candidate)
        best_candidate_id = self._find_best_fit_candidate_id(limit=10)
        summary["is_best_fit"] = summary["id"] == best_candidate_id
        return summary

    def _find_best_fit_candidate_id(self, limit: int = 20) -> int | None:
        candidates = self.list_candidate_profiles(limit=limit)
        best_candidate_id = None
        best_score = -1.0

        for candidate in candidates:
            summary = self._build_candidate_summary(candidate)
            if summary["fit_score"] > best_score:
                best_score = summary["fit_score"]
                best_candidate_id = candidate.id

        return best_candidate_id

    def search_candidate_profiles_summary(self, query: str | None = None, limit: int = 10) -> list[dict[str, object]]:
        candidate_query = self.db.query(User).filter(User.role == UserRole.STUDENT)

        if query and query.strip():
            term = f"%{query.strip()}%"
            candidate_query = candidate_query.filter(
                or_(
                    User.full_name.ilike(term),
                    User.email.ilike(term),
                )
            )

        candidates = candidate_query.order_by(User.full_name.asc()).limit(limit).all()
        best_candidate_id = self._find_best_fit_candidate_id(limit=limit)

        summaries = []
        for candidate in candidates:
            summary = self._build_candidate_summary(candidate)
            summary["is_best_fit"] = summary["id"] == best_candidate_id
            summaries.append(summary)

        return summaries

    def get_open_job_counts_by_seniority(self, recruiter_id: int) -> dict[str, int]:
        counts: dict[str, int] = {}
        for job in self.list_open_job_postings(recruiter_id):
            level = job.seniority_level.value
            counts[level] = counts.get(level, 0) + 1
        return counts

    def _calculate_candidate_fit_score(self, candidate_summary: dict[str, object]) -> float:
        return (
            candidate_summary["readiness_score"] * 0.45
            + candidate_summary["resume_strength"] * 0.2
            + candidate_summary["project_alignment"] * 0.15
            + candidate_summary["interview_readiness"] * 0.1
            + (candidate_summary.get("overall_score") or 0.0) * 0.1
        )

    def get_best_fit_candidate(self, limit: int = 20) -> dict[str, object] | None:
        candidates = self.list_candidate_profiles(limit=limit)
        best_candidate = None
        best_score = -1.0

        for candidate in candidates:
            summary = self._build_candidate_summary(candidate)
            if summary["fit_score"] > best_score:
                best_score = summary["fit_score"]
                best_candidate = summary

        if best_candidate:
            best_candidate["is_best_fit"] = True
        return best_candidate

    def search_candidate_profiles(self, query: str | None = None, limit: int = 10) -> list[User]:
        candidate_query = self.db.query(User).filter(User.role == UserRole.STUDENT)

        if query and query.strip():
            term = f"%{query.strip()}%"
            candidate_query = candidate_query.filter(
                or_(
                    User.full_name.ilike(term),
                    User.email.ilike(term),
                )
            )

        return candidate_query.order_by(User.full_name.asc()).limit(limit).all()

    def get_candidate_profile(self, candidate_id: int) -> User | None:
        return (
            self.db.query(User)
            .filter(User.id == candidate_id, User.role == UserRole.STUDENT)
            .first()
        )

    def get_dashboard_data(self, recruiter_id: int) -> dict[str, object]:
        jobs = self.list_open_job_postings(recruiter_id)
        candidates = self.list_candidate_profiles(limit=10)
        return {
            "total_open_jobs": len(jobs),
            "total_candidates": self.db.query(User).filter(User.role == UserRole.STUDENT).count(),
            "job_counts_by_seniority": self.get_open_job_counts_by_seniority(recruiter_id),
            "best_fit_candidate": self.get_best_fit_candidate(limit=10),
            "top_open_job": jobs[0] if jobs else None,
            "recent_jobs": jobs[:5],
            "recent_candidates": candidates,
        }
