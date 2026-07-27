from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import Mapped

from app.core.database import Base


class StudentSettings(Base):
    __tablename__ = "student_settings"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, unique=True)
    photo_url: Mapped[str] = Column(String(500), nullable=True)
    phone: Mapped[str] = Column(String(20), nullable=True)
    bio: Mapped[str] = Column(String(1000), nullable=True)
    theme: Mapped[str] = Column(String(20), nullable=False, default="light")
    language: Mapped[str] = Column(String(10), nullable=False, default="en")
    email_notifications: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    push_notifications: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    sms_notifications: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    profile_visibility: Mapped[str] = Column(String(20), nullable=False, default="public")  # public, private, mentors
    two_factor_enabled: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    two_factor_secret: Mapped[str] = Column(String(100), nullable=True)
    privacy_settings: Mapped[dict] = Column(JSON, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

