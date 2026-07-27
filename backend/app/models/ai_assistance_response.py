from __future__ import annotations
from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.core.database import Base


class AIAssistanceResponse(Base):
    __tablename__ = "ai_assistance_responses"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, nullable=False)
    submission_id = Column(Integer, nullable=True)
    task_type = Column(String(100), nullable=False)
    response_json = Column(JSON, nullable=False)
    prompt_version = Column(String(50), nullable=True)
    provider = Column(String(100), nullable=True)
    model_name = Column(String(100), nullable=True)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
