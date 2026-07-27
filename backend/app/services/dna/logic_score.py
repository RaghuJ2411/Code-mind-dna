from __future__ import annotations

from app.services.dna.config import DNAConfig
from app.services.dna.normalizers import normalize_ratio, normalize_delta


def calculate_logic_score(features: dict[str, float]) -> dict[str, object]:
    feature_values = {
        "solve_rate": normalize_ratio(features.get("solve_rate")),
        "first_attempt_acceptance_rate": normalize_ratio(features.get("first_attempt_acceptance_rate")),
        "average_attempts_to_solve": normalize_delta(-features.get("average_attempts_to_solve", 0.0), negative_bound=-3.0, positive_bound=-1.0),
        "medium_problem_performance": normalize_ratio(features.get("medium_solve_rate")),
        "hard_problem_performance": normalize_ratio(features.get("hard_solve_rate")),
    }

    contributions = []
    available_weight = 0.0
    total_score = 0.0

    for feature, weight in DNAConfig.logic_weights.items():
        normalized = feature_values.get(feature)
        available = normalized is not None and normalized >= 0.0
        if available:
            total_score += normalized * weight
            available_weight += weight
        contributions.append(
            {
                "feature": feature,
                "raw_value": features.get(feature),
                "normalized_value": normalized,
                "configured_weight": weight,
            }
        )

    effective_score = total_score / available_weight if available_weight > 0 else 0.0
    return {
        "score": round(effective_score, 2),
        "confidence": round(min(1.0, available_weight), 2),
        "evidence_status": "SUFFICIENT_DATA" if available_weight >= 0.8 else "LIMITED_DATA",
        "explanation": "Weighted logic performance based on accuracy and problem difficulty.",
        "contributions": contributions,
    }
