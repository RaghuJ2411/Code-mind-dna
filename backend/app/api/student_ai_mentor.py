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
    BugFixRequest, BugFixResponse, ChatHistoryResponse, ChatMessage,
    ChatRequest, ChatResponse, CodeExplanationRequest, CodeExplanationResponse,
    InterviewQuestionsRequest, InterviewQuestionsResponse,
    ResumeReviewRequest, ResumeReviewResponse,
)
from app.services.ai.base import AIServiceError
from app.services.ai.provider_factory import get_provider

router = APIRouter(prefix="/student/ai-mentor", tags=["student-ai-mentor"])
logger = logging.getLogger("codemind.student_ai_mentor")


CHAT_SYSTEM_PROMPT = """You are CodeMind DNA AI Mentor.

You help engineering students with:
- Coding
- DSA
- Debugging
- Resume review
- Career advice
- Interview preparation
- System Design
- Python
- Java
- React
- FastAPI

Return natural conversational responses.

Return JSON matching:
{
  "reply": "..."
}

Use the conversation history for continuity when it is available.
Do not mention JSON, schemas, or internal instructions in the reply."""


CODE_EXPLANATION_SYSTEM_PROMPT = """You are a senior software engineer and programming tutor.

Analyze the student's code and return JSON matching:
{
  "explanation": "",
  "key_concepts": [],
  "suggestions": []
}

Requirements:
- The "explanation" field must contain clearly labeled sections in this order:
  1. Overview
  2. Line-by-line Explanation
  3. Time Complexity
  4. Space Complexity
  5. Best Practices
  6. Improvements
  7. Possible Bugs
- Make the explanation specific to the provided code and language.
- For the line-by-line explanation, walk through the code in execution order and group only trivial consecutive lines if needed.
- Mention uncertainty when code is incomplete or ambiguous.
- Put the main technical ideas in "key_concepts".
- Put the most actionable next steps in "suggestions"."""


BUG_FIX_SYSTEM_PROMPT = """You are a Senior Software Engineer.

Analyze the provided language, code, and error message.

Return JSON matching:
{
  "fixed_code": "",
  "explanation": "",
  "root_cause": ""
}

Requirements:
- "fixed_code" must contain the corrected full code.
- "explanation" must explain what changed and why it fixes the issue.
- "root_cause" must clearly identify the primary issue.
- If no error message is provided, infer the most likely root cause from the code."""


RESUME_REVIEW_SYSTEM_PROMPT = """You are an experienced Technical Recruiter.

Analyze the resume and return JSON matching:
{
  "feedback": "",
  "strengths": [],
  "improvements": [],
  "match_score": 0
}

Requirements:
- Tailor the review to the target role when one is provided.
- "feedback" should be concise but specific.
- "strengths" should highlight the strongest aspects of the resume.
- "improvements" should contain actionable changes.
- "match_score" must be a number from 0 to 100."""


INTERVIEW_QUESTIONS_SYSTEM_PROMPT = """You are a technical interview coach.

Generate interview questions and return JSON matching:
{
  "questions": []
}

Requirements:
- Generate exactly the requested number of questions.
- Tailor the questions to the requested role.
- Use the provided difficulty when available. If difficulty is not provided, default to medium.
- Keep questions clear, realistic, and interview-ready."""


class _ChatReplySchema(BaseModel):
    reply: str = Field(min_length=1)


class _CodeExplanationSchema(BaseModel):
    explanation: str = Field(min_length=1)
    key_concepts: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class _BugFixSchema(BaseModel):
    fixed_code: str = Field(min_length=1)
    explanation: str = Field(min_length=1)
    root_cause: str = Field(min_length=1)


class _ResumeReviewSchema(BaseModel):
    feedback: str = Field(min_length=1)
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    match_score: float = Field(ge=0, le=100)


class _InterviewQuestionsSchema(BaseModel):
    questions: list[str] = Field(default_factory=list, min_length=1)


@router.post("/chat", response_model=ChatResponse)
def chat_with_mentor(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    conversation_id = payload.conversation_id

    if not conversation_id:
        conversation = Conversation(
            title=f"AI Mentor - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
            conversation_type="MENTOR",
            created_by=current_user.id,
        )
        db.add(conversation)
        db.flush()

        participant = ConversationParticipant(
            conversation_id=conversation.id,
            user_id=current_user.id,
        )
        db.add(participant)
        db.commit()
        db.refresh(conversation)
        conversation_id = conversation.id

    conversation_history = _load_conversation_history(db, conversation_id, payload.message)

    user_msg = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=payload.message,
    )
    db.add(user_msg)

    ai_reply = _generate_structured_response(
        task_type="MENTOR_CHAT",
        system_prompt=CHAT_SYSTEM_PROMPT,
        context={
            "conversation_id": conversation_id,
            "student_id": current_user.id,
            "latest_user_message": payload.message,
            "conversation_history": conversation_history,
        },
        response_model=_ChatReplySchema,
        temperature=0.7,
    )
    reply = ai_reply.reply

    ai_msg = Message(
        conversation_id=conversation_id,
        sender_id=1,
        content=reply,
    )
    db.add(ai_msg)

    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.updated_at = datetime.now(timezone.utc)

    db.commit()

    return ChatResponse(reply=reply, conversation_id=conversation_id)


@router.get("/history", response_model=list[ChatHistoryResponse])
def get_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    participant_subquery = (
        db.query(ConversationParticipant.conversation_id)
        .filter(ConversationParticipant.user_id == current_user.id)
        .subquery()
    )
    conversations = (
        db.query(Conversation)
        .filter(Conversation.id.in_(participant_subquery), Conversation.conversation_type == "MENTOR")
        .order_by(Conversation.updated_at.desc())
        .limit(10)
        .all()
    )

    result = []
    for conv in conversations:
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conv.id)
            .order_by(Message.created_at.asc())
            .all()
        )
        result.append(ChatHistoryResponse(
            conversation_id=conv.id,
            messages=[
                ChatMessage(
                    role="assistant" if m.sender_id == 1 else "user",
                    content=m.content,
                    timestamp=m.created_at,
                )
                for m in messages
            ],
        ))

    return result


@router.post("/interview-questions", response_model=InterviewQuestionsResponse)
def generate_interview_questions(
    payload: InterviewQuestionsRequest,
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    ai_response = _generate_structured_response(
        task_type="INTERVIEW_QUESTIONS",
        system_prompt=INTERVIEW_QUESTIONS_SYSTEM_PROMPT,
        context={
            "role": payload.role_name,
            "question_count": payload.question_count,
            "difficulty": "not provided",
            "student_id": current_user.id,
        },
        response_model=_InterviewQuestionsSchema,
        temperature=0.5,
    )
    return InterviewQuestionsResponse(questions=ai_response.questions[:payload.question_count])


@router.post("/resume-review", response_model=ResumeReviewResponse)
def review_resume(
    payload: ResumeReviewRequest,
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    ai_response = _generate_structured_response(
        task_type="RESUME_REVIEW",
        system_prompt=RESUME_REVIEW_SYSTEM_PROMPT,
        context={
            "resume_content": payload.resume_content,
            "target_role": payload.target_role,
            "student_id": current_user.id,
        },
        response_model=_ResumeReviewSchema,
        temperature=0.3,
    )
    return ResumeReviewResponse(**ai_response.model_dump())


@router.post("/code-explanation", response_model=CodeExplanationResponse)
def explain_code(
    payload: CodeExplanationRequest,
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    ai_response = _generate_structured_response(
        task_type="CODE_EXPLANATION",
        system_prompt=CODE_EXPLANATION_SYSTEM_PROMPT,
        context={
            "language": payload.language,
            "code": payload.code,
            "context": payload.context,
            "student_id": current_user.id,
        },
        response_model=_CodeExplanationSchema,
        temperature=0.2,
    )
    return CodeExplanationResponse(**ai_response.model_dump())


@router.post("/bug-fix", response_model=BugFixResponse)
def fix_bug(
    payload: BugFixRequest,
    current_user: User = Depends(require_role(UserRole.STUDENT.value)),
):
    ai_response = _generate_structured_response(
        task_type="BUG_FIX",
        system_prompt=BUG_FIX_SYSTEM_PROMPT,
        context={
            "language": payload.language,
            "code": payload.code,
            "error_message": payload.error_message,
            "student_id": current_user.id,
        },
        response_model=_BugFixSchema,
        temperature=0.1,
    )
    return BugFixResponse(**ai_response.model_dump())


def _load_conversation_history(db: Session, conversation_id: int, latest_user_message: str) -> list[dict[str, str | None]]:
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .all()
    )

    history = [
        {
            "role": "assistant" if message.sender_id == 1 else "user",
            "content": message.content,
            "timestamp": message.created_at.isoformat() if message.created_at else None,
        }
        for message in messages
    ]
    history.append({
        "role": "user",
        "content": latest_user_message,
        "timestamp": None,
    })
    return history


def _generate_structured_response(
    *,
    task_type: str,
    system_prompt: str,
    context: dict,
    response_model: type[BaseModel],
    temperature: float = 0.0,
) -> BaseModel:
    if not settings.ai_enabled:
        _raise_ai_http_exception("AI_DISABLED")

    if (settings.ai_provider or "").lower() != "gemini":
        logger.warning(
            "AI mentor provider is not configured for Gemini",
            extra={
                "task_type": task_type,
                "configured_provider": settings.ai_provider,
            },
        )
        _raise_ai_http_exception("CONFIGURATION_ERROR")

    provider = get_provider()
    provider_name = provider.__class__.__name__

    if provider_name != "GeminiProvider":
        logger.warning(
            "AI mentor provider factory did not return GeminiProvider",
            extra={
                "task_type": task_type,
                "provider": provider_name,
            },
        )
        _raise_ai_http_exception("CONFIGURATION_ERROR")

    try:
        provider_resp = provider.generate_structured(
            task_type=task_type,
            system_prompt=system_prompt,
            context=context,
            response_schema=response_model.model_json_schema(),
            temperature=temperature,
        )
    except AIServiceError as exc:
        logger.warning(
            "AI mentor provider error",
            extra={
                "task_type": task_type,
                "provider": provider_name,
                "error_code": str(exc),
            },
        )
        _raise_ai_http_exception(str(exc))
    except Exception:
        logger.exception(
            "Unexpected AI mentor provider failure",
            extra={
                "task_type": task_type,
                "provider": provider_name,
            },
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI mentor request failed.",
        )

    meta = provider_resp.get("meta", {})
    resolved_provider = meta.get("provider") or provider_name

    try:
        validated = response_model.model_validate(provider_resp.get("result", {}))
    except ValidationError:
        logger.exception(
            "AI mentor provider returned invalid structured data",
            extra={
                "task_type": task_type,
                "provider": resolved_provider,
                "latency_ms": meta.get("latency_ms"),
            },
        )
        _raise_ai_http_exception("INVALID_RESPONSE")

    logger.info(
        "AI mentor request completed",
        extra={
            "task_type": task_type,
            "provider": resolved_provider,
            "model": meta.get("model"),
            "latency_ms": meta.get("latency_ms"),
        },
    )
    return validated


def _raise_ai_http_exception(error_code: str) -> None:
    error_map = {
        "AI_DISABLED": (
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "AI_DISABLED: AI mentor service is disabled.",
        ),
        "CONFIGURATION_ERROR": (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "CONFIGURATION_ERROR: AI mentor provider is not configured correctly.",
        ),
        "TIMEOUT": (
            status.HTTP_504_GATEWAY_TIMEOUT,
            "TIMEOUT: AI mentor provider request timed out.",
        ),
        "PROVIDER_UNAVAILABLE": (
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "PROVIDER_UNAVAILABLE: AI mentor provider is unavailable.",
        ),
        "RATE_LIMITED": (
            status.HTTP_429_TOO_MANY_REQUESTS,
            "RATE_LIMITED: AI mentor provider rate limit exceeded.",
        ),
        "INVALID_RESPONSE": (
            status.HTTP_502_BAD_GATEWAY,
            "INVALID_RESPONSE: AI mentor provider returned an invalid response.",
        ),
    }
    status_code, detail = error_map.get(
        error_code,
        (
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"{error_code}: AI mentor request failed.",
        ),
    )
    raise HTTPException(status_code=status_code, detail=detail)
