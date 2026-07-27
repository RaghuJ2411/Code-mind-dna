from __future__ import annotations
from typing import Any
import time

from .base import LLMProvider


class MockProvider(LLMProvider):
    def generate_structured(self, task_type: str, system_prompt: str, context: dict, response_schema: Any, temperature: float = 0.0, max_tokens: int | None = None) -> dict:
        # Simple deterministic mock for development and tests.
        start = time.time()
        # Use task_type to produce a small structured example
        if task_type == "CODE_REVIEW":
            result = {
                "summary": "Mock code review: small function looks fine.",
                "correctness_observations": ["No obvious correctness issues found."],
                "code_quality_observations": ["Consider adding docstrings."],
                "complexity": {"time_complexity": "O(n)", "space_complexity": "O(1)", "confidence": "LOW"},
                "improvements": [{"title": "Add comments", "reason": "Improve readability", "priority": "LOW"}],
                "learning_points": ["Modularize logic into smaller functions."],
            }
        else:
            result = {"message": "mock response"}

        # Return a shallow metadata wrapper expected by higher-level services
        return {"result": result, "meta": {"model": "mock", "latency_ms": int((time.time() - start) * 1000)}}
