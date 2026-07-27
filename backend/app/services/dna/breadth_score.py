from __future__ import annotations

from app.services.dna.config import DNAConfig
from app.services.dna.normalizers import normalize_ratio


def calculate_breadth_score(features: dict[str, float]) -> dict[str, object]:
    topic_breadth_norm = normalize_ratio(features.get("topic_breadth_ratio"))
    unique_topics_solved_norm = normalize_ratio(features.get("unique_topics_solved"))
    difficulty_breadth_norm = normalize_ratio(features.get("difficulty_breadth"))
    cross_topic_balance_norm = normalize_ratio(features.get("cross_topic_success_balance"))

    contributions = [
        {
            "feature": "topic_breadth_ratio",
            "raw_value": features.get("topic_breadth_ratio"),
            "normalized_value": topic_breadth_norm,
            "configured_weight": DNAConfig.breadth_weights["topic_breadth_ratio"],
        },
        {
            "feature": "unique_topics_solved",
            "raw_value": features.get("unique_topics_solved"),
            "normalized_value": unique_topics_solved_norm,
            "configured_weight": DNAConfig.breadth_weights["unique_topics_solved"],
        },
        {
            "feature": "difficulty_breadth",
            "raw_value": features.get("difficulty_breadth"),
            "normalized_value": difficulty_breadth_norm,
            "configured_weight": DNAConfig.breadth_weights["difficulty_breadth"],
        },
        {
            "feature": "cross_topic_success_balance",
            "raw_value": features.get("cross_topic_success_balance"),
            "normalized_value": cross_topic_balance_norm,
            "configured_weight": DNAConfig.breadth_weights["cross_topic_success_balance"],
        },
    ]

    total_weight = sum(c["configured_weight"] for c in contributions)
    total_score = sum(c["normalized_value"] * c["configured_weight"] for c in contributions)

    evidence_count = sum(1 for c in contributions if c["raw_value"] is not None)
    confidence = min(1.0, evidence_count / len(contributions))

    return {
        "score": round(total_score / total_weight, 2),
        "confidence": round(confidence, 2),
        "evidence_status": "SUFFICIENT_DATA" if evidence_count >= 2 else "LIMITED_DATA",
        "explanation": "Breadth reflects topic coverage, balanced difficulty, and success across categories.",
        "contributions": contributions,
    }
