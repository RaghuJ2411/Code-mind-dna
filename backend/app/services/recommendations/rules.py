from __future__ import annotations

from datetime import datetime

from app.services.recommendations.config import RecommendationPriority, RecommendationType


def build_topic_practice_recommendation(topic: str, solve_rate: float, attempts: int) -> dict[str, object]:
    return {
        "recommendation_type": RecommendationType.PRACTICE_TOPIC.value,
        "priority": RecommendationPriority.HIGH.value if solve_rate < 0.4 else RecommendationPriority.MEDIUM.value,
        "title": f"Strengthen {topic} fundamentals",
        "reason": f"Your recent {topic} solve rate is {solve_rate:.0%} across {attempts} attempted problems.",
        "action_json": {"topic": topic, "difficulty": "EASY", "problem_count": 3},
    }


def build_increase_difficulty_recommendation() -> dict[str, object]:
    return {
        "recommendation_type": RecommendationType.INCREASE_DIFFICULTY.value,
        "priority": RecommendationPriority.MEDIUM.value,
        "title": "Increase problem difficulty",
        "reason": "Your overall problem-solving performance is stable enough to benefit from higher difficulty practice.",
        "action_json": {"difficulty": "MEDIUM", "problem_count": 2},
    }


def build_review_foundation_recommendation() -> dict[str, object]:
    return {
        "recommendation_type": RecommendationType.REVIEW_FOUNDATION.value,
        "priority": RecommendationPriority.HIGH.value,
        "title": "Review foundation concepts",
        "reason": "Your solve rates show room for improvement on foundational topics.",
        "action_json": {},
    }


def build_debug_error_pattern_recommendation(error_type: str) -> dict[str, object]:
    return {
        "recommendation_type": RecommendationType.DEBUG_ERROR_PATTERN.value,
        "priority": RecommendationPriority.HIGH.value,
        "title": f"Review {error_type} debugging practice",
        "reason": f"Repeated {error_type} errors suggest focused debugging practice is needed.",
        "action_json": {},
    }


def build_improve_consistency_recommendation() -> dict[str, object]:
    return {
        "recommendation_type": RecommendationType.IMPROVE_CONSISTENCY.value,
        "priority": RecommendationPriority.MEDIUM.value,
        "title": "Improve consistency",
        "reason": "Maintaining regular coding activity will improve your evidence strength and reliability.",
        "action_json": {},
    }
