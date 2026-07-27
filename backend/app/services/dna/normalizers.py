from __future__ import annotations

from app.services.dna.config import DNAConfig


def clamp_score(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def normalize_ratio(value: float | None) -> float:
    if value is None:
        return 0.0
    return clamp_score(value * 100.0)


def normalize_inverse_ratio(value: float | None, good_threshold: float = 0.1, bad_threshold: float = 0.4) -> float:
    if value is None:
        return 0.0
    if value <= good_threshold:
        return 100.0
    if value >= bad_threshold:
        return 0.0
    scale = (bad_threshold - value) / (bad_threshold - good_threshold)
    return clamp_score(scale * 100.0)


def normalize_lower_is_better(value: float | None, excellent: float, poor: float) -> float:
    if value is None:
        return 0.0
    if value <= excellent:
        return 100.0
    if value >= poor:
        return 0.0
    scale = (poor - value) / (poor - excellent)
    return clamp_score(scale * 100.0)


def normalize_delta(value: float | None, negative_bound: float = -0.5, positive_bound: float = 0.5) -> float:
    if value is None:
        return 0.0
    if value <= negative_bound:
        return 0.0
    if value >= positive_bound:
        return 100.0
    scale = (value - negative_bound) / (positive_bound - negative_bound)
    return clamp_score(scale * 100.0)


def normalize_bounded(value: float | None, minimum: float, maximum: float) -> float:
    if value is None:
        return 0.0
    if maximum == minimum:
        return 0.0
    scale = (value - minimum) / (maximum - minimum)
    return clamp_score(scale * 100.0)


def normalize_positive_evidence(value: int | None, threshold: int = 1, cap: int = 10) -> float:
    if value is None or value <= 0:
        return 0.0
    return clamp_score(min(value, cap) / cap * 100.0)
