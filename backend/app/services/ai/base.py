from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AIServiceError(Exception):
    """
    Base exception for all AI provider errors.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return self.message


class LLMProvider(ABC):
    """
    Base class for all LLM providers.
    """

    @abstractmethod
    def generate_structured(
        self,
        task_type: str,
        system_prompt: str,
        context: dict,
        response_schema: Any,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> dict:
        """
        Generate structured output from an AI model.

        Parameters
        ----------
        task_type : str
            Type of task being performed.

        system_prompt : str
            System instructions for the model.

        context : dict
            Input data for the model.

        response_schema : Any
            Schema used to validate the response.

        temperature : float
            Controls randomness.

        max_tokens : int | None
            Maximum number of tokens.

        Returns
        -------
        dict
            Structured response.
        """
        raise NotImplementedError(
            "Subclasses must implement generate_structured()."
        )
