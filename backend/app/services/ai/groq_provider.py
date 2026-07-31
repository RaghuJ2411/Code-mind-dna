from groq import Groq

from app.core.config import settings
from .base import AIServiceError


class GroqProvider:

    def __init__(self):
        if not settings.groq_api_key:
            raise AIServiceError("Groq API key is missing.")

        self.client = Groq(
            api_key=settings.groq_api_key
        )

    def generate_structured(self, *args, **kwargs):

        try:
            response = self.client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {
                        "role": "user",
                        "content": str(kwargs)
                    }
                ],
            )

            return {
                "result": response.choices[0].message.content
            }

        except Exception as e:
            raise AIServiceError(
                f"Groq error: {str(e)}"
            )
