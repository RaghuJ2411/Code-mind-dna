from __future__ import annotations

import json
import time
from typing import Any

import httpx

from app.core.config import settings
from .base import LLMProvider, AIServiceError


class GeminiProvider(LLMProvider):

    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model = settings.gemini_model
        self.timeout = settings.ai_request_timeout_seconds

    def generate_structured(
        self,
        task_type: str,
        system_prompt: str,
        context: dict,
        response_schema: Any,
        temperature: float = 0.0,
        max_tokens: int | None = None,
    ) -> dict:

        if not settings.ai_enabled:
            raise AIServiceError("AI_DISABLED")

        if not self.api_key:
            raise AIServiceError("CONFIGURATION_ERROR")

        prompt = (
            system_prompt
            + "\n\nReturn ONLY valid JSON.\n\n"
            + json.dumps(context, default=str)
        )

        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        start = time.time()

        try:

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload)

            latency = int((time.time() - start) * 1000)

        except httpx.ReadTimeout:
            raise AIServiceError("TIMEOUT")

        except Exception:
            raise AIServiceError("PROVIDER_UNAVAILABLE")

        if response.status_code == 429:
            raise AIServiceError("RATE_LIMITED")

        if response.status_code >= 500:
            raise AIServiceError("PROVIDER_UNAVAILABLE")

        try:
            body = response.json()
        except Exception:
            raise AIServiceError("INVALID_RESPONSE")

        try:
            text = body["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            raise AIServiceError("INVALID_RESPONSE")

        try:
            parsed = json.loads(text)
        except Exception:
            parsed = {"message": text}

        return {
            "result": parsed,
            "meta": {
                "provider": "gemini",
                "model": self.model,
                "latency_ms": latency,
            },
        }
