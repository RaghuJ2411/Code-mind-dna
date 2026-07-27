from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped

from app.core.database import Base


class CodingDNAProfile(Base):
    __tablename__ = "coding_dna_profiles"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    student_id: Mapped[int] = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    overall_score: Mapped[float | None] = Column(Float, nullable=True)
    overall_confidence: Mapped[float | None] = Column(Float, nullable=True)

    logic_score: Mapped[float | None] = Column(Float, nullable=True)
    logic_confidence: Mapped[float | None] = Column(Float, nullable=True)
    debugging_score: Mapped[float | None] = Column(Float, nullable=True)
    debugging_confidence: Mapped[float | None] = Column(Float, nullable=True)
    optimization_score: Mapped[float | None] = Column(Float, nullable=True)
    optimization_confidence: Mapped[float | None] = Column(Float, nullable=True)
    consistency_score: Mapped[float | None] = Column(Float, nullable=True)
    consistency_confidence: Mapped[float | None] = Column(Float, nullable=True)
    learning_velocity_score: Mapped[float | None] = Column(Float, nullable=True)
    learning_velocity_confidence: Mapped[float | None] = Column(Float, nullable=True)
    breadth_score: Mapped[float | None] = Column(Float, nullable=True)
    breadth_confidence: Mapped[float | None] = Column(Float, nullable=True)

    evidence_status: Mapped[str] = Column(String(50), nullable=False)
    scoring_version: Mapped[str] = Column(String(20), nullable=False)
    feature_snapshot_json: Mapped[dict] = Column(JSON, nullable=False, default=dict)
    explanation_snapshot_json: Mapped[dict] = Column(JSON, nullable=False, default=dict)

    calculated_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    created_at: Mapped[datetime] = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    __table_args__ = ()
