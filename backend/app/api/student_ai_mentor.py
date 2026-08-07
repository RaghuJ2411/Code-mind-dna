from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import User, UserRole

router = APIRouter(
    prefix="/student/ai-mentor",
    tags=["student-ai-mentor"],
)

@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
):
    return {
        "success": True,
        "message": "Chat endpoint is working"
    }


@router.get("/history")
async def history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
):
    return []
