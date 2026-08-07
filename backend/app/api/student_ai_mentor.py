from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.models.user import User, UserRole

# ✅ Import your schemas
from app.schemas.ai_mentor import (
    ChatRequest,
    ChatResponse,
    ChatHistoryResponse,
)

router = APIRouter(
    prefix="/student/ai-mentor",
    tags=["student-ai-mentor"],
)


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
):
    return ChatResponse(
        reply="Chat endpoint is working.",
        conversation_id=request.conversation_id or 1,
    )


@router.get("/history", response_model=ChatHistoryResponse)
async def history(
    conversation_id: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT)),
):
    return ChatHistoryResponse(
        conversation_id=conversation_id,
        messages=[],
    )
