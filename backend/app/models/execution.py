from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base


class SubmissionVerdict(str, PyEnum):
    ACCEPTED = "ACCEPTED"
    WRONG_ANSWER = "WRONG_ANSWER"
    COMPILATION_ERROR = "COMPILATION_ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    TIME_LIMIT_EXCEEDED = "TIME_LIMIT_EXCEEDED"
    MEMORY_LIMIT_EXCEEDED = "MEMORY_LIMIT_EXCEEDED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    problem_id: Mapped[int] = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    language: Mapped[str] = Column(String(50), nullable=False)
    source_code: Mapped[str] = Column(Text, nullable=False)
    verdict: Mapped[SubmissionVerdict] = Column(Enum(SubmissionVerdict), nullable=False, index=True)
    passed_test_cases: Mapped[int] = Column(Integer, nullable=False, default=0)
    total_test_cases: Mapped[int] = Column(Integer, nullable=False, default=0)
    runtime_ms: Mapped[int | None] = Column(Integer, nullable=True)
    memory_kb: Mapped[int | None] = Column(Integer, nullable=True)
    attempt_number: Mapped[int] = Column(Integer, nullable=False, default=1)
    error_type: Mapped[str | None] = Column(String(100), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)

    student: Mapped["User"] = relationship("User")
    problem: Mapped["Problem"] = relationship("Problem")


class CodingEvent(Base):
    __tablename__ = "coding_events"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    problem_id: Mapped[int] = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    session_id: Mapped[int | None] = Column(Integer, nullable=True)
    event_type: Mapped[str] = Column(String(100), nullable=False, index=True)
    language: Mapped[str | None] = Column(String(50), nullable=True)
    metadata_json: Mapped[dict | None] = Column(JSON, nullable=True, default=dict)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)


class CodingSession(Base):
    __tablename__ = "coding_sessions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    problem_id: Mapped[int] = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    started_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_activity_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ended_at: Mapped[datetime | None] = Column(DateTime(timezone=True), nullable=True)
    language: Mapped[str] = Column(String(50), nullable=False, default="python")
    run_count: Mapped[int] = Column(Integer, nullable=False, default=0)
    submit_count: Mapped[int] = Column(Integer, nullable=False, default=0)
    is_solved: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    wrong_answer_count: Mapped[int] = Column(Integer, nullable=False, default=0)
    compilation_error_count: Mapped[int] = Column(Integer, nullable=False, default=0)
    runtime_error_count: Mapped[int] = Column(Integer, nullable=False, default=0)
    time_limit_count: Mapped[int] = Column(Integer, nullable=False, default=0)
