from __future__ import annotations
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base


class RecruiterInterview(Base):
    __tablename__ = "recruiter_interviews"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    recruiter_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    candidate_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id: Mapped[int] = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    interviewer: Mapped[str] = Column(String(255), nullable=False)
    slot: Mapped[str] = Column(String(100), nullable=False)
    mode: Mapped[str] = Column(String(50), nullable=False, default="Zoom")
    link: Mapped[str | None] = Column(String(500), nullable=True)
    notes: Mapped[str | None] = Column(Text, nullable=True)
    status: Mapped[str] = Column(String(50), nullable=False, default="SCHEDULED")
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    candidate = relationship("User", foreign_keys=[candidate_id])
    job = relationship("JobPosting", foreign_keys=[job_id])


class RecruiterShortlist(Base):
    __tablename__ = "recruiter_shortlists"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    recruiter_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False)
    candidate_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id: Mapped[int] = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    rating: Mapped[float | None] = Column(Float, nullable=True)
    notes: Mapped[str | None] = Column(Text, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    candidate = relationship("User", foreign_keys=[candidate_id])
    job = relationship("JobPosting", foreign_keys=[job_id])

    __table_args__ = (UniqueConstraint("recruiter_id", "candidate_id", "job_id", name="uq_recruiter_shortlist"),)


class RecruiterCompanyProfile(Base):
    __tablename__ = "recruiter_company_profiles"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    recruiter_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    company_name: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[str | None] = Column(Text, nullable=True)
    industry: Mapped[str | None] = Column(String(100), nullable=True)
    website: Mapped[str | None] = Column(String(255), nullable=True)
    employees: Mapped[str | None] = Column(String(50), nullable=True)
    location: Mapped[str | None] = Column(String(255), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class RecruiterReport(Base):
    __tablename__ = "recruiter_reports"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    recruiter_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[str | None] = Column(Text, nullable=True)
    report_type: Mapped[str] = Column(String(50), nullable=False)
    data: Mapped[dict | None] = Column(JSON, nullable=True)
    generated_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    recruiter = relationship("User", foreign_keys=[recruiter_id])

