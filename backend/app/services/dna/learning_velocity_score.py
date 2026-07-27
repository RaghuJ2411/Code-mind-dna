from __future__ import annotations

from app.services.dna.config import DNAConfig
from app.services.dna.normalizers import normalize_delta, normalize_ratio


def calculate_learning_velocity_score(features: dict[str, float]) -> dict[str, object]:
    solve_rate_improvement_norm = normalize_delta(features.get("solve_rate_delta"), negative_bound=-0.2, positive_bound=0.2)
    attempt_efficiency_improvement_norm = normalize_delta(features.get("attempt_efficiency_delta"), negative_bound=-2.0, positive_bound=0.0)
    solve_time_improvement_norm = normalize_delta(features.get("solve_time_improvement_minutes"), negative_bound=-30.0, positive_bound=0.0)
    difficulty_progression_norm = normalize_delta(features.get("difficulty_progression_delta"), negative_bound=-1.0, positive_bound=1.0)

    contributions = [
        {
            "feature": "solve_rate_improvement",
            "raw_value": features.get("solve_rate_delta"),
            "normalized_value": solve_rate_improvement_norm,
            "configured_weight": DNAConfig.learning_velocity_weights["solve_rate_improvement"],
        },
        {
            "feature": "attempt_efficiency_improvement",
            "raw_value": features.get("attempt_efficiency_delta"),
            "normalized_value": attempt_efficiency_improvement_norm,
            "configured_weight": DNAConfig.learning_velocity_weights["attempt_efficiency_improvement"],
        },
        {
            "feature": "solve_time_improvement",
            "raw_value": features.get("solve_time_improvement_minutes"),
            "normalized_value": solve_time_improvement_norm,
            "configured_weight": DNAConfig.learning_velocity_weights["solve_time_improvement"],
        },
        {
            "feature": "difficulty_progression",
            "raw_value": features.get("difficulty_progression_delta"),
            "normalized_value": difficulty_progression_norm,
            "configured_weight": DNAConfig.learning_velocity_weights["difficulty_progression"],
        },
    ]

    total_weight = sum(c["configured_weight"] for c in contributions)
    total_score = sum(c["normalized_value"] * c["configured_weight"] for c in contributions)

    evidence_count = sum(1 for c in contributions if c["raw_value"] is not None)
    confidence = min(1.0, evidence_count / len(contributions))

    return {
        "score": round(total_score / total_weight, 2),
        "confidence": round(confidence, 2),
        "evidence_status": "SUFFICIENT_DATA" if evidence_count >= 3 else "LIMITED_DATA",
        "explanation": "Learning velocity reflects improvement in accuracy, efficiency, and difficulty over time.",
        "contributions": contributions,
    }
