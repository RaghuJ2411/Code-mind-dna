from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped

from app.core.database import Base


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    title: Mapped[str] = Column(String(255), nullable=True)
    conversation_type: Mapped[str] = Column(String(50), nullable=False)  # MENTOR, RECRUITER, GROUP
    created_by: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ConversationParticipant(Base):
    __tablename__ = "conversation_participants"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[int] = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    last_read_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)
    joined_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_muted: Mapped[bool] = Column(Boolean, nullable=False, default=False)

    __table_args__ = (UniqueConstraint("conversation_id", "user_id", name="uq_conversation_participant"),)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    conversation_id: Mapped[int] = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    sender_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = Column(Text, nullable=False)
    attachment_url: Mapped[str] = Column(String(500), nullable=True)
    attachment_type: Mapped[str] = Column(String(50), nullable=True)
    is_read: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

