from __future__ import annotations

from app.services.dna.config import DNAConfig
from app.services.dna.normalizers import normalize_ratio, normalize_inverse_ratio, normalize_positive_evidence, normalize_lower_is_better


def calculate_debugging_score(features: dict[str, float]) -> dict[str, object]:
    error_recovery_norm = normalize_ratio(features.get("error_recovery_rate"))
    inverse_repeated_error_norm = normalize_inverse_ratio(features.get("repeated_error_rate"))
    failed_attempt_recovery_norm = normalize_positive_evidence(features.get("recoverable_error_sequences", 0))
    recovery_time_efficiency_norm = normalize_lower_is_better(features.get("average_recovery_time_minutes", None), excellent=5.0, poor=30.0)

    contributions = [
        {
            "feature": "error_recovery_rate",
            "raw_value": features.get("error_recovery_rate"),
            "normalized_value": error_recovery_norm,
            "configured_weight": DNAConfig.debugging_weights["error_recovery_rate"],
        },
        {
            "feature": "inverse_repeated_error_rate",
            "raw_value": 1 - features.get("repeated_error_rate", 0.0) if features.get("repeated_error_rate") is not None else None,
            "normalized_value": inverse_repeated_error_norm,
            "configured_weight": DNAConfig.debugging_weights["inverse_repeated_error_rate"],
        },
        {
            "feature": "failed_attempt_recovery",
            "raw_value": features.get("recoverable_error_sequences", 0),
            "normalized_value": failed_attempt_recovery_norm,
            "configured_weight": DNAConfig.debugging_weights["failed_attempt_recovery"],
        },
        {
            "feature": "recovery_time_efficiency",
            "raw_value": features.get("average_recovery_time_minutes"),
            "normalized_value": recovery_time_efficiency_norm,
            "configured_weight": DNAConfig.debugging_weights["recovery_time_efficiency"],
        },
    ]

    total_weight = 0.0
    total_score = 0.0
    for contribution in contributions:
        normalized = contribution["normalized_value"]
        weight = contribution["configured_weight"]
        if normalized is not None:
            total_score += normalized * weight
            total_weight += weight

    score = total_score / total_weight if total_weight > 0 else 0.0
    confidence = min(1.0, total_weight)

    evidence_status = (
        "INSUFFICIENT_DATA"
        if features.get("recoverable_error_sequences", 0) < DNAConfig.min_debugging_recoverable_sequences
        else "SUFFICIENT_DATA"
    )

    return {
        "score": round(score, 2),
        "confidence": round(confidence, 2),
        "evidence_status": evidence_status,
        "explanation": "Debugging performance reflects recovery from errors and reduced repeated mistakes.",
        "contributions": contributions,
    }
