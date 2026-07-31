from openai import OpenAI
from app.core.config import settings

client = OpenAI(
    api_key=settings.openrouter_api_key,
    base_url="https://openrouter.ai/api/v1"
)


class OpenRouterProvider:

    def generate_structured(self, *args, **kwargs):

        response = client.chat.completions.create(
            model=settings.openrouter_model,
            messages=[
                {
                    "role": "user",
                    "content": str(kwargs)
                }
            ]
        )

        return {
            "result": response.choices[0].message.content
        }
