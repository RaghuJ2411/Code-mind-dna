from __future__ import annotations

from app.services.dna.config import DNAConfig
from app.services.dna.normalizers import normalize_inverse_ratio, normalize_positive_evidence, normalize_ratio


def calculate_consistency_score(features: dict[str, float]) -> dict[str, object]:
    weekly_consistency_norm = normalize_inverse_ratio(features.get("weekly_consistency_ratio"), good_threshold=0.1, bad_threshold=0.5)
    active_day_regularity_norm = normalize_positive_evidence(features.get("active_days_last_30"), threshold=15, cap=30)
    activity_stability_norm = normalize_ratio(features.get("activity_stability"))
    streak_behavior_norm = normalize_ratio(features.get("streak_behavior"))

    contributions = [
        {
            "feature": "weekly_consistency_ratio",
            "raw_value": features.get("weekly_consistency_ratio"),
            "normalized_value": weekly_consistency_norm,
            "configured_weight": DNAConfig.consistency_weights["weekly_consistency_ratio"],
        },
        {
            "feature": "active_day_regularity",
            "raw_value": features.get("active_days_last_30"),
            "normalized_value": active_day_regularity_norm,
            "configured_weight": DNAConfig.consistency_weights["active_day_regularity"],
        },
        {
            "feature": "activity_stability",
            "raw_value": features.get("activity_stability"),
            "normalized_value": activity_stability_norm,
            "configured_weight": DNAConfig.consistency_weights["activity_stability"],
        },
        {
            "feature": "streak_behavior",
            "raw_value": features.get("streak_behavior"),
            "normalized_value": streak_behavior_norm,
            "configured_weight": DNAConfig.consistency_weights["streak_behavior"],
        },
    ]

    total_weight = 0.0
    total_score = 0.0
    for contribution in contributions:
        total_score += contribution["normalized_value"] * contribution["configured_weight"]
        total_weight += contribution["configured_weight"]

    return {
        "score": round(total_score / total_weight, 2),
        "confidence": round(min(1.0, features.get("active_days_last_30", 0) / 30), 2),
        "evidence_status": "SUFFICIENT_DATA" if features.get("active_days_last_30", 0) >= 7 else "LIMITED_DATA",
        "explanation": "Consistency reflects steady, balanced activity and regular coding weeks.",
        "contributions": contributions,
    }
