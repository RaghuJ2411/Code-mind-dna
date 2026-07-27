from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str  # user, assistant
    content: str
    timestamp: datetime | None = None


class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None


class ChatResponse(BaseModel):
    reply: str
    conversation_id: int


class ChatHistoryResponse(BaseModel):
    conversation_id: int
    messages: list[ChatMessage] = Field(default_factory=list)


class InterviewQuestionsRequest(BaseModel):
    role_name: str
    question_count: int = 5


class InterviewQuestionsResponse(BaseModel):
    questions: list[str] = Field(default_factory=list)


class ResumeReviewRequest(BaseModel):
    resume_content: str
    target_role: str | None = None


class ResumeReviewResponse(BaseModel):
    feedback: str
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    match_score: float | None = None


class CodeExplanationRequest(BaseModel):
    code: str
    language: str
    context: str | None = None


class CodeExplanationResponse(BaseModel):
    explanation: str
    key_concepts: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class BugFixRequest(BaseModel):
    code: str
    error_message: str | None = None
    language: str


class BugFixResponse(BaseModel):
    fixed_code: str
    explanation: str
    root_cause: str | None = None

