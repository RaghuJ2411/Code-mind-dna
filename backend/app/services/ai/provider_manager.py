from .base import AIServiceError
from .gemini_provider import GeminiProvider
from .groq_provider import GroqProvider
from .openrouter_provider import OpenRouterProvider


class ProviderManager:

    def __init__(self):

        self.gemini = None
        self.groq = None
        self.openrouter = None

        try:
            self.gemini = GeminiProvider()
            print("Gemini initialized successfully.")
        except Exception as e:
            print(f"Gemini initialization failed: {e}")

        try:
            self.groq = GroqProvider()
            print("Groq initialized successfully.")
        except Exception as e:
            print(f"Groq initialization failed: {e}")

        try:
            self.openrouter = OpenRouterProvider()
            print(f"OpenRouter initialization failed: {e}")

    def generate_structured(self, *args, **kwargs):

        if self.gemini:
            try:
                print("Trying Gemini...")
                return self.gemini.generate_structured(
                    *args,
                    **kwargs
                )
            except Exception as e:
                print(f"Gemini failed: {e}")

        if self.groq:
            try:
                print("Trying Groq...")
                return self.groq.generate_structured(
                    *args,
                    **kwargs
                )
            except Exception as e:
                print(f"Groq failed: {e}")

        if self.openrouter:
            try:
                print("Trying OpenRouter...")
                return self.openrouter.generate_structured(
                    *args,
                    **kwargs
                )
            except Exception as e:
                print(f"OpenRouter failed: {e}")

        raise AIServiceError("All providers failed.")
