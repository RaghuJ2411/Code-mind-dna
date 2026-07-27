from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base


class CareerSeniority(str, PyEnum):
    ENTRY = "ENTRY"
    MID = "MID"
    SENIOR = "SENIOR"


class CareerRole(Base):
    __tablename__ = "career_roles"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String(255), nullable=False)
    seniority_level: Mapped[CareerSeniority] = Column(Enum(CareerSeniority), nullable=False)
    description: Mapped[str] = Column(Text, nullable=False)
    required_skills_json: Mapped[list[str]] = Column(JSON, nullable=False, default=list)
    target_score_min: Mapped[int] = Column(Integer, nullable=False, default=50)
    target_score_max: Mapped[int] = Column(Integer, nullable=False, default=100)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class StudentResumeEntry(Base):
    __tablename__ = "student_resume_entries"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    section: Mapped[str] = Column(String(100), nullable=False)
    title: Mapped[str] = Column(String(255), nullable=False)
    content: Mapped[str] = Column(Text, nullable=False)
    skills_json: Mapped[list[str]] = Column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student = relationship("User")


class StudentProject(Base):
    __tablename__ = "student_projects"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[str] = Column(Text, nullable=False)
    technologies_json: Mapped[list[str]] = Column(JSON, nullable=False, default=list)
    outcome: Mapped[str] = Column(Text, nullable=True)
    project_url: Mapped[str | None] = Column(String(500), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student = relationship("User")


class InterviewPracticeSession(Base):
    __tablename__ = "interview_practice_sessions"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_name: Mapped[str | None] = Column(String(255), nullable=True)
    question: Mapped[str] = Column(Text, nullable=False)
    answer: Mapped[str] = Column(Text, nullable=False)
    feedback_score: Mapped[int] = Column(Integer, nullable=False)
    feedback_text: Mapped[str] = Column(Text, nullable=False)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    student = relationship("User")


class MentorCareerReview(Base):
    __tablename__ = "mentor_career_reviews"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    mentor_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_id: Mapped[int | None] = Column(Integer, ForeignKey("career_roles.id"), nullable=True, index=True)
    review_type: Mapped[str] = Column(String(50), nullable=False, default="CAREER")
    note: Mapped[str] = Column(Text, nullable=False)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    mentor = relationship("User", foreign_keys=[mentor_id])
    student = relationship("User", foreign_keys=[student_id])
    role = relationship("CareerRole", foreign_keys=[role_id])
