from __future__ import annotations
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base


class StudentJobApplication(Base):
    __tablename__ = "student_job_applications"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id: Mapped[int] = Column(Integer, ForeignKey("job_postings.id"), nullable=False, index=True)
    status: Mapped[str] = Column(String(50), nullable=False, default="APPLIED")
    applied_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    student = relationship("User", foreign_keys=[student_id])
    job = relationship("JobPosting", foreign_keys=[job_id])


class JobSeniority(str, PyEnum):
    ENTRY = "ENTRY"
    MID = "MID"
    SENIOR = "SENIOR"
    LEAD = "LEAD"


class JobPosting(Base):
    __tablename__ = "job_postings"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    recruiter_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = Column(String(255), nullable=False)
    company: Mapped[str] = Column(String(255), nullable=False)
    location: Mapped[str] = Column(String(255), nullable=False)
    seniority_level: Mapped[JobSeniority] = Column(Enum(JobSeniority), nullable=False)
    description: Mapped[str] = Column(Text, nullable=False)
    requirements_json: Mapped[list[str]] = Column(JSON, nullable=False, default=list)
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    recruiter = relationship("User", foreign_keys=[recruiter_id])
