from __future__ import annotations
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.career import (
    CareerRole,
    InterviewPracticeSession,
    StudentProject,
    StudentResumeEntry,
)
from app.models.dna_profile import CodingDNAProfile
from app.services.analytics.behavior_feature_service import BehaviorFeatureService
from app.services.dna import CodingDNAProfileService
from app.services.dna.confidence import confidence_label


class CareerService:
    DEFAULT_ROLES = [
        {
            "name": "Algorithm Developer",
            "seniority_level": "ENTRY",
            "description": "Ideal for problem solvers who excel at algorithms, data structures, and technical reasoning.",
            "required_skills_json": ["ARRAYS", "STRINGS", "SORTING", "SEARCHING"],
            "target_score_min": 60,
            "target_score_max": 100,
        },
        {
            "name": "Backend Engineer",
            "seniority_level": "MID",
            "description": "Focuses on scalable systems, APIs, and backend logic using strong debugging and optimization practices.",
            "required_skills_json": ["HASHING", "TREES", "DYNAMIC_PROGRAMMING", "GRAPHS"],
            "target_score_min": 55,
            "target_score_max": 100,
        },
        {
            "name": "Systems Engineer",
            "seniority_level": "SENIOR",
            "description": "Matches students with deep technical problem-solving strengths in recursion, graphs, and optimization.",
            "required_skills_json": ["TREES", "GRAPHS", "RECURSION", "DYNAMIC_PROGRAMMING"],
            "target_score_min": 70,
            "target_score_max": 100,
        },
    ]

    def __init__(self, db: Session):
        self.db = db
        self.feature_service = BehaviorFeatureService(db)
        self.dna_service = CodingDNAProfileService(db)
        self.ensure_default_roles()

    def ensure_default_roles(self) -> None:
        existing = self.db.query(CareerRole).count()
        if existing > 0:
            return

        for role_data in self.DEFAULT_ROLES:
            self.db.add(CareerRole(**role_data))
        self.db.commit()

    def _get_latest_profile(self, student_id: int) -> CodingDNAProfile | None:
        return self.dna_service.get_latest_profile(student_id)

    def _build_student_skills(self, student_id: int) -> set[str]:
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=90)
        topic_metrics = self.feature_service.calculate_topic_metrics(student_id, start, now)
        skills = {topic_metric["topic"] for topic_metric in topic_metrics if topic_metric["solved"] > 0}

        resume_entries = self.db.query(StudentResumeEntry).filter(StudentResumeEntry.student_id == student_id).all()
        for entry in resume_entries:
            for skill in entry.skills_json or []:
                skills.add(skill.upper())

        project_entries = self.db.query(StudentProject).filter(StudentProject.student_id == student_id).all()
        for project in project_entries:
            for tech in project.technologies_json or []:
                skills.add(tech.upper())

        return skills

    def _calculate_readiness(self, student_id: int) -> tuple[float, str, str]:
        profile = self._get_latest_profile(student_id)
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=30)

        activity_metrics = self.feature_service.calculate_activity_metrics(student_id, start, now)
        consistency = self.feature_service.calculate_consistency_metrics(student_id)
        topic_metrics = self.feature_service.calculate_topic_metrics(student_id, start, now)

        overall_score = profile.overall_score if profile and profile.overall_score is not None else 0.0
        solve_rate_score = activity_metrics.get("solve_rate", 0.0) * 100.0
        consistency_score = min(1.0, consistency.get("active_days_last_30", 0) / 30.0) * 100.0
        topic_breadth = len([topic for topic in topic_metrics if topic["solved"] > 0])
        topic_breadth_score = min(1.0, topic_breadth / max(1, len(topic_metrics))) * 100.0

        readiness_score = round(
            (overall_score * 0.45)
            + (solve_rate_score * 0.2)
            + (consistency_score * 0.2)
            + (topic_breadth_score * 0.15),
            2,
        )

        if readiness_score >= 75:
            readiness_label = "Highly ready"
        elif readiness_score >= 50:
            readiness_label = "Building readiness"
        else:
            readiness_label = "Needs more practice"

        confidence_label = confidence_label(profile.overall_confidence or 0.0).value if profile and profile.overall_confidence is not None else "INSUFFICIENT_EVIDENCE"
        return readiness_score, readiness_label, confidence_label

    def _calculate_role_match_score(self, role: CareerRole, student_skills: set[str], readiness_score: float) -> float:
        required_skills = {skill.upper() for skill in (role.required_skills_json or [])}
        matches = len(required_skills & student_skills)
        skill_match_ratio = matches / max(1, len(required_skills))
        return round((readiness_score * 0.55) + (skill_match_ratio * 45.0), 2)

    def _calculate_resume_strength(self, student_id: int, student_skills: set[str]) -> float:
        entries = self.db.query(StudentResumeEntry).filter(StudentResumeEntry.student_id == student_id).all()
        if not entries:
            return 10.0

        skill_matches = sum(len({skill.upper() for skill in entry.skills_json or []} & student_skills) for entry in entries)
        score = min(100.0, 20.0 + len(entries) * 20.0 + skill_matches * 5.0)
        return round(score, 2)

    def _calculate_project_alignment(self, student_id: int, student_skills: set[str]) -> float:
        projects = self.db.query(StudentProject).filter(StudentProject.student_id == student_id).all()
        if not projects:
            return 15.0

        technology_matches = sum(len({tech.upper() for tech in project.technologies_json or []} & student_skills) for project in projects)
        score = min(100.0, 25.0 + len(projects) * 20.0 + technology_matches * 7.0)
        return round(score, 2)

    def _calculate_interview_readiness(self, student_id: int, readiness_score: float) -> float:
        sessions = self.db.query(InterviewPracticeSession).filter(InterviewPracticeSession.student_id == student_id).count()
        return round(min(100.0, max(20.0, readiness_score * 0.6 + sessions * 8.0)), 2)

    def get_role_catalog(self) -> list[CareerRole]:
        return self.db.query(CareerRole).order_by(CareerRole.name.asc()).all()

    def get_role(self, role_id: int) -> CareerRole | None:
        return self.db.query(CareerRole).filter(CareerRole.id == role_id).first()

    def build_career_overview(self, student_id: int) -> dict[str, object]:
        readiness_score, readiness_label, confidence_label = self._calculate_readiness(student_id)
        student_skills = self._build_student_skills(student_id)
        roles = self.get_role_catalog()

        top_roles = [
            {
                "id": role.id,
                "name": role.name,
                "seniority_level": role.seniority_level.value,
                "description": role.description,
                "match_score": self._calculate_role_match_score(role, student_skills, readiness_score),
            }
            for role in roles
        ]
        top_roles.sort(key=lambda role: role["match_score"], reverse=True)

        return {
            "readiness_score": readiness_score,
            "readiness_label": readiness_label,
            "confidence_label": confidence_label,
            "resume_strength": self._calculate_resume_strength(student_id, student_skills),
            "project_alignment": self._calculate_project_alignment(student_id, student_skills),
            "interview_readiness": self._calculate_interview_readiness(student_id, readiness_score),
            "top_roles": top_roles[:3],
            "recommended_actions": self._build_recommended_actions(student_id, student_skills, readiness_score),
            "resume_entry_count": self.db.query(StudentResumeEntry).filter(StudentResumeEntry.student_id == student_id).count(),
            "project_count": self.db.query(StudentProject).filter(StudentProject.student_id == student_id).count(),
            "interview_session_count": self.db.query(InterviewPracticeSession).filter(InterviewPracticeSession.student_id == student_id).count(),
        }

    def _build_recommended_actions(self, student_id: int, student_skills: set[str], readiness_score: float) -> list[str]:
        actions = []
        if self.db.query(StudentResumeEntry).filter(StudentResumeEntry.student_id == student_id).count() == 0:
            actions.append("Add a resume entry that highlights your strongest technical work.")
        if self.db.query(StudentProject).filter(StudentProject.student_id == student_id).count() == 0:
            actions.append("Document a project with technologies and outcomes to strengthen your portfolio.")
        if self.db.query(InterviewPracticeSession).filter(InterviewPracticeSession.student_id == student_id).count() == 0:
            actions.append("Practice an interview response for a target role.")
        if readiness_score < 60:
            actions.append("Solve more problems in your weakest topic areas to boost career readiness.")
        return actions

    def list_resume_entries(self, student_id: int) -> list[StudentResumeEntry]:
        return (
            self.db.query(StudentResumeEntry)
            .filter(StudentResumeEntry.student_id == student_id)
            .order_by(StudentResumeEntry.created_at.desc())
            .all()
        )

    def create_resume_entry(self, student_id: int, payload: dict[str, object]) -> StudentResumeEntry:
        entry = StudentResumeEntry(
            student_id=student_id,
            section=payload["section"],
            title=payload["title"],
            content=payload["content"],
            skills_json=[skill.upper() for skill in payload.get("skills", [])],
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def list_projects(self, student_id: int) -> list[StudentProject]:
        return (
            self.db.query(StudentProject)
            .filter(StudentProject.student_id == student_id)
            .order_by(StudentProject.created_at.desc())
            .all()
        )

    def create_project(self, student_id: int, payload: dict[str, object]) -> StudentProject:
        project = StudentProject(
            student_id=student_id,
            title=payload["title"],
            description=payload["description"],
            technologies_json=[tech.upper() for tech in payload.get("technologies", [])],
            outcome=payload.get("outcome"),
            project_url=payload.get("project_url"),
        )
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def list_interview_sessions(self, student_id: int, limit: int = 20) -> list[InterviewPracticeSession]:
        return (
            self.db.query(InterviewPracticeSession)
            .filter(InterviewPracticeSession.student_id == student_id)
            .order_by(InterviewPracticeSession.created_at.desc())
            .limit(limit)
            .all()
        )

    def practice_interview(self, student_id: int, payload: dict[str, object]) -> InterviewPracticeSession:
        readiness_score, _, _ = self._calculate_readiness(student_id)
        role_name = payload.get("role_name")
        question = payload["question"].strip()
        answer = payload["answer"].strip()
        feedback_score = min(100, max(20, round(readiness_score * 0.55 + len(answer) * 0.15 + len(question) * 0.1)))

        if feedback_score >= 75:
            feedback_text = "Your answer is strong. Consider adding more specific examples from your projects to make it even clearer."
        elif feedback_score >= 50:
            feedback_text = "Your response is on the right track. Add more detail around the steps you took and the impact you delivered."
        else:
            feedback_text = "Your answer can improve by focusing on a clear problem, the solution you built, and the result it achieved."

        session = InterviewPracticeSession(
            student_id=student_id,
            role_name=role_name,
            question=question,
            answer=answer,
            feedback_score=feedback_score,
            feedback_text=feedback_text,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session
