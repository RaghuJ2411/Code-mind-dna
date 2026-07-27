"""
AI-Powered Career Intelligence Service

Leverages the existing AI provider infrastructure (Mock/OpenAI) to provide:
- Skill gap analysis (DNA profile vs career role requirements)
- Career path prediction
- Resume content parsing and enrichment
- AI-generated interview feedback
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.career import CareerRole, InterviewPracticeSession
from app.models.dna_profile import CodingDNAProfile
from app.models.user import User
from app.services.ai.provider_factory import get_provider
from app.services.ai.prompt_registry import PROMPT_REGISTRY
from app.services.ai.usage_service import record_ai_request
from app.services.analytics.behavior_feature_service import BehaviorFeatureService
from app.services.dna.profile_service import CodingDNAProfileService
from app.services.dna.config import DNAConfig, DimensionName


class CareerAIService:
    """AI-powered career intelligence service."""

    # Prompt templates for AI career analysis
    SKILL_GAP_SYSTEM_PROMPT = """You are a senior technical career coach. Analyze the student's coding DNA profile against the requirements of a target career role.

Given the student's skill profile and the role's requirements, provide structured JSON:
- overall_match_percentage: float (0-100) - how well the student currently matches
- gaps: list of objects with {skill, current_proficiency, required_proficiency, gap, priority, description}
- strengths: list of string strengths
- recommendations: list of actionable recommendations
- estimated_improvement_time: string estimate (e.g. "3-6 months")
- ai_insight: string with personalized insight

Evaluate based on: solve rate, topic mastery, difficulty progression, consistency, debugging ability, and problem-solving breadth."""

    CAREER_PREDICTION_SYSTEM_PROMPT = """You are a career path strategist. Given a student's complete coding DNA profile and activity metrics, predict their optimal career path.

Provide structured JSON:
- primary_path: {path_name, confidence, steps: [{role_name, seniority_level, match_score, time_to_achieve, skills_to_develop, description}], ai_rationale}
- alternative_paths: list of alternative path objects
- overall_readiness_score: float
- confidence_label: string
- ai_summary: string summary

Consider: overall DNA scores across all 6 dimensions, topic mastery, consistency, learning velocity, and progression trends."""

    RESUME_PARSE_SYSTEM_PROMPT = """You are a professional resume reviewer and career advisor. Analyze the provided resume content and extract structured information.

Provide structured JSON:
- parsed_entries: list of {section, title, content, skills}
- extracted_skills: list of all skills mentioned
- suggested_roles: list of career roles that match this profile
- experience_years: float or null
- education_level: string or null
- ai_summary: string summary of the resume"""

    INTERVIEW_FEEDBACK_SYSTEM_PROMPT = """You are an expert technical interviewer. Review the candidate's interview response and provide detailed feedback.

Provide structured JSON:
- overall_score: float (0-100)
- strengths: list of string strengths
- improvements: list of string areas to improve
- content_quality: string assessment
- communication_clarity: string assessment
- technical_accuracy: string assessment
- sample_answer: string with a strong example answer
- suggested_followups: list of follow-up questions
- ai_feedback: string with personalized feedback"""

    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.current_user = current_user
        self.provider = get_provider()
        self.feature_service = BehaviorFeatureService(db)
        self.dna_service = CodingDNAProfileService(db)

    def _get_latest_profile(self) -> CodingDNAProfile | None:
        return (
            self.db.query(CodingDNAProfile)
            .filter(CodingDNAProfile.student_id == self.current_user.id)
            .order_by(CodingDNAProfile.calculated_at.desc())
            .first()
        )

    def _build_student_context(self, profile: CodingDNAProfile | None) -> dict[str, Any]:
        """Build a comprehensive context dict of the student's profile for AI analysis."""
        now = datetime.now(timezone.utc)
        start_30 = now - timedelta(days=30)
        start_60 = now - timedelta(days=60)

        # Metrics from behavior feature service
        success = self.feature_service.calculate_success_metrics(self.current_user.id, start_60, now)
        debugging = self.feature_service.calculate_debugging_metrics(self.current_user.id, start_60, now)
        difficulty = self.feature_service.calculate_difficulty_metrics(self.current_user.id, start_60, now)
        consistency = self.feature_service.calculate_consistency_metrics(self.current_user.id)
        progression = self.feature_service.calculate_progression_metrics(self.current_user.id)
        topics = self.feature_service.calculate_topic_metrics(self.current_user.id, start_60, now)
        activity = self.feature_service.calculate_activity_metrics(self.current_user.id, start_30, now)

        context: dict[str, Any] = {
            "overall_dna": {
                "overall_score": profile.overall_score if profile else None,
                "overall_confidence": profile.overall_confidence if profile else None,
                "logic_score": profile.logic_score if profile else None,
                "debugging_score": profile.debugging_score if profile else None,
                "optimization_score": profile.optimization_score if profile else None,
                "consistency_score": profile.consistency_score if profile else None,
                "learning_velocity_score": profile.learning_velocity_score if profile else None,
                "breadth_score": profile.breadth_score if profile else None,
                "evidence_status": profile.evidence_status if profile else "NO_DATA",
            },
            "success_metrics": success,
            "debugging_metrics": debugging,
            "difficulty_metrics": difficulty,
            "consistency_metrics": consistency,
            "progression_metrics": progression,
            "topic_metrics": topics,
            "activity_metrics": activity,
        }
        return context

    def analyze_skill_gap(self, role_id: int, include_recommendations: bool = True) -> dict[str, Any]:
        """Analyze skill gaps between the student's DNA profile and a target career role."""
        role = self.db.query(CareerRole).filter(CareerRole.id == role_id).first()
        if not role:
            raise ValueError(f"Career role with id {role_id} not found")

        profile = self._get_latest_profile()
        student_context = self._build_student_context(profile)

        context = {
            "student": student_context,
            "target_role": {
                "name": role.name,
                "seniority_level": role.seniority_level.value,
                "description": role.description,
                "required_skills": role.required_skills_json or [],
                "target_score_min": role.target_score_min,
                "target_score_max": role.target_score_max,
            },
            "include_recommendations": include_recommendations,
        }

        # Use AI provider for analysis
        provider_resp = self.provider.generate_structured(
            task_type="SKILL_GAP",
            system_prompt=self.SKILL_GAP_SYSTEM_PROMPT,
            context=context,
            response_schema=None,
            temperature=0.3,
        )

        result = provider_resp.get("result", {})
        meta = provider_resp.get("meta", {})

        # Record AI usage
        record_ai_request(
            self.db,
            self.current_user.id,
            "SKILL_GAP",
            meta.get("provider", "mock"),
            meta.get("model", "mock"),
            "v1",
            "SUCCESS",
            latency_ms=meta.get("latency_ms"),
        )

        return {
            "role_name": role.name,
            "role_seniority": role.seniority_level.value,
            "overall_match_percentage": result.get("overall_match_percentage", 50.0),
            "gaps": result.get("gaps", []),
            "strengths": result.get("strengths", []),
            "recommendations": result.get("recommendations", []),
            "estimated_improvement_time": result.get("estimated_improvement_time"),
            "ai_insight": result.get("ai_insight"),
            "generated_at": datetime.now(timezone.utc),
        }

    def predict_career_paths(self, include_alternative_paths: bool = True) -> dict[str, Any]:
        """Predict optimal career paths based on the student's DNA profile."""
        profile = self._get_latest_profile()
        student_context = self._build_student_context(profile)

        # Get available career roles
        roles = self.db.query(CareerRole).order_by(CareerRole.name.asc()).all()
        role_data = [
            {
                "id": role.id,
                "name": role.name,
                "seniority_level": role.seniority_level.value,
                "description": role.description,
                "required_skills": role.required_skills_json or [],
                "target_score_min": role.target_score_min,
                "target_score_max": role.target_score_max,
            }
            for role in roles
        ]

        context = {
            "student": student_context,
            "available_roles": role_data,
            "include_alternative_paths": include_alternative_paths,
        }

        # Use AI provider for prediction
        provider_resp = self.provider.generate_structured(
            task_type="CAREER_PREDICTION",
            system_prompt=self.CAREER_PREDICTION_SYSTEM_PROMPT,
            context=context,
            response_schema=None,
            temperature=0.3,
        )

        result = provider_resp.get("result", {})
        meta = provider_resp.get("meta", {})

        # Record AI usage
        record_ai_request(
            self.db,
            self.current_user.id,
            "CAREER_PREDICTION",
            meta.get("provider", "mock"),
            meta.get("model", "mock"),
            "v1",
            "SUCCESS",
            latency_ms=meta.get("latency_ms"),
        )

        return {
            "primary_path": result.get("primary_path"),
            "alternative_paths": result.get("alternative_paths", []),
            "overall_readiness_score": result.get("overall_readiness_score", 50.0),
            "confidence_label": result.get("confidence_label"),
            "ai_summary": result.get("ai_summary"),
            "generated_at": datetime.now(timezone.utc),
        }

    def parse_resume_content(self, resume_content: str, target_role: str | None = None) -> dict[str, Any]:
        """Parse resume content using AI to extract structured data."""
        context = {
            "resume_content": resume_content,
            "target_role": target_role,
        }

        provider_resp = self.provider.generate_structured(
            task_type="RESUME_PARSE",
            system_prompt=self.RESUME_PARSE_SYSTEM_PROMPT,
            context=context,
            response_schema=None,
            temperature=0.2,
        )

        result = provider_resp.get("result", {})
        meta = provider_resp.get("meta", {})

        # Record AI usage
        record_ai_request(
            self.db,
            self.current_user.id,
            "RESUME_PARSE",
            meta.get("provider", "mock"),
            meta.get("model", "mock"),
            "v1",
            "SUCCESS",
            latency_ms=meta.get("latency_ms"),
        )

        return {
            "parsed_entries": result.get("parsed_entries", []),
            "extracted_skills": result.get("extracted_skills", []),
            "suggested_roles": result.get("suggested_roles", []),
            "experience_years": result.get("experience_years"),
            "education_level": result.get("education_level"),
            "ai_summary": result.get("ai_summary"),
        }

    def generate_interview_feedback(
        self, question: str, answer: str, role_name: str | None = None, seniority_level: str | None = None
    ) -> dict[str, Any]:
        """Generate AI-powered interview feedback."""
        context = {
            "question": question,
            "answer": answer,
            "role_name": role_name,
            "seniority_level": seniority_level,
        }

        provider_resp = self.provider.generate_structured(
            task_type="INTERVIEW_FEEDBACK",
            system_prompt=self.INTERVIEW_FEEDBACK_SYSTEM_PROMPT,
            context=context,
            response_schema=None,
            temperature=0.3,
        )

        result = provider_resp.get("result", {})
        meta = provider_resp.get("meta", {})

        # Record AI usage
        record_ai_request(
            self.db,
            self.current_user.id,
            "INTERVIEW_FEEDBACK",
            meta.get("provider", "mock"),
            meta.get("model", "mock"),
            "v1",
            "SUCCESS",
            latency_ms=meta.get("latency_ms"),
        )

        return {
            "overall_score": result.get("overall_score", 50.0),
            "strengths": result.get("strengths", []),
            "improvements": result.get("improvements", []),
            "content_quality": result.get("content_quality"),
            "communication_clarity": result.get("communication_clarity"),
            "technical_accuracy": result.get("technical_accuracy"),
            "sample_answer": result.get("sample_answer"),
            "suggested_followups": result.get("suggested_followups", []),
            "ai_feedback": result.get("ai_feedback"),
            "generated_at": datetime.now(timezone.utc),
        }

