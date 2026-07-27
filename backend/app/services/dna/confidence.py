from __future__ import annotations

from app.services.dna.config import ConfidenceLabel, DNAConfig


def confidence_label(value: float) -> ConfidenceLabel:
    if value < 0.2:
        return ConfidenceLabel.VERY_LOW
    if value < 0.4:
        return ConfidenceLabel.LOW
    if value < 0.6:
        return ConfidenceLabel.MEDIUM
    if value < 0.8:
        return ConfidenceLabel.HIGH
    return ConfidenceLabel.VERY_HIGH


def calculate_evidence_confidence(evidence_value: float, max_value: float = 1.0) -> float:
    if evidence_value is None:
        return 0.0
    return max(0.0, min(1.0, evidence_value / max_value))


def debugging_confidence(error_sequence_count: int, recovery_sequence_count: int, topic_count: int) -> float:
    if recovery_sequence_count <= 0:
        return 0.0

    evidence = min(1.0, recovery_sequence_count / max(1, DNAConfig.min_debugging_recoverable_sequences))
    topic_factor = min(1.0, topic_count / 5)
    return max(0.0, min(1.0, 0.6 * evidence + 0.4 * topic_factor))


def optimization_confidence(comparable_pairs: int, improved_pairs: int) -> float:
    if comparable_pairs <= 0:
        return 0.0

    evidence = min(1.0, comparable_pairs / max(1, DNAConfig.min_optimization_evidence))
    improvement_factor = min(1.0, improved_pairs / max(1, comparable_pairs))
    return max(0.0, min(1.0, 0.7 * evidence + 0.3 * improvement_factor))


def consistency_confidence(active_days: int, distinct_weeks: int) -> float:
    if distinct_weeks <= 0:
        return 0.0
    evidence = min(1.0, active_days / (distinct_weeks * 5))
    return max(0.0, min(1.0, evidence))


def learning_velocity_confidence(previous_problems: int, recent_problems: int) -> float:
    if previous_problems + recent_problems == 0:
        return 0.0
    evidence = min(1.0, (previous_problems + recent_problems) / 10)
    return max(0.0, min(1.0, evidence))


def breadth_confidence(unique_topics: int, meaningful_topic_count: int) -> float:
    if unique_topics <= 0:
        return 0.0
    evidence = min(1.0, unique_topics / max(1, DNAConfig.min_breadth_topics))
    return max(0.0, min(1.0, evidence))
