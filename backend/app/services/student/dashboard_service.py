from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.dna_profile import CodingDNAProfile
from app.models.execution import Submission, SubmissionVerdict
from app.models.problem import DifficultyLevel, Problem, TopicType
from app.models.user import UserRole
from app.services.analytics.behavior_feature_service import BehaviorFeatureService
from app.models.student_goal import StudentGoal
from app.models.student_recommendation import StudentRecommendation
from app.services.ai.usage_summary_service import AIUsageSummaryService
from app.services.dna import CodingDNAProfileService
from app.services.dna.confidence import confidence_label


class StudentDashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.feature_service = BehaviorFeatureService(db)
        self.dna_service = CodingDNAProfileService(db)
        self.ai_usage_service = AIUsageSummaryService(db)

    def _get_latest_profile(self, student_id: int) -> CodingDNAProfile | None:
        return self.dna_service.get_latest_profile(student_id)

    def _get_evidence_status(self, student_id: int, profile: CodingDNAProfile | None) -> str:
        if profile:
            return profile.evidence_status
        return self.feature_service.build_behavior_profile(student_id, date_range_days=60)["evidence_status"]

    def _build_coding_dna_summary(self, profile: CodingDNAProfile | None) -> dict[str, object]:
        if not profile:
            return {
                "overall_score": None,
                "overall_confidence": None,
                "confidence_label": "INSUFFICIENT_EVIDENCE",
                "calculated_at": None,
                "strongest_dimension": None,
                "development_dimension": None,
            }

        dimension_payloads, dimensions, _ = self.dna_service._build_dimension_payloads(profile.feature_snapshot_json)
        strongest = max(
            [d for d in dimension_payloads if d["score"] is not None],
            key=lambda x: x["score"],
            default=None,
        )
        development = min(
            [d for d in dimension_payloads if d["score"] is not None],
            key=lambda x: x["score"],
            default=None,
        )

        return {
            "overall_score": profile.overall_score,
            "overall_confidence": profile.overall_confidence,
            "confidence_label": confidence_label(profile.overall_confidence or 0.0).value if profile.overall_score is not None else "INSUFFICIENT_EVIDENCE",
            "calculated_at": profile.calculated_at,
            "strongest_dimension": {
                "name": strongest["name"],
                "score": strongest["score"],
            }
            if strongest
            else None,
            "development_dimension": {
                "name": development["name"],
                "score": development["score"],
            }
            if development
            else None,
        }

    def _build_activity_summary(self, student_id: int) -> dict[str, object]:
        now = datetime.now(timezone.utc)
        last_30 = now - timedelta(days=30)
        last_30 = now - timedelta(days=30)

        recent_activity = self.feature_service.calculate_activity_metrics(student_id, last_30, now)
        consistency = self.feature_service.calculate_consistency_metrics(student_id)

        problems_attempted = recent_activity["problems_attempted"]
        problems_solved = recent_activity["problems_solved"]
        solve_rate = self.feature_service.calculate_success_metrics(student_id, last_30, now)["solve_rate"]

        return {
            "problems_attempted": problems_attempted,
            "problems_solved": problems_solved,
            "solve_rate": solve_rate,
            "active_days_last_7": consistency["active_days_last_7"],
            "active_days_last_30": consistency["active_days_last_30"],
            "current_streak": consistency["current_streak"],
        }

    def _build_recent_progress(self, student_id: int) -> dict[str, object]:
        progression = self.feature_service.calculate_progression_metrics(student_id)
        profile = self._get_latest_profile(student_id)

        overall_delta = 0.0
        if profile and profile.overall_score is not None:
            previous = self.db.query(CodingDNAProfile)
            previous_profile = (
                previous.filter(CodingDNAProfile.student_id == student_id)
                .order_by(CodingDNAProfile.calculated_at.desc())
                .offset(1)
                .limit(1)
                .first()
            )

            if previous_profile and previous_profile.overall_score is not None:
                overall_delta = (profile.overall_score - previous_profile.overall_score)

        return {
            "overall_dna_delta": round(overall_delta, 2),
            "solve_rate_delta": round(progression["solve_rate_delta"] * 100, 2),
            "attempt_efficiency_delta": round(progression["attempt_efficiency_delta"], 2),
            "difficulty_progression_delta": round(progression["difficulty_progression_delta"], 2),
        }

    def _build_practice_summary(self, student_id: int) -> dict[str, object]:
        recommendations_count = (
            self.db.query(StudentRecommendation)
            .filter(
                StudentRecommendation.student_id == student_id,
                StudentRecommendation.status == "PENDING",
            )
            .count()
        )
        active_goals_count = (
            self.db.query(StudentGoal)
            .filter(
                StudentGoal.student_id == student_id,
                StudentGoal.status == "ACTIVE",
            )
            .count()
        )

        return {
            "pending_recommendations": recommendations_count,
            "pending_mentor_tasks": 0,
            "active_goals": active_goals_count,
        }

    def _build_ai_usage_summary(self, student_id: int) -> dict[str, object]:
        summary = self.ai_usage_service.get_daily_usage(student_id)
        return {
            "tasks": summary["tasks"],
            "limits": summary["limits"],
        }

    def _accepted_problem_ids(self, student_id: int) -> set[int]:
        rows = (
            self.db.query(Submission.problem_id)
            .filter(
                Submission.student_id == student_id,
                Submission.verdict == SubmissionVerdict.ACCEPTED,
            )
            .distinct()
            .all()
        )
        return {row[0] for row in rows}

    def _suitable_difficulty(self, student_id: int) -> str:
        now = datetime.now(timezone.utc)
        metrics = self.feature_service.calculate_difficulty_metrics(student_id, now - timedelta(days=30), now)

        if metrics["medium"]["attempted"] >= 2 and metrics["medium"]["solve_rate"] >= 0.65:
            return DifficultyLevel.HARD.value
        if metrics["easy"]["attempted"] >= 2 and metrics["easy"]["solve_rate"] >= 0.7:
            return DifficultyLevel.MEDIUM.value
        return DifficultyLevel.EASY.value

    def _find_problem_candidate(
        self,
        student_id: int,
        solved_problem_ids: set[int],
        *,
        topic: str | None = None,
        difficulty: str | None = None,
        excluded_problem_ids: set[int] | None = None,
    ) -> Problem | None:
        query = self.db.query(Problem).filter(Problem.is_active.is_(True))

        excluded_problem_ids = excluded_problem_ids or set()
        blocked_ids = solved_problem_ids | excluded_problem_ids
        if blocked_ids:
            query = query.filter(Problem.id.notin_(blocked_ids))

        if topic:
            query = query.filter(Problem.topic == TopicType(topic))
        if difficulty:
            query = query.filter(Problem.difficulty == DifficultyLevel(difficulty))

        return query.order_by(Problem.id.asc()).first()

    def build_practice_queue(self, student_id: int, limit: int = 8) -> list[dict[str, object]]:
        queue: list[dict[str, object]] = []
        solved_problem_ids = self._accepted_problem_ids(student_id)
        queued_problem_ids: set[int] = set()

        recommendations = (
            self.db.query(StudentRecommendation)
            .filter(
                StudentRecommendation.student_id == student_id,
                StudentRecommendation.status.in_(["PENDING", "IN_PROGRESS"]),
            )
            .order_by(StudentRecommendation.generated_at.desc())
            .limit(limit)
            .all()
        )

        for recommendation in recommendations:
            action = recommendation.action_json or {}
            candidate = self._find_problem_candidate(
                student_id,
                solved_problem_ids,
                topic=action.get("topic"),
                difficulty=action.get("difficulty"),
                excluded_problem_ids=queued_problem_ids,
            )
            if candidate:
                queued_problem_ids.add(candidate.id)

            queue.append(
                {
                    "source": "RECOMMENDATION",
                    "title": recommendation.title,
                    "reason": recommendation.reason,
                    "recommendation_id": recommendation.id,
                    "problem_id": candidate.id if candidate else None,
                    "problem_slug": candidate.slug if candidate else None,
                    "difficulty": candidate.difficulty.value if candidate else action.get("difficulty"),
                    "topic": candidate.topic.value if candidate else action.get("topic"),
                }
            )

            if len(queue) >= limit:
                return queue[:limit]

        now = datetime.now(timezone.utc)
        weak_topics = [
            topic_metric
            for topic_metric in self.feature_service.calculate_topic_metrics(student_id, now - timedelta(days=30), now)
            if topic_metric["classification"] == "WEAK_CANDIDATE"
        ]
        for topic_metric in weak_topics:
            candidate = self._find_problem_candidate(
                student_id,
                solved_problem_ids,
                topic=topic_metric["topic"],
                difficulty=DifficultyLevel.EASY.value,
                excluded_problem_ids=queued_problem_ids,
            )
            if not candidate:
                continue
            queued_problem_ids.add(candidate.id)
            queue.append(
                {
                    "source": "WEAK_TOPIC",
                    "title": f"Practice {topic_metric['topic']}",
                    "reason": f"Recent {topic_metric['topic']} solve rate is {topic_metric['solve_rate']:.0%}.",
                    "recommendation_id": None,
                    "problem_id": candidate.id,
                    "problem_slug": candidate.slug,
                    "difficulty": candidate.difficulty.value,
                    "topic": candidate.topic.value,
                }
            )
            if len(queue) >= limit:
                return queue[:limit]

        suitable_difficulty = self._suitable_difficulty(student_id)
        candidate = self._find_problem_candidate(
            student_id,
            solved_problem_ids,
            difficulty=suitable_difficulty,
            excluded_problem_ids=queued_problem_ids,
        )
        if candidate and len(queue) < limit:
            queued_problem_ids.add(candidate.id)
            queue.append(
                {
                    "source": "SUGGESTED_DIFFICULTY",
                    "title": f"Keep momentum with a {candidate.difficulty.value.lower()} problem",
                    "reason": "This difficulty matches your recent performance trend.",
                    "recommendation_id": None,
                    "problem_id": candidate.id,
                    "problem_slug": candidate.slug,
                    "difficulty": candidate.difficulty.value,
                    "topic": candidate.topic.value,
                }
            )

        if len(queue) < limit:
            fallback_problems = (
                self.db.query(Problem)
                .filter(Problem.is_active.is_(True))
                .order_by(Problem.id.asc())
                .all()
            )
            for problem in fallback_problems:
                if problem.id in solved_problem_ids or problem.id in queued_problem_ids:
                    continue
                queue.append(
                    {
                        "source": "UNSOLVED_PROBLEM",
                        "title": f"Try {problem.title}",
                        "reason": "You have not solved this active problem yet.",
                        "recommendation_id": None,
                        "problem_id": problem.id,
                        "problem_slug": problem.slug,
                        "difficulty": problem.difficulty.value,
                        "topic": problem.topic.value,
                    }
                )
                if len(queue) >= limit:
                    break

        return queue[:limit]

    def build_recent_activity(self, student_id: int, limit: int = 10) -> list[dict[str, object]]:
        timeline: list[dict[str, object]] = []

        solved_submissions = (
            self.db.query(Submission)
            .join(Problem, Submission.problem_id == Problem.id)
            .filter(
                Submission.student_id == student_id,
                Submission.verdict == SubmissionVerdict.ACCEPTED,
            )
            .order_by(Submission.created_at.desc())
            .limit(limit)
            .all()
        )
        for submission in solved_submissions:
            timeline.append(
                {
                    "event_type": "PROBLEM_SOLVED",
                    "title": f"Solved {submission.problem.title}",
                    "description": f"Accepted in {submission.attempt_number} attempt(s).",
                    "occurred_at": submission.created_at,
                    "metadata": {
                        "problem_id": submission.problem_id,
                        "problem_slug": submission.problem.slug,
                        "difficulty": submission.problem.difficulty.value,
                        "topic": submission.problem.topic.value,
                    },
                }
            )

        dna_updates = (
            self.db.query(CodingDNAProfile)
            .filter(CodingDNAProfile.student_id == student_id)
            .order_by(CodingDNAProfile.calculated_at.desc())
            .limit(limit)
            .all()
        )
        for profile in dna_updates:
            timeline.append(
                {
                    "event_type": "DNA_UPDATED",
                    "title": "Coding DNA updated",
                    "description": "Your latest behavior evidence was converted into a refreshed DNA profile.",
                    "occurred_at": profile.calculated_at,
                    "metadata": {
                        "overall_score": profile.overall_score,
                        "overall_confidence": profile.overall_confidence,
                        "evidence_status": profile.evidence_status,
                    },
                }
            )

        completed_recommendations = (
            self.db.query(StudentRecommendation)
            .filter(
                StudentRecommendation.student_id == student_id,
                StudentRecommendation.completed_at.isnot(None),
            )
            .order_by(StudentRecommendation.completed_at.desc())
            .limit(limit)
            .all()
        )
        for recommendation in completed_recommendations:
            timeline.append(
                {
                    "event_type": "RECOMMENDATION_COMPLETED",
                    "title": recommendation.title,
                    "description": recommendation.reason,
                    "occurred_at": recommendation.completed_at,
                    "metadata": {
                        "recommendation_id": recommendation.id,
                        "recommendation_type": recommendation.recommendation_type,
                    },
                }
            )

        achieved_goals = (
            self.db.query(StudentGoal)
            .filter(
                StudentGoal.student_id == student_id,
                StudentGoal.status == "ACHIEVED",
            )
            .order_by(StudentGoal.updated_at.desc())
            .limit(limit)
            .all()
        )
        for goal in achieved_goals:
            timeline.append(
                {
                    "event_type": "GOAL_ACHIEVED",
                    "title": goal.title,
                    "description": f"Reached target {goal.current_value}/{goal.target_value}.",
                    "occurred_at": goal.updated_at,
                    "metadata": {"goal_id": goal.id, "goal_type": goal.goal_type},
                }
            )

        timeline.sort(key=lambda item: item["occurred_at"], reverse=True)
        return timeline[:limit]

    def build_overview(self, student: object) -> dict[str, object]:
        profile = self._get_latest_profile(student.id)
        evidence_status = self._get_evidence_status(student.id, profile)
        return {
            "profile": {
                "full_name": student.full_name,
                "profile_status": "AVAILABLE" if profile else "NOT_GENERATED",
            },
            "evidence_status": evidence_status,
            "coding_dna": self._build_coding_dna_summary(profile),
            "activity": self._build_activity_summary(student.id),
            "recent_progress": self._build_recent_progress(student.id),
            "practice": self._build_practice_summary(student.id),
            "ai_usage": self._build_ai_usage_summary(student.id),
        }
