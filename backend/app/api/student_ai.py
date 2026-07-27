from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.ai_deps import require_ai_daily_limit
from app.api.deps import get_db, require_role
from app.models.user import UserRole
from app.services.ai.code_review_service import CodeReviewService

router = APIRouter()


@router.post("/student/ai/code-review/{submission_id}")
def request_code_review(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_ai_daily_limit("CODE_REVIEW", allowed_roles=[UserRole.STUDENT.value])),
):
    service = CodeReviewService(db, current_user)
    try:
        result = service.generate_review(submission_id)
        return {"status": "success", "data": result}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized")
    except ValueError:
        raise HTTPException(status_code=404, detail="Submission not found")
    except Exception as exc:
        raise HTTPException(status_code=500, detail="AI service failed")


@router.get("/student/ai/code-review/{submission_id}")
def get_code_review(submission_id: int, db: Session = Depends(get_db), current_user=Depends(require_role(UserRole.STUDENT.value))):
    service = CodeReviewService(db, current_user)
    review = service.get_cached_review(submission_id)
    if not review:
        raise HTTPException(status_code=404, detail="Code review not found")
    return {"status": "success", "data": review.review_json}
