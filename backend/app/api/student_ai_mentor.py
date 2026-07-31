from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_role
from app.core.config import settings
from app.models.message import Conversation, ConversationParticipant, Message
from app.models.user import User, UserRole
from app.schemas.ai_mentor import (
    BugFixRequest,
    BugFixResponse,
    ChatHistoryResponse,
    ChatMessage,
    ChatRequest,
    ChatResponse,
    CodeExplanationRequest,
    CodeExplanationResponse,
    InterviewQuestionsRequest,
    InterviewQuestionsResponse,
    ResumeReviewRequest,
    ResumeReviewResponse,
)
from app.services.ai.base import AIServiceError
from app.services.ai.provider_factory import get_provider

router = APIRouter(
    prefix="/student/ai-mentor",
    tags=["student-ai-mentor"],
)

logger = logging.getLogger("codemind.student_ai_mentor")
