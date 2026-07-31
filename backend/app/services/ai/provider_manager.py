from .base import AIServiceError
from .gemini_provider import GeminiProvider
from .groq_provider import GroqProvider
from .openrouter_provider import OpenRouterProvider


class ProviderManager:

    def __init__(self):
        self.gemini = GeminiProvider()
        self.groq = GroqProvider()
        self.openrouter = OpenRouterProvider()

    def generate_structured(self, *args, **kwargs):

        try:
            return self.gemini.generate_structured(
                *args,
                **kwargs
            )

        except Exception:
            print("Gemini failed.")

        try:
            return self.groq.generate_structured(
                *args,
                **kwargs
            )

        except Exception:
            print("Groq failed.")

        try:
            return self.openrouter.generate_structured(
                *args,
                **kwargs
            )

        except Exception:
            print("OpenRouter failed.")

        raise AIServiceError("All providers failed.")
