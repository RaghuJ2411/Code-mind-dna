from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DNAProfileStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    NOT_GENERATED = "NOT_GENERATED"


class DNADimensionContribution(BaseModel):
    feature: str
    raw_value: float | None
    normalized_value: float | None
    configured_weight: float
    weighted_contribution: float | None = None


class DNADimension(BaseModel):
    name: str
    score: float | None
    confidence: float | None
    classification: str | None = None
    evidence_status: str
    explanation: str
    contributions: list[DNADimensionContribution]


class DNAProfileResponse(BaseModel):
    profile_status: DNAProfileStatus
    overall_score: float | None = None
    overall_confidence: float | None = None
    confidence_label: str | None = None
    scoring_version: str | None = None
    calculated_at: datetime | None = None
    dimensions: list[DNADimension] = Field(default_factory=list)


class DNAHistoryItem(BaseModel):
    overall_score: float | None
    overall_confidence: float | None
    scoring_version: str
    calculated_at: datetime


class DNAHistoryResponse(BaseModel):
    total: int
    data: list[DNAHistoryItem]


class DNAExplanationResponse(BaseModel):
    dimension: str
    explanation: str
    contributions: list[DNADimensionContribution]


class DNARecalculationResponse(BaseModel):
    success: bool
    message: str
