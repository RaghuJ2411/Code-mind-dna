from __future__ import annotations

from datetime import datetime, timedelta, timezone

from app.services.dna.config import DNAConfig


def temporal_weight_for_date(dt: datetime) -> float:
    if dt is None:
        return 0.0

    now = datetime.now(timezone.utc)
    age_days = (now - dt).days

    if age_days <= DNAConfig.temporal_windows["recent"]:
        return DNAConfig.temporal_windows["decay_30"]
    if age_days <= DNAConfig.temporal_windows["recent"] * 2:
        return DNAConfig.temporal_windows["decay_60"]
    if age_days <= DNAConfig.temporal_windows["recent"] * 3:
        return DNAConfig.temporal_windows["decay_90"]
    return DNAConfig.temporal_windows["decay_older"]


def weighted_average(values: list[float], weights: list[float]) -> float:
    if not values or not weights or len(values) != len(weights):
        return 0.0
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0
    return sum(v * w for v, w in zip(values, weights)) / total_weight
