from app.services.recommendations.config import RecommendationType, RecommendationPriority
from app.services.recommendations.recommendation_service import RecommendationService
from app.services.recommendations.rules import (
    build_debug_error_pattern_recommendation,
    build_improve_consistency_recommendation,
    build_increase_difficulty_recommendation,
    build_review_foundation_recommendation,
    build_topic_practice_recommendation,
)

__all__ = [
    "RecommendationType",
    "RecommendationPriority",
    "RecommendationService",
    "build_debug_error_pattern_recommendation",
    "build_improve_consistency_recommendation",
    "build_increase_difficulty_recommendation",
    "build_review_foundation_recommendation",
    "build_topic_practice_recommendation",
]
