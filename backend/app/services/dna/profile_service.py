from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.models.dna_profile import CodingDNAProfile
from app.models.problem import TopicType
from app.models.user import User, UserRole
from app.services.analytics.behavior_feature_service import BehaviorFeatureService
from app.services.dna.confidence import confidence_label
from app.services.dna.config import (
    DNAConfig,
    DNA_SCORING_VERSION,
    DimensionName,
    EvidenceStatus,
)
from app.services.dna.debugging_score import calculate_debugging_score
from app.services.dna.explanation_service import build_dimension_explanation
from app.services.dna.learning_velocity_score import calculate_learning_velocity_score
from app.services.dna.logic_score import calculate_logic_score
from app.services.dna.optimization_score import calculate_optimization_score
from app.services.dna.overall_score import calculate_overall_score
from app.services.dna.consistency_score import calculate_consistency_score
from app.services.dna.breadth_score import calculate_breadth_score


class CodingDNAProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.feature_service = BehaviorFeatureService(db)

    def _load_student(self, student_id: int):
        return self.db.query(User).filter(User.id == student_id, User.role == UserRole.STUDENT).first()

    def _build_feature_snapshot(self, student_id: int) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=60)

        success = self.feature_service.calculate_success_metrics(student_id, start_date, now)
        debugging = self.feature_service.calculate_debugging_metrics(student_id, start_date, now)
        difficulty = self.feature_service.calculate_difficulty_metrics(student_id, start_date, now)
        consistency = self.feature_service.calculate_consistency_metrics(student_id)
        progression = self.feature_service.calculate_progression_metrics(student_id)
        topics = self.feature_service.calculate_topic_metrics(student_id, start_date, now)
        optimization = self.feature_service.calculate_optimization_metrics(student_id, start_date, now)

        unique_topics_solved = len([t for t in topics if t["solved"] > 0])
        difficulty_breadth = len([d for d in [difficulty["easy"], difficulty["medium"], difficulty["hard"]] if d["attempted"] > 0]) / 3.0
        cross_topic_success_balance = (sum(t["solve_rate"] for t in topics) / len(topics)) if topics else 0.0
        topic_breadth_ratio = len(topics) / max(1, len(list(TopicType)))

        return {
            **success,
            **debugging,
            **{
                "medium_solve_rate": difficulty["medium"]["solve_rate"],
                "hard_solve_rate": difficulty["hard"]["solve_rate"],
                "difficulty_progression_delta": progression["difficulty_progression_delta"],
                "attempt_efficiency_delta": progression["attempt_efficiency_delta"],
                "solve_rate_delta": progression["solve_rate_delta"],
                "solve_time_improvement_minutes": progression["solve_time_improvement_minutes"],
            },
            **{
                "unique_topics_solved": unique_topics_solved,
                "topic_breadth_ratio": topic_breadth_ratio,
                "difficulty_breadth": difficulty_breadth,
                "cross_topic_success_balance": cross_topic_success_balance,
            },
            **optimization,
            **consistency,
        }

    def _classify_dimension(self, score: float | None, confidence: float | None) -> str:
        if score is None or confidence is None or confidence < DNAConfig.min_confidence_for_classification:
            return "INSUFFICIENT_CONFIDENCE"
        if score >= 80.0:
            return "STRENGTH"
        if score >= 65.0:
            return "DEVELOPING_STRENGTH"
        if score >= 45.0:
            return "DEVELOPING"
        return "DEVELOPMENT_AREA"

    def _build_dimension_payload(self, dimension: DimensionName, result: dict[str, object], features: dict[str, Any]) -> dict[str, object]:
        return {
            "name": dimension.value,
            "score": result.get("score"),
            "confidence": result.get("confidence"),
            "classification": self._classify_dimension(result.get("score"), result.get("confidence")),
            "evidence_status": result.get("evidence_status", EvidenceStatus.INSUFFICIENT_DATA),
            "explanation": build_dimension_explanation(dimension.value, features),
            "contributions": result.get("contributions", []),
        }

    def _build_dimension_payloads(self, features: dict[str, Any]) -> tuple[list[dict[str, object]], dict[DimensionName, dict[str, object]], dict[str, object]]:
        logic = calculate_logic_score(features)
        debugging = calculate_debugging_score({
            **features,
            "recoverable_error_sequences": features.get("recoverable_sequences", 0),
            "average_recovery_time_minutes": features.get("average_recovery_time_minutes"),
        })
        optimization = calculate_optimization_score(features)
        consistency = calculate_consistency_score(features)
        learning_velocity = calculate_learning_velocity_score(features)
        breadth = calculate_breadth_score(features)

        dimensions = {
            DimensionName.LOGIC: logic,
            DimensionName.DEBUGGING: debugging,
            DimensionName.OPTIMIZATION: optimization,
            DimensionName.CONSISTENCY: consistency,
            DimensionName.LEARNING_VELOCITY: learning_velocity,
            DimensionName.PROBLEM_SOLVING_BREADTH: breadth,
        }

        payloads = [
            self._build_dimension_payload(dimension, result, features)
            for dimension, result in dimensions.items()
        ]

        return payloads, dimensions, calculate_overall_score(dimensions)

    def get_latest_profile(self, student_id: int) -> CodingDNAProfile | None:
        return (
            self.db.query(CodingDNAProfile)
            .filter(CodingDNAProfile.student_id == student_id)
            .order_by(CodingDNAProfile.calculated_at.desc())
            .first()
        )

    def get_profile_history(self, student_id: int, limit: int = 10) -> list[CodingDNAProfile]:
        return (
            self.db.query(CodingDNAProfile)
            .filter(CodingDNAProfile.student_id == student_id)
            .order_by(CodingDNAProfile.calculated_at.desc())
            .limit(limit)
            .all()
        )

    def recalculate_profile(self, student_id: int) -> CodingDNAProfile:
        result = self.calculate_coding_dna(student_id)
        return result["profile"]

    def build_profile_record_response(self, profile: CodingDNAProfile) -> dict[str, object]:
        features = profile.feature_snapshot_json or {}
        dimension_payloads, _, _ = self._build_dimension_payloads(features)
        return {
            "profile_status": "AVAILABLE",
            "overall_score": profile.overall_score,
            "overall_confidence": profile.overall_confidence,
            "confidence_label": confidence_label(profile.overall_confidence or 0.0).value,
            "scoring_version": profile.scoring_version,
            "calculated_at": profile.calculated_at,
            "dimensions": dimension_payloads,
        }

    def calculate_coding_dna(self, student_id: int) -> dict[str, object]:
        student = self._load_student(student_id)
        if not student:
            raise ValueError("Student not found or invalid role")

        features = self._build_feature_snapshot(student_id)
        dimension_payloads, dimensions, overall = self._build_dimension_payloads(features)

        if features.get("total_submissions", 0) == 0:
            evidence_status = EvidenceStatus.NO_DATA
        elif any(
            dim.get("evidence_status") != EvidenceStatus.SUFFICIENT_DATA.value
            for dim in dimensions.values()
        ):
            evidence_status = EvidenceStatus.LIMITED_DATA
        else:
            evidence_status = EvidenceStatus.SUFFICIENT_DATA

        profile = CodingDNAProfile(
            student_id=student_id,
            overall_score=overall["overall_score"],
            overall_confidence=overall["overall_confidence"],
            logic_score=dimensions[DimensionName.LOGIC]["score"],
            logic_confidence=dimensions[DimensionName.LOGIC]["confidence"],
            debugging_score=dimensions[DimensionName.DEBUGGING]["score"],
            debugging_confidence=dimensions[DimensionName.DEBUGGING]["confidence"],
            optimization_score=dimensions[DimensionName.OPTIMIZATION]["score"],
            optimization_confidence=dimensions[DimensionName.OPTIMIZATION]["confidence"],
            consistency_score=dimensions[DimensionName.CONSISTENCY]["score"],
            consistency_confidence=dimensions[DimensionName.CONSISTENCY]["confidence"],
            learning_velocity_score=dimensions[DimensionName.LEARNING_VELOCITY]["score"],
            learning_velocity_confidence=dimensions[DimensionName.LEARNING_VELOCITY]["confidence"],
            breadth_score=dimensions[DimensionName.PROBLEM_SOLVING_BREADTH]["score"],
            breadth_confidence=dimensions[DimensionName.PROBLEM_SOLVING_BREADTH]["confidence"],
            evidence_status=evidence_status.value,
            scoring_version=DNA_SCORING_VERSION,
            feature_snapshot_json=features,
            explanation_snapshot_json={
                k.value: v.get("explanation") for k, v in {
                    DimensionName.LOGIC: dimensions[DimensionName.LOGIC],
                    DimensionName.DEBUGGING: dimensions[DimensionName.DEBUGGING],
                    DimensionName.OPTIMIZATION: dimensions[DimensionName.OPTIMIZATION],
                    DimensionName.CONSISTENCY: dimensions[DimensionName.CONSISTENCY],
                    DimensionName.LEARNING_VELOCITY: dimensions[DimensionName.LEARNING_VELOCITY],
                    DimensionName.PROBLEM_SOLVING_BREADTH: dimensions[DimensionName.PROBLEM_SOLVING_BREADTH],
                }.items()
            },
            calculated_at=datetime.now(timezone.utc),
        )

        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)

        return {
            "profile": profile,
            "dimensions": dimension_payloads,
            "overall": overall,
        }
