from __future__ import annotations
from typing import Any
from abc import ABC, abstractmethod


class AIServiceError(Exception):
    pass


class LLMProvider(ABC):
    @abstractmethod
    def generate_structured(self, task_type: str, system_prompt: str, context: dict, response_schema: Any, temperature: float = 0.0, max_tokens: int | None = None) -> dict:
        """Generate structured JSON-like output validated against `response_schema`.

        Must return a dict that can be parsed by `response_schema`.
        """
        raise NotImplementedError()
