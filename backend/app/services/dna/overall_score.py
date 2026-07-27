from __future__ import annotations

from app.services.dna.config import DNAConfig, DimensionName, DNA_SCORING_VERSION


def calculate_overall_score(dimensions: dict[DimensionName, dict[str, object]]) -> dict[str, object]:
    total_weight = 0.0
    weighted_score = 0.0
    contributions = []

    for dimension, weight in DNAConfig.overall_dimension_weights.items():
        dimension_entry = dimensions.get(dimension)
        if not dimension_entry or dimension_entry.get("score") is None:
            continue

        score = dimension_entry["score"]
        effective_weight = weight
        weighted_score += score * effective_weight
        total_weight += effective_weight
        contributions.append(
            {
                "dimension": dimension.value,
                "score": score,
                "configured_weight": weight,
                "effective_weight": effective_weight,
            }
        )

    overall_score = weighted_score / total_weight if total_weight > 0 else 0.0
    overall_confidence = (
        sum(d.get("confidence", 0.0) for d in dimensions.values() if d.get("score") is not None)
        / max(1, len([d for d in dimensions.values() if d.get("score") is not None]))
    )

    return {
        "overall_score": round(overall_score, 2),
        "overall_confidence": round(min(1.0, overall_confidence), 2),
        "scoring_version": DNA_SCORING_VERSION,
        "dimension_contributions": contributions,
    }
