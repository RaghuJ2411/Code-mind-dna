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

        # ==================================================
        # Try Gemini
        # ==================================================

        try:
            print("=" * 50)
            print("Trying Gemini provider...")
            print("=" * 50)

            result = self.gemini.generate_structured(
                *args,
                **kwargs
            )

            print("Gemini succeeded.")
            return result

        except Exception as e:
            print(f"Gemini failed: {e}")

        # ==================================================
        # Try Groq
        # ==================================================

        try:
            print("=" * 50)
            print("Trying Groq provider...")
            print("=" * 50)

            result = self.groq.generate_structured(
                *args,
                **kwargs
            )

            print("Groq succeeded.")
            return result

        except Exception as e:
            print(f"Groq failed: {e}")

        # ==================================================
        # Try OpenRouter
        # ==================================================

        try:
            print("=" * 50)
            print("Trying OpenRouter provider...")
            print("=" * 50)

            result = self.openrouter.generate_structured(
                *args,
                **kwargs
            )

            print("OpenRouter succeeded.")
            return result

        except Exception as e:
            print(f"OpenRouter failed: {e}")

        # ==================================================
        # All providers failed
        # ==================================================

        raise AIServiceError(
            "All AI providers failed."
        )
