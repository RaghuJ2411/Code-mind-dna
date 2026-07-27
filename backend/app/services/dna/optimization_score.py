from __future__ import annotations

from app.services.dna.config import DNAConfig
from app.services.dna.normalizers import normalize_ratio, normalize_lower_is_better


def calculate_optimization_score(features: dict[str, float]) -> dict[str, object]:
    runtime_improvement_norm = normalize_ratio(features.get("runtime_improvement"))
    memory_improvement_norm = normalize_ratio(features.get("memory_improvement"))
    post_acceptance_refinement_norm = normalize_ratio(features.get("post_acceptance_refinement"))
    execution_efficiency_stability_norm = normalize_ratio(features.get("execution_efficiency_stability"))

    comparable_pairs = features.get("optimization_comparable_pairs", 0)
    if comparable_pairs < DNAConfig.min_optimization_evidence:
        return {
            "score": None,
            "confidence": 0.0,
            "evidence_status": "INSUFFICIENT_DATA",
            "explanation": "Not enough optimization evidence available yet.",
            "contributions": [],
        }

    contributions = [
        {
            "feature": "runtime_improvement",
            "raw_value": features.get("runtime_improvement"),
            "normalized_value": runtime_improvement_norm,
            "configured_weight": DNAConfig.optimization_weights["runtime_improvement"],
        },
        {
            "feature": "memory_improvement",
            "raw_value": features.get("memory_improvement"),
            "normalized_value": memory_improvement_norm,
            "configured_weight": DNAConfig.optimization_weights["memory_improvement"],
        },
        {
            "feature": "post_acceptance_refinement",
            "raw_value": features.get("post_acceptance_refinement"),
            "normalized_value": post_acceptance_refinement_norm,
            "configured_weight": DNAConfig.optimization_weights["post_acceptance_refinement"],
        },
        {
            "feature": "execution_efficiency_stability",
            "raw_value": features.get("execution_efficiency_stability"),
            "normalized_value": execution_efficiency_stability_norm,
            "configured_weight": DNAConfig.optimization_weights["execution_efficiency_stability"],
        },
    ]

    total_weight = 0.0
    total_score = 0.0
    for contribution in contributions:
        normalized = contribution["normalized_value"]
        weight = contribution["configured_weight"]
        total_score += normalized * weight
        total_weight += weight

    return {
        "score": round(total_score / total_weight, 2),
        "confidence": round(min(1.0, comparable_pairs / DNAConfig.min_optimization_evidence), 2),
        "evidence_status": "SUFFICIENT_DATA",
        "explanation": "Optimization reflects consistent runtime and memory improvements after accepted solutions.",
        "contributions": contributions,
    }
