from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.career import InterviewPracticeSession, StudentProject, StudentResumeEntry
from app.models.recruiter import JobPosting, StudentJobApplication
from app.models.recruiter_extended import (
    RecruiterInterview,
    RecruiterShortlist,
    RecruiterCompanyProfile,
    RecruiterReport,
)
from app.models.user import User, UserRole
from app.services.career.career_service import CareerService
from app.core.database import Base


class RecruiterExtendedService:
    def __init__(self, db: Session):
        self.db = db
        self.career_service = CareerService(db)

    # ─── Interviews ────────────────────────────────────────────────

    def create_interview(self, recruiter_id: int, payload: dict) -> dict:
        interview = RecruiterInterview(
            recruiter_id=recruiter_id,
            candidate_id=payload["candidate_id"],
            job_id=payload["job_id"],
            interviewer=payload["interviewer"],
            slot=payload["slot"],
            mode=payload.get("mode", "Zoom"),
            link=payload.get("link"),
            notes=payload.get("notes"),
        )
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)
        return self._build_interview_response(interview)

    def list_interviews(self, recruiter_id: int, status: str | None = None) -> list[dict]:
        query = self.db.query(RecruiterInterview).filter(RecruiterInterview.recruiter_id == recruiter_id)
        if status:
            query = query.filter(RecruiterInterview.status == status)
        interviews = query.order_by(RecruiterInterview.slot.desc()).all()
        return [self._build_interview_response(i) for i in interviews]

    def get_interview(self, recruiter_id: int, interview_id: int) -> dict | None:
        interview = self.db.query(RecruiterInterview).filter(
            RecruiterInterview.id == interview_id,
            RecruiterInterview.recruiter_id == recruiter_id,
        ).first()
        return self._build_interview_response(interview) if interview else None

    def update_interview(self, recruiter_id: int, interview_id: int, payload: dict) -> dict | None:
        interview = self.db.query(RecruiterInterview).filter(
            RecruiterInterview.id == interview_id,
            RecruiterInterview.recruiter_id == recruiter_id,
        ).first()
        if not interview:
            return None
        for key, value in payload.items():
            if hasattr(interview, key) and value is not None:
                setattr(interview, key, value)
        self.db.commit()
        self.db.refresh(interview)
        return self._build_interview_response(interview)

    def _build_interview_response(self, interview: RecruiterInterview) -> dict:
        candidate = self.db.query(User).filter(User.id == interview.candidate_id).first()
        job = self.db.query(JobPosting).filter(JobPosting.id == interview.job_id).first()
        return {
            "id": interview.id,
            "candidate_id": interview.candidate_id,
            "candidate_name": candidate.full_name if candidate else "",
            "job_id": interview.job_id,
            "job_title": job.title if job else "",
            "interviewer": interview.interviewer,
            "slot": interview.slot,
            "mode": interview.mode,
            "link": interview.link,
            "notes": interview.notes,
            "status": interview.status,
            "created_at": interview.created_at.isoformat() if interview.created_at else None,
            "updated_at": interview.updated_at.isoformat() if interview.updated_at else None,
        }

    # ─── Messages ──────────────────────────────────────────────────

    def send_message(self, sender_id: int, payload: dict) -> dict:
        from app.models.message import Conversation, ConversationParticipant, Message

        recipient_id = payload["recipient_id"]
        conversation = (
            self.db.query(Conversation)
            .join(ConversationParticipant, ConversationParticipant.conversation_id == Conversation.id)
            .filter(
                Conversation.conversation_type == "RECRUITER",
                ConversationParticipant.user_id.in_([sender_id, recipient_id]),
            )
            .group_by(Conversation.id)
            .having(func.count(ConversationParticipant.id) == 2)
            .first()
        )

        if not conversation:
            conversation = Conversation(
                title="Recruiter Chat",
                conversation_type="RECRUITER",
                created_by=sender_id,
            )
            self.db.add(conversation)
            self.db.flush()
            for uid in [sender_id, recipient_id]:
                self.db.add(ConversationParticipant(conversation_id=conversation.id, user_id=uid))
            self.db.flush()

        message = Message(
            conversation_id=conversation.id,
            sender_id=sender_id,
            content=payload["body"],
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        sender = self.db.query(User).filter(User.id == sender_id).first()
        recipient = self.db.query(User).filter(User.id == recipient_id).first()
        return {
            "id": message.id,
            "sender_id": sender_id,
            "sender_name": sender.full_name if sender else "",
            "recipient_id": recipient_id,
            "recipient_name": recipient.full_name if recipient else "",
            "subject": payload.get("subject", ""),
            "body": message.content,
            "is_read": message.is_read,
            "created_at": message.created_at.isoformat() if message.created_at else None,
        }

    def list_conversations(self, user_id: int) -> list[dict]:
        from app.models.message import Conversation, ConversationParticipant, Message

        participant_rows = self.db.query(ConversationParticipant).filter(
            ConversationParticipant.user_id == user_id
        ).all()
        conversation_ids = [p.conversation_id for p in participant_rows]
        conversations = self.db.query(Conversation).filter(
            Conversation.id.in_(conversation_ids),
            Conversation.conversation_type == "RECRUITER",
        ).order_by(Conversation.updated_at.desc()).all()

        results = []
        for conv in conversations:
            last_msg = self.db.query(Message).filter(
                Message.conversation_id == conv.id
            ).order_by(Message.created_at.desc()).first()

            participants = self.db.query(ConversationParticipant).filter(
                ConversationParticipant.conversation_id == conv.id,
                ConversationParticipant.user_id != user_id,
            ).all()

            other_names = []
            for p in participants:
                u = self.db.query(User).filter(User.id == p.user_id).first()
                if u:
                    other_names.append(u.full_name)

            results.append({
                "id": conv.id,
                "participant": ", ".join(other_names),
                "unread": bool(last_msg and not last_msg.is_read and last_msg.sender_id != user_id),
                "message": last_msg.content if last_msg else "",
                "created_at": conv.updated_at.isoformat() if conv.updated_at else None,
            })
        return results

    # ─── Applications ───────────────────────────────────────────────

    def list_applications(self, recruiter_id: int, status: str | None = None) -> list[dict]:
        job_ids = [j.id for j in self.db.query(JobPosting).filter(JobPosting.recruiter_id == recruiter_id).all()]
        if not job_ids:
            return []

        query = self.db.query(StudentJobApplication).filter(StudentJobApplication.job_id.in_(job_ids))
        if status:
            query = query.filter(StudentJobApplication.status == status)

        applications = query.order_by(StudentJobApplication.applied_at.desc()).all()
        return [self._build_application_response(app) for app in applications]

    def update_application_status(self, recruiter_id: int, application_id: int, status: str) -> dict | None:
        job_ids = [j.id for j in self.db.query(JobPosting).filter(JobPosting.recruiter_id == recruiter_id).all()]
        app = self.db.query(StudentJobApplication).filter(
            StudentJobApplication.id == application_id,
            StudentJobApplication.job_id.in_(job_ids),
        ).first()
        if not app:
            return None
        app.status = status
        self.db.commit()
        self.db.refresh(app)
        return self._build_application_response(app)

    def _build_application_response(self, app: StudentJobApplication) -> dict:
        student = self.db.query(User).filter(User.id == app.student_id).first()
        job = self.db.query(JobPosting).filter(JobPosting.id == app.job_id).first()
        fit_score = None
        if student:
            summary = self._build_candidate_summary(student)
            fit_score = summary["fit_score"]
        return {
            "id": app.id,
            "student_id": app.student_id,
            "student_name": student.full_name if student else "",
            "student_email": student.email if student else "",
            "job_id": app.job_id,
            "job_title": job.title if job else "",
            "job_company": job.company if job else "",
            "status": app.status,
            "applied_at": app.applied_at.isoformat() if app.applied_at else None,
            "fit_score": fit_score,
        }

    # ─── Shortlist ─────────────────────────────────────────────────

    def add_to_shortlist(self, recruiter_id: int, payload: dict) -> dict:
        existing = self.db.query(RecruiterShortlist).filter(
            RecruiterShortlist.recruiter_id == recruiter_id,
            RecruiterShortlist.candidate_id == payload["candidate_id"],
            RecruiterShortlist.job_id == payload["job_id"],
        ).first()
        if existing:
            return self._build_shortlist_response(existing)

        shortlist = RecruiterShortlist(
            recruiter_id=recruiter_id,
            candidate_id=payload["candidate_id"],
            job_id=payload["job_id"],
            rating=payload.get("rating"),
            notes=payload.get("notes"),
        )
        self.db.add(shortlist)
        self.db.commit()
        self.db.refresh(shortlist)
        return self._build_shortlist_response(shortlist)

    def list_shortlisted(self, recruiter_id: int) -> list[dict]:
        items = self.db.query(RecruiterShortlist).filter(
            RecruiterShortlist.recruiter_id == recruiter_id
        ).order_by(RecruiterShortlist.created_at.desc()).all()
        return [self._build_shortlist_response(item) for item in items]

    def remove_from_shortlist(self, recruiter_id: int, shortlist_id: int) -> bool:
        item = self.db.query(RecruiterShortlist).filter(
            RecruiterShortlist.id == shortlist_id,
            RecruiterShortlist.recruiter_id == recruiter_id,
        ).first()
        if not item:
            return False
        self.db.delete(item)
        self.db.commit()
        return True

    def _build_shortlist_response(self, item: RecruiterShortlist) -> dict:
        candidate = self.db.query(User).filter(User.id == item.candidate_id).first()
        job = self.db.query(JobPosting).filter(JobPosting.id == item.job_id).first()
        return {
            "id": item.id,
            "candidate_id": item.candidate_id,
            "candidate_name": candidate.full_name if candidate else "",
            "candidate_email": candidate.email if candidate else "",
            "job_id": item.job_id,
            "job_title": job.title if job else "",
            "rating": item.rating,
            "notes": item.notes,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }

    # ─── Company Profile ────────────────────────────────────────────

    def get_company_profile(self, recruiter_id: int) -> dict | None:
        profile = self.db.query(RecruiterCompanyProfile).filter(
            RecruiterCompanyProfile.recruiter_id == recruiter_id
        ).first()
        if not profile:
            return None
        return {
            "id": profile.id,
            "recruiter_id": profile.recruiter_id,
            "company_name": profile.company_name,
            "description": profile.description or "",
            "industry": profile.industry or "",
            "website": profile.website or "",
            "employees": profile.employees or "",
            "location": profile.location or "",
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
        }

    def upsert_company_profile(self, recruiter_id: int, payload: dict) -> dict:
        profile = self.db.query(RecruiterCompanyProfile).filter(
            RecruiterCompanyProfile.recruiter_id == recruiter_id
        ).first()
        if profile:
            for key, value in payload.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
        else:
            profile = RecruiterCompanyProfile(recruiter_id=recruiter_id, **payload)
            self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return {
            "id": profile.id,
            "recruiter_id": profile.recruiter_id,
            "company_name": profile.company_name,
            "description": profile.description or "",
            "industry": profile.industry or "",
            "website": profile.website or "",
            "employees": profile.employees or "",
            "location": profile.location or "",
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
        }

    # ─── Analytics ──────────────────────────────────────────────────

    def get_hiring_analytics(self, recruiter_id: int) -> dict:
        job_ids = [j.id for j in self.db.query(JobPosting).filter(JobPosting.recruiter_id == recruiter_id).all()]
        total_jobs = len(job_ids)
        active_jobs = self.db.query(JobPosting).filter(
            JobPosting.recruiter_id == recruiter_id,
            JobPosting.is_active == True,
        ).count()

        total_apps = self.db.query(StudentJobApplication).filter(
            StudentJobApplication.job_id.in_(job_ids)
        ).count() if job_ids else 0

        total_interviews = self.db.query(RecruiterInterview).filter(
            RecruiterInterview.recruiter_id == recruiter_id
        ).count()

        total_shortlisted = self.db.query(RecruiterShortlist).filter(
            RecruiterShortlist.recruiter_id == recruiter_id
        ).count()

        funnel: dict[str, int] = {"applied": 0, "shortlisted": 0, "interviewed": 0, "offered": 0, "hired": 0}
        if job_ids:
            apps = self.db.query(StudentJobApplication).filter(
                StudentJobApplication.job_id.in_(job_ids)
            ).all()
            for app in apps:
                funnel["applied"] += 1
                status = app.status.upper()
                if status in funnel:
                    funnel[status] += 1

        offer_count = funnel.get("offered", 0)
        hired_count = funnel.get("hired", 0)
        offer_conversion = (hired_count / offer_count * 100) if offer_count > 0 else 0.0

        return {
            "total_jobs": total_jobs,
            "active_jobs": active_jobs,
            "total_applications": total_apps,
            "total_interviews": total_interviews,
            "total_shortlisted": total_shortlisted,
            "offer_conversion_rate": round(offer_conversion, 1),
            "hiring_funnel": funnel,
            "top_skills_demand": self._get_top_skills_demand(recruiter_id),
            "monthly_hires": funnel.get("hired", 0),
        }

    def _get_top_skills_demand(self, recruiter_id: int) -> list[dict]:
        jobs = self.db.query(JobPosting).filter(
            JobPosting.recruiter_id == recruiter_id,
            JobPosting.is_active == True,
        ).all()
        skill_count: dict[str, int] = {}
        for job in jobs:
            for req in (job.requirements_json or []):
                skill_count[req] = skill_count.get(req, 0) + 1
        sorted_skills = sorted(skill_count.items(), key=lambda x: x[1], reverse=True)
        return [{"skill": skill, "count": count} for skill, count in sorted_skills[:10]]

    # ─── Reports ────────────────────────────────────────────────────

    def generate_report(self, recruiter_id: int, report_type: str) -> dict:
        titles = {
            "recruitment": "Recruitment report",
            "hiring": "Hiring report",
            "candidate": "Candidate report",
        }
        data = {}
        if report_type == "recruitment":
            data = self.get_hiring_analytics(recruiter_id)
        elif report_type == "hiring":
            analytics = self.get_hiring_analytics(recruiter_id)
            data = {
                "offer_conversion_rate": analytics["offer_conversion_rate"],
                "hiring_funnel": analytics["hiring_funnel"],
                "monthly_hires": analytics["monthly_hires"],
            }
        elif report_type == "candidate":
            candidates = self.db.query(User).filter(User.role == UserRole.STUDENT).count()
            data = {"total_candidates": candidates}

        report = RecruiterReport(
            recruiter_id=recruiter_id,
            title=titles.get(report_type, f"{report_type} report"),
            description=f"Generated {report_type} report",
            report_type=report_type,
            data=data,
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return {
            "id": report.id,
            "title": report.title,
            "description": report.description,
            "report_type": report.report_type,
            "generated_at": report.generated_at.isoformat() if report.generated_at else None,
            "data": report.data or {},
        }

    def list_reports(self, recruiter_id: int) -> list[dict]:
        reports = self.db.query(RecruiterReport).filter(
            RecruiterReport.recruiter_id == recruiter_id
        ).order_by(RecruiterReport.generated_at.desc()).all()
        return [
            {
                "id": r.id,
                "title": r.title,
                "description": r.description,
                "report_type": r.report_type,
                "generated_at": r.generated_at.isoformat() if r.generated_at else None,
                "data": r.data or {},
            }
            for r in reports
        ]

    # ─── AI Matching / Candidate Ranking ────────────────────────────

    def rank_candidates(self, recruiter_id: int, limit: int = 20) -> list[dict]:
        candidates = self.db.query(User).filter(User.role == UserRole.STUDENT).limit(limit).all()
        best_fit_id = self._find_best_fit_candidate_id(limit)
        ranked = []
        for candidate in candidates:
            summary = self._build_candidate_summary(candidate)
            ranked.append(summary)

        ranked.sort(key=lambda x: x["fit_score"], reverse=True)
        results = []
        for idx, candidate in enumerate(ranked):
            results.append({
                "id": candidate["id"],
                "full_name": candidate["full_name"],
                "email": candidate["email"],
                "fit_score": candidate["fit_score"],
                "readiness_label": candidate["readiness_label"],
                "resume_strength": candidate["resume_strength"],
                "interview_readiness": candidate["interview_readiness"],
                "skills": candidate["skills"],
                "top_role_match": candidate["top_roles"][0]["name"] if candidate.get("top_roles") else "",
                "rank": idx + 1,
                "is_best_fit": candidate["id"] == best_fit_id,
            })
        return results

    def get_ai_match(self, recruiter_id: int, candidate_id: int, job_id: int) -> dict | None:
        candidate = self.db.query(User).filter(User.id == candidate_id, User.role == UserRole.STUDENT).first()
        job = self.db.query(JobPosting).filter(
            JobPosting.id == job_id,
            JobPosting.recruiter_id == recruiter_id,
        ).first()
        if not candidate or not job:
            return None

        summary = self._build_candidate_summary(candidate)
        skills = summary.get("skills", [])
        requirements = job.requirements_json or []

        matched = [s for s in skills if any(r.lower() in s.lower() or s.lower() in r.lower() for r in requirements)]
        gaps = [r for r in requirements if not any(r.lower() in s.lower() or s.lower() in r.lower() for s in skills)]

        match_score = min(100.0, (len(matched) / max(len(requirements), 1)) * 100 * 0.7 + summary["fit_score"] * 0.3)

        return {
            "candidate_id": candidate_id,
            "candidate_name": candidate.full_name,
            "job_id": job_id,
            "job_title": job.title,
            "match_score": round(match_score, 1),
            "match_rationale": f"Matched {len(matched)} of {len(requirements)} required skills with overall fit score of {summary['fit_score']:.1f}.",
            "skill_gaps": gaps,
            "strengths": matched,
            "recommendation": "Advance for review" if match_score >= 60 else "Consider for development",
        }

    # ─── Settings ───────────────────────────────────────────────────

    def get_settings(self, user_id: int) -> dict | None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        return {
            "full_name": user.full_name,
            "email": user.email,
            "notifications": True,
            "theme": "light",
            "language": "English",
        }

    def update_settings(self, user_id: int, payload: dict) -> dict | None:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        if payload.get("full_name"):
            user.full_name = payload["full_name"]
        if payload.get("email"):
            user.email = payload["email"]
        self.db.commit()
        return self.get_settings(user_id)

    # ─── Helpers ────────────────────────────────────────────────────

    def _build_candidate_summary(self, candidate: User) -> dict:
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

        return {
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
            "fit_score": (
                readiness_score * 0.45
                + resume_strength * 0.2
                + project_alignment * 0.15
                + interview_readiness * 0.1
                + (profile.overall_score if profile else 0.0) * 0.1
            ),
        }

    def _find_best_fit_candidate_id(self, limit: int = 20) -> int | None:
        candidates = self.db.query(User).filter(User.role == UserRole.STUDENT).limit(limit).all()
        best_id = None
        best_score = -1.0
        for candidate in candidates:
            summary = self._build_candidate_summary(candidate)
            if summary["fit_score"] > best_score:
                best_score = summary["fit_score"]
                best_id = candidate.id
        return best_id

