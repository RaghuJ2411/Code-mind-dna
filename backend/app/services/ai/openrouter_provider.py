from openai import OpenAI

from app.core.config import settings
from .base import AIServiceError


class OpenRouterProvider:

    def __init__(self):
        if not settings.openrouter_api_key:
            raise AIServiceError(
                "OpenRouter API key is missing."
            )

        self.client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def generate_structured(self, *args, **kwargs):

        try:
            response = self.client.chat.completions.create(
                model=settings.openrouter_model,
                messages=[
                    {
                        "role": "user",
                        "content": str(kwargs),
                    }
                ],
            )

            return {
                "result": response.choices[0].message.content
            }

        except Exception as e:
            raise AIServiceError(
                f"OpenRouter error: {str(e)}"
            )
