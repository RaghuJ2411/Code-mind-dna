from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class ConversationResponse(BaseModel):
    id: int
    title: str | None = None
    conversation_type: str
    unread_count: int = 0
    last_message: str | None = None
    last_message_at: datetime | None = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ParticipantResponse(BaseModel):
    user_id: int
    user_name: str
    user_role: str

    class Config:
        from_attributes = True


class ConversationDetailResponse(BaseModel):
    id: int
    title: str | None = None
    conversation_type: str
    participants: list[ParticipantResponse] = Field(default_factory=list)
    messages: list[dict] = Field(default_factory=list)
    created_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    sender_name: str
    content: str
    attachment_url: str | None = None
    attachment_type: str | None = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SendMessageRequest(BaseModel):
    content: str
    attachment_url: str | None = None
    attachment_type: str | None = None


class UnreadCountResponse(BaseModel):
    total_unread: int

