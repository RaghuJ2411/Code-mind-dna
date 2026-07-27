from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class LearningCourseResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    category: str
    difficulty: str
    duration_hours: float | None = None
    thumbnail_url: str | None = None
    skills_covered: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EnrollmentResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    progress_pct: float
    completed: bool
    completed_at: datetime | None = None
    enrolled_at: datetime

    class Config:
        from_attributes = True


class CourseProgressResponse(BaseModel):
    id: int
    course_id: int
    module_id: str
    completed_sections: list[str] = Field(default_factory=list)
    current_section: str | None = None
    last_accessed_at: datetime | None = None

    class Config:
        from_attributes = True


class BookmarkResponse(BaseModel):
    id: int
    resource_type: str
    resource_id: int
    resource_title: str | None = None
    notes: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class BookmarkCreate(BaseModel):
    resource_type: str
    resource_id: int
    resource_title: str | None = None
    notes: str | None = None


class NoteResponse(BaseModel):
    id: int
    resource_type: str | None = None
    resource_id: int | None = None
    title: str
    content: str
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NoteCreate(BaseModel):
    resource_type: str | None = None
    resource_id: int | None = None
    title: str
    content: str
    tags: list[str] = Field(default_factory=list)


class NoteUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None


class CertificateResponse(BaseModel):
    id: int
    course_id: int
    certificate_url: str | None = None
    issued_at: datetime
    is_verified: bool

    class Config:
        from_attributes = True


class LearningHistoryItem(BaseModel):
    course_id: int
    course_title: str
    action: str  # ENROLLED, PROGRESS, COMPLETED
    timestamp: datetime


class LearningHistoryResponse(BaseModel):
    items: list[LearningHistoryItem] = Field(default_factory=list)

