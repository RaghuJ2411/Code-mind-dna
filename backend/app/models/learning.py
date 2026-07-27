from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped

from app.core.database import Base


class LearningCourse(Base):
    __tablename__ = "learning_courses"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    title: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[str] = Column(Text, nullable=True)
    category: Mapped[str] = Column(String(100), nullable=False, default="general")
    difficulty: Mapped[str] = Column(String(50), nullable=False, default="beginner")
    duration_hours: Mapped[float] = Column(Float, nullable=True)
    thumbnail_url: Mapped[str] = Column(String(500), nullable=True)
    content_json: Mapped[dict] = Column(JSON, nullable=False, default=dict)
    skills_covered: Mapped[list] = Column(JSON, nullable=False, default=list)
    prerequisites: Mapped[list] = Column(JSON, nullable=False, default=list)
    is_active: Mapped[bool] = Column(Boolean, nullable=False, default=True)
    created_by: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id: Mapped[int] = Column(Integer, ForeignKey("learning_courses.id"), nullable=False)
    progress_pct: Mapped[float] = Column(Float, nullable=False, default=0.0)
    completed: Mapped[bool] = Column(Boolean, nullable=False, default=False)
    completed_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)
    enrolled_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("student_id", "course_id", name="uq_enrollment"),)


class CourseProgress(Base):
    __tablename__ = "course_progress"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id: Mapped[int] = Column(Integer, ForeignKey("learning_courses.id"), nullable=False)
    module_id: Mapped[str] = Column(String(100), nullable=False)
    completed_sections: Mapped[list] = Column(JSON, nullable=False, default=list)
    current_section: Mapped[str] = Column(String(100), nullable=True)
    last_accessed_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint("student_id", "course_id", "module_id", name="uq_course_progress"),)


class Bookmark(Base):
    __tablename__ = "bookmarks"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    resource_type: Mapped[str] = Column(String(50), nullable=False)  # course, problem, article
    resource_id: Mapped[int] = Column(Integer, nullable=False)
    resource_title: Mapped[str] = Column(String(255), nullable=True)
    notes: Mapped[str] = Column(Text, nullable=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    resource_type: Mapped[str] = Column(String(50), nullable=True)
    resource_id: Mapped[int] = Column(Integer, nullable=True)
    title: Mapped[str] = Column(String(255), nullable=False)
    content: Mapped[str] = Column(Text, nullable=False)
    tags: Mapped[list] = Column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id: Mapped[int] = Column(Integer, ForeignKey("learning_courses.id"), nullable=False)
    certificate_url: Mapped[str] = Column(String(500), nullable=True)
    issued_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=True)
    is_verified: Mapped[bool] = Column(Boolean, nullable=False, default=False)

