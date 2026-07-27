from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models.execution import Submission, SubmissionVerdict
from app.models.problem import Problem, TopicType
from app.models.student_recommendation import StudentRecommendation
from app.models.user import UserRole
from app.services.analytics.behavior_feature_service import BehaviorFeatureService
from app.services.recommendations.config import (
    MAX_ACTIVE_RECOMMENDATIONS,
    RECOMMENDATION_DUPLICATE_WINDOW_DAYS,
    RECOMMENDATION_MIN_PROBLEMS_PER_TOPIC,
    RECOMMENDATION_WEAK_SOLVE_RATE_THRESHOLD,
)
from app.services.recommendations.rules import (
    build_debug_error_pattern_recommendation,
    build_improve_consistency_recommendation,
    build_increase_difficulty_recommendation,
    build_topic_practice_recommendation,
)


class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.feature_service = BehaviorFeatureService(db)

    def _recent_topic_performance(self, student_id: int) -> list[dict[str, object]]:
        now = datetime.now(timezone.utc)
        thirty_days = now - timedelta(days=30)
        submissions = (
            self.db.query(Submission)
            .join(Problem)
            .filter(Submission.student_id == student_id, Submission.created_at >= thirty_days)
            .all()
        )

        topics = {}
        for submission in submissions:
            if not submission.problem:
                continue
            topic = submission.problem.topic.value
            topics.setdefault(topic, []).append(submission)

        performance = []
        for topic, subs in topics.items():
            attempted = len(set(s.problem_id for s in subs))
            solved = len(set(s.problem_id for s in subs if s.verdict == SubmissionVerdict.ACCEPTED))
            if attempted < RECOMMENDATION_MIN_PROBLEMS_PER_TOPIC:
                continue
            solve_rate = solved / attempted if attempted else 0.0
            performance.append({"topic": topic, "attempted": attempted, "solve_rate": solve_rate})

        return performance

    def _recent_recommendations(self, student_id: int) -> list[StudentRecommendation]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=RECOMMENDATION_DUPLICATE_WINDOW_DAYS)
        return (
            self.db.query(StudentRecommendation)
            .filter(
                StudentRecommendation.student_id == student_id,
                StudentRecommendation.generated_at >= cutoff,
                StudentRecommendation.status.in_(["PENDING", "IN_PROGRESS"]),
            )
            .all()
        )

    def _has_recent_recommendation_type(self, student_id: int, recommendation_type: str) -> bool:
        cutoff = datetime.now(timezone.utc) - timedelta(days=RECOMMENDATION_DUPLICATE_WINDOW_DAYS)
        return (
            self.db.query(StudentRecommendation)
            .filter(
                StudentRecommendation.student_id == student_id,
                StudentRecommendation.generated_at >= cutoff,
                StudentRecommendation.recommendation_type == recommendation_type,
                StudentRecommendation.status.in_(["PENDING", "IN_PROGRESS"]),
            )
            .first()
            is not None
        )

    def _create_recommendation(self, student_id: int, payload: dict[str, object]) -> StudentRecommendation:
        recommendation = StudentRecommendation(
            student_id=student_id,
            recommendation_type=payload["recommendation_type"],
            priority=payload["priority"],
            title=payload["title"],
            reason=payload["reason"],
            action_json=payload["action_json"],
            source_snapshot_json={},
            status="PENDING",
            generated_at=datetime.now(timezone.utc),
        )
        self.db.add(recommendation)
        self.db.commit()
        self.db.refresh(recommendation)
        return recommendation

    def generate_student_recommendations(self, student_id: int) -> list[StudentRecommendation]:
        existing = self._recent_recommendations(student_id)
        if len(existing) >= MAX_ACTIVE_RECOMMENDATIONS:
            return existing

        recommendations = []
        topic_perf = self._recent_topic_performance(student_id)
        weak_topics = [p for p in topic_perf if p["solve_rate"] < RECOMMENDATION_WEAK_SOLVE_RATE_THRESHOLD]

        for topic in weak_topics[:2]:
            payload = build_topic_practice_recommendation(topic["topic"], topic["solve_rate"], topic["attempted"])
            if not self._has_recent_recommendation_type(student_id, payload["recommendation_type"]):
                recommendations.append(self._create_recommendation(student_id, payload))
            if len(recommendations) >= MAX_ACTIVE_RECOMMENDATIONS:
                break

        if len(recommendations) < MAX_ACTIVE_RECOMMENDATIONS:
            payload = build_improve_consistency_recommendation()
            if not self._has_recent_recommendation_type(student_id, payload["recommendation_type"]):
                recommendations.append(self._create_recommendation(student_id, payload))

        if len(recommendations) < MAX_ACTIVE_RECOMMENDATIONS:
            payload = build_increase_difficulty_recommendation()
            if not self._has_recent_recommendation_type(student_id, payload["recommendation_type"]):
                recommendations.append(self._create_recommendation(student_id, payload))

        return recommendations[:MAX_ACTIVE_RECOMMENDATIONS]

    def list_student_recommendations(self, student_id: int) -> list[StudentRecommendation]:
        return (
            self.db.query(StudentRecommendation)
            .filter(StudentRecommendation.student_id == student_id)
            .order_by(StudentRecommendation.generated_at.desc())
            .limit(MAX_ACTIVE_RECOMMENDATIONS)
            .all()
        )

    def update_recommendation_status(self, student_id: int, recommendation_id: int, status: str) -> StudentRecommendation | None:
        recommendation = (
            self.db.query(StudentRecommendation)
            .filter(StudentRecommendation.id == recommendation_id, StudentRecommendation.student_id == student_id)
            .first()
        )
        if not recommendation:
            return None

        recommendation.status = status
        if status == "IN_PROGRESS":
            recommendation.started_at = datetime.now(timezone.utc)
        elif status == "COMPLETED":
            recommendation.completed_at = datetime.now(timezone.utc)
        elif status == "DISMISSED":
            recommendation.dismissed_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(recommendation)
        return recommendation
