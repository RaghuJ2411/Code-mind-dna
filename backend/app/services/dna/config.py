from __future__ import annotations

from enum import Enum


DNA_SCORING_VERSION = "1.0"


class EvidenceStatus(str, Enum):
    NO_DATA = "NO_DATA"
    LIMITED_DATA = "LIMITED_DATA"
    SUFFICIENT_DATA = "SUFFICIENT_DATA"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class ConfidenceLabel(str, Enum):
    VERY_LOW = "VERY_LOW"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class DimensionName(str, Enum):
    LOGIC = "LOGIC"
    DEBUGGING = "DEBUGGING"
    OPTIMIZATION = "OPTIMIZATION"
    CONSISTENCY = "CONSISTENCY"
    LEARNING_VELOCITY = "LEARNING_VELOCITY"
    PROBLEM_SOLVING_BREADTH = "PROBLEM_SOLVING_BREADTH"


class DNAConfig:
    logic_weights = {
        "solve_rate": 0.30,
        "first_attempt_acceptance_rate": 0.20,
        "average_attempts_to_solve": 0.20,
        "medium_problem_performance": 0.15,
        "hard_problem_performance": 0.15,
    }

    debugging_weights = {
        "error_recovery_rate": 0.40,
        "inverse_repeated_error_rate": 0.25,
        "failed_attempt_recovery": 0.20,
        "recovery_time_efficiency": 0.15,
    }

    optimization_weights = {
        "runtime_improvement": 0.35,
        "memory_improvement": 0.20,
        "post_acceptance_refinement": 0.25,
        "execution_efficiency_stability": 0.20,
    }

    consistency_weights = {
        "weekly_consistency_ratio": 0.40,
        "active_day_regularity": 0.25,
        "activity_stability": 0.20,
        "streak_behavior": 0.15,
    }

    learning_velocity_weights = {
        "solve_rate_improvement": 0.30,
        "attempt_efficiency_improvement": 0.25,
        "solve_time_improvement": 0.20,
        "difficulty_progression": 0.25,
    }

    breadth_weights = {
        "topic_breadth_ratio": 0.35,
        "unique_topics_solved": 0.25,
        "difficulty_breadth": 0.20,
        "cross_topic_success_balance": 0.20,
    }

    overall_dimension_weights = {
        DimensionName.LOGIC: 0.25,
        DimensionName.DEBUGGING: 0.20,
        DimensionName.OPTIMIZATION: 0.15,
        DimensionName.CONSISTENCY: 0.15,
        DimensionName.LEARNING_VELOCITY: 0.15,
        DimensionName.PROBLEM_SOLVING_BREADTH: 0.10,
    }

    temporal_windows = {
        "recent": 30,
        "previous": 30,
        "decay_30": 1.0,
        "decay_60": 0.75,
        "decay_90": 0.50,
        "decay_older": 0.25,
    }

    min_optimization_evidence = 2
    min_debugging_recoverable_sequences = 2
    min_breadth_topics = 3
    min_learning_evidence_problems = 3
    min_confidence_for_classification = 0.50
    meaningful_change_threshold = 2.0
