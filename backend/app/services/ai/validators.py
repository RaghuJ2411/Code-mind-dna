from .schemas import CodeReviewResponse, ErrorExplanationResponse, SkillGapResponse, LearningRoadmapResponse


task_schema_map = {
    "CODE_REVIEW": CodeReviewResponse,
    "ERROR_EXPLANATION": ErrorExplanationResponse,
    "SKILL_GAP": SkillGapResponse,
    "ROADMAP": LearningRoadmapResponse,
}


def validate_ai_response(task_type: str, data: dict):
    schema = task_schema_map.get(task_type)
    if not schema:
        raise ValueError(f"No schema defined for task type {task_type}")
    return schema.model_validate(data)
