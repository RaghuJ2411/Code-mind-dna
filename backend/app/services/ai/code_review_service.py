from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.services.ai.provider_factory import get_provider
from app.services.ai.context_builders import build_code_review_context
from app.services.ai.prompt_registry import PROMPT_REGISTRY
from app.services.ai.validators import validate_ai_response
from app.services.ai.usage_service import record_ai_request
from app.models.ai_code_review import AICodeReview
from app.models.execution import Submission
from app.models.problem import Problem
from app.models.user import User
from app.models.ai_request_log import AIRequestLog


class CodeReviewService:
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.current_user = current_user
        self.provider = get_provider()

    def get_cached_review(self, submission_id: int) -> AICodeReview | None:
        return self.db.query(AICodeReview).filter(AICodeReview.submission_id == submission_id).first()

    def generate_review(self, submission_id: int) -> dict:
        # Fetch submission and problem
        submission = self.db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            raise ValueError("Submission not found")
        if submission.student_id != self.current_user.id:
            raise PermissionError("not owner")

        problem = self.db.query(Problem).filter(Problem.id == submission.problem_id).first()

        context = build_code_review_context(
            problem={"id": problem.id, "title": problem.title, "description": problem.description, "constraints": problem.constraints if hasattr(problem, 'constraints') else None, "difficulty": getattr(problem, 'difficulty', None), "topics": getattr(problem, 'topics', None)},
            submission={"language": submission.language, "source_code": submission.source_code, "verdict": submission.verdict, "safe_error": submission.error_type, "passed_test_count": submission.passed_test_cases, "total_test_count": submission.total_test_cases, "runtime_ms": submission.runtime_ms, "memory_kb": submission.memory_kb},
        )

        prompt = PROMPT_REGISTRY["CODE_REVIEW"]

        provider_resp = self.provider.generate_structured(
            task_type="CODE_REVIEW",
            system_prompt=prompt["system"],
            context=context,
            response_schema=None,
            temperature=0.0,
        )

        # Validate structure
        try:
            validated = validate_ai_response("CODE_REVIEW", provider_resp.get("result", {}))
        except Exception as e:
            record_ai_request(
                self.db,
                self.current_user.id,
                "CODE_REVIEW",
                "mock",
                "mock",
                prompt.get("version"),
                "VALIDATION_FAILED",
                error_category=str(e),
            )
            raise

        # persist ai request and review
        meta = provider_resp.get("meta", {})
        record_ai_request(self.db, self.current_user.id, "CODE_REVIEW", meta.get("model", "mock"), meta.get("model", "mock"), prompt.get("version"), "SUCCESS", latency_ms=meta.get("latency_ms"))

        review = AICodeReview(
            student_id=self.current_user.id,
            submission_id=submission.id,
            review_json=validated.model_dump(),
            prompt_version=prompt.get("version"),
            provider="mock",
            model_name=meta.get("model", "mock"),
            status="SUCCESS",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)

        return validated.model_dump()
