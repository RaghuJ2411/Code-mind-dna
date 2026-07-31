from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.groq_api_key)


class GroqProvider:

    def generate_structured(self, *args, **kwargs):

        response = client.chat.completions.create(
            model=settings.groq_model,
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
