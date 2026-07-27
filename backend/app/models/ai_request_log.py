from __future__ import annotations
from sqlalchemy import Column, Integer, String, DateTime, JSON
from app.core.database import Base


class AIRequestLog(Base):
    __tablename__ = "ai_request_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True)
    task_type = Column(String(100), nullable=False)
    provider = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    prompt_version = Column(String(50), nullable=True)
    status = Column(String(50), nullable=False)
    input_token_count = Column(Integer, nullable=True)
    output_token_count = Column(Integer, nullable=True)
    latency_ms = Column(Integer, nullable=True)
    error_category = Column(String(200), nullable=True)
    request_metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=True)
