from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.ai_deps import require_ai_daily_limit
from app.api.deps import get_db, require_role
from app.models.user import UserRole
from app.schemas.ai_usage import AIUsageHistoryResponse
from app.services.ai.assistance_service import AIAssistanceService
from app.services.ai.usage_summary_service import AIUsageSummaryService

router = APIRouter()


@router.post("/student/ai/error-explanation/{submission_id}")
def request_error_explanation(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_ai_daily_limit("ERROR_EXPLANATION", allowed_roles=[UserRole.STUDENT.value])),
):
    service = AIAssistanceService(db, current_user)
    try:
        result = service.generate_assistance(submission_id, "ERROR_EXPLANATION")
        return {"status": "success", "data": result}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized")
    except ValueError:
        raise HTTPException(status_code=404, detail="Submission not found")
    except Exception:
        raise HTTPException(status_code=500, detail="AI service failed")


@router.post("/student/ai/skill-gap/{submission_id}")
def request_skill_gap(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_ai_daily_limit("SKILL_GAP", allowed_roles=[UserRole.STUDENT.value])),
):
    service = AIAssistanceService(db, current_user)
    try:
        result = service.generate_assistance(submission_id, "SKILL_GAP")
        return {"status": "success", "data": result}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized")
    except ValueError:
        raise HTTPException(status_code=404, detail="Submission not found")
    except Exception:
        raise HTTPException(status_code=500, detail="AI service failed")


@router.post("/student/ai/roadmap/{submission_id}")
def request_roadmap(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_ai_daily_limit("ROADMAP", allowed_roles=[UserRole.STUDENT.value])),
):
    service = AIAssistanceService(db, current_user)
    try:
        result = service.generate_assistance(submission_id, "ROADMAP")
        return {"status": "success", "data": result}
    except PermissionError:
        raise HTTPException(status_code=403, detail="Not authorized")
    except ValueError:
        raise HTTPException(status_code=404, detail="Submission not found")
    except Exception:
        raise HTTPException(status_code=500, detail="AI service failed")


@router.get("/student/ai/usage-history", response_model=AIUsageHistoryResponse)
def get_ai_usage_history(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(UserRole.STUDENT.value)),
):
    summary_service = AIUsageSummaryService(db)
    daily_summary = summary_service.get_daily_usage(current_user.id)
    recent_requests = summary_service.get_recent_requests(current_user.id, limit=12)
    return AIUsageHistoryResponse(daily_summary=daily_summary, recent_requests=recent_requests)
