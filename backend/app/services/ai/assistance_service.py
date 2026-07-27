from datetime import datetime
from sqlalchemy.orm import Session
from app.services.ai.provider_factory import get_provider
from app.services.ai.prompt_registry import PROMPT_REGISTRY
from app.services.ai.usage_service import record_ai_request
from app.services.ai.validators import validate_ai_response
from app.models.ai_assistance_response import AIAssistanceResponse
from app.models.execution import Submission
from app.models.problem import Problem
from app.models.user import User


class AIAssistanceService:
    def __init__(self, db: Session, current_user: User):
        self.db = db
        self.current_user = current_user
        self.provider = get_provider()

    def generate_assistance(self, submission_id: int, task_type: str) -> dict:
        submission = self.db.query(Submission).filter(Submission.id == submission_id).first()
        if not submission:
            raise ValueError("Submission not found")
        if submission.student_id != self.current_user.id:
            raise PermissionError("not owner")

        problem = self.db.query(Problem).filter(Problem.id == submission.problem_id).first()
        prompt = PROMPT_REGISTRY.get(task_type)
        if not prompt:
            raise ValueError("Unknown AI task")

        context = {
            "problem": {
                "id": problem.id,
                "title": problem.title,
                "description": problem.description,
                "constraints": problem.constraints,
                "difficulty": problem.difficulty,
                "topic": problem.topic,
            },
            "submission": {
                "id": submission.id,
                "language": submission.language,
                "source_code": submission.source_code,
                "verdict": submission.verdict,
                "passed_test_cases": submission.passed_test_cases,
                "total_test_cases": submission.total_test_cases,
                "runtime_ms": submission.runtime_ms,
                "memory_kb": submission.memory_kb,
                "error_type": submission.error_type,
            },
            "user": {
                "id": self.current_user.id,
                "role": self.current_user.role.value,
            },
        }

        provider_resp = self.provider.generate_structured(
            task_type=task_type,
            system_prompt=prompt["system"],
            context=context,
            response_schema=prompt.get("schema"),
            temperature=0.0,
        )

        validated = validate_ai_response(task_type, provider_resp.get("result", {}))
        meta = provider_resp.get("meta", {})
        record_ai_request(
            self.db,
            self.current_user.id,
            task_type,
            meta.get("provider", "mock"),
            meta.get("model", "mock"),
            prompt.get("version"),
            "SUCCESS",
            latency_ms=meta.get("latency_ms"),
        )

        record = AIAssistanceResponse(
            student_id=self.current_user.id,
            submission_id=submission.id,
            task_type=task_type,
            response_json=validated.model_dump(),
            prompt_version=prompt.get("version"),
            provider=meta.get("provider", "mock"),
            model_name=meta.get("model", "mock"),
            status="SUCCESS",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        return validated.model_dump()

    def get_last_response(self, submission_id: int, task_type: str) -> AIAssistanceResponse | None:
        return (
            self.db.query(AIAssistanceResponse)
            .filter(AIAssistanceResponse.submission_id == submission_id)
            .filter(AIAssistanceResponse.task_type == task_type)
            .order_by(AIAssistanceResponse.created_at.desc())
            .first()
        )
