from __future__ import annotations

from abc import ABC, abstractmethod


class CodeExecutionProvider(ABC):
    @abstractmethod
    def execute_code(
        self,
        source_code: str,
        language: str,
        stdin: str,
        time_limit_ms: int,
        memory_limit_mb: int,
    ) -> dict:
        raise NotImplementedError
