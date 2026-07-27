from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped

from app.core.database import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    title: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    assessment_type: Mapped[str] = Column(String(50), nullable=False)  # MCQ, CODING, MIXED
    difficulty: Mapped[str] = Column(String(50), nullable=False, default="medium")
    time_limit_minutes: Mapped[int] = Column(Integer, nullable=True)
    passing_score: Mapped[float] = Column(Float, nullable=False, default=60.0)
    total_questions: Mapped[int] = Column(Integer, nullable=False, default=0)
    is_active: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    created_by: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    assessment_id: Mapped[int] = Column(Integer, ForeignKey("assessments.id"), nullable=False, index=True)
    question_type: Mapped[str] = Column(String(50), nullable=False)  # MCQ, CODING, SHORT_ANSWER
    question_text: Mapped[str] = Column(Text, nullable=False)
    options: Mapped[list] = Column(JSON, nullable=True)  # For MCQ
    correct_answer: Mapped[str] = Column(Text, nullable=True)
    explanation: Mapped[str] = Column(Text, nullable=True)
    points: Mapped[int] = Column(Integer, nullable=False, default=1)
    order_index: Mapped[int] = Column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    assessment_id: Mapped[int] = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    started_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    submitted_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)
    time_taken_seconds: Mapped[int] = Column(Integer, nullable=True)
    is_completed: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    score: Mapped[float] = Column(Float, nullable=True)
    passed: Mapped[bool] = Column(Boolean, nullable=False, default=False)


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    attempt_id: Mapped[int] = Column(Integer, ForeignKey("assessment_attempts.id"), nullable=False)
    question_id: Mapped[int] = Column(Integer, ForeignKey("assessment_questions.id"), nullable=False)
    student_answer: Mapped[str] = Column(Text, nullable=True)
    is_correct: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    points_earned: Mapped[int] = Column(Integer, nullable=False, default=0)
    feedback: Mapped[str] = Column(Text, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

