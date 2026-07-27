from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, relationship

from app.core.database import Base


class DifficultyLevel(str, PyEnum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class TopicType(str, PyEnum):
    ARRAYS = "ARRAYS"
    STRINGS = "STRINGS"
    HASHING = "HASHING"
    LINKED_LISTS = "LINKED_LISTS"
    STACKS = "STACKS"
    QUEUES = "QUEUES"
    TREES = "TREES"
    GRAPHS = "GRAPHS"
    RECURSION = "RECURSION"
    BACKTRACKING = "BACKTRACKING"
    DYNAMIC_PROGRAMMING = "DYNAMIC_PROGRAMMING"
    SEARCHING = "SEARCHING"
    SORTING = "SORTING"


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    title: Mapped[str] = Column(String(255), nullable=False)
    slug: Mapped[str] = Column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str] = Column(Text, nullable=False)
    difficulty: Mapped[DifficultyLevel] = Column(Enum(DifficultyLevel), nullable=False)
    topic: Mapped[TopicType] = Column(Enum(TopicType), nullable=False)
    constraints: Mapped[str] = Column(Text, nullable=False)
    input_format: Mapped[str] = Column(Text, nullable=False)
    output_format: Mapped[str] = Column(Text, nullable=False)
    starter_code: Mapped[dict] = Column(JSON, nullable=False, default=dict)
    time_limit_ms: Mapped[int] = Column(Integer, nullable=False, default=1000)
    memory_limit_mb: Mapped[int] = Column(Integer, nullable=False, default=256)
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)
    created_by: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    test_cases: Mapped[list["TestCase"]] = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    problem_id: Mapped[int] = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    input_data: Mapped[str] = Column(Text, nullable=False)
    expected_output: Mapped[str] = Column(Text, nullable=False)
    explanation: Mapped[str] = Column(Text, nullable=True)
    is_sample: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    order_index: Mapped[int] = Column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    problem: Mapped[Problem] = relationship("Problem", back_populates="test_cases")


class CodeDraft(Base):
    __tablename__ = "code_drafts"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    problem_id: Mapped[int] = Column(Integer, ForeignKey("problems.id"), nullable=False, index=True)
    language: Mapped[str] = Column(String(50), nullable=False)
    code: Mapped[str] = Column(Text, nullable=False)
    updated_at: Mapped[datetime] = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (UniqueConstraint("student_id", "problem_id", "language", name="uq_code_draft_student_problem_language"),)
