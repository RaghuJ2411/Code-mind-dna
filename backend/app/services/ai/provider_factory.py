from app.core.config import settings
from .client import MockProvider

try:
    from .openai_provider import OpenAIProvider
except Exception:
    OpenAIProvider = None

try:
    from .gemini_provider import GeminiProvider
except Exception:
    GeminiProvider = None


def get_provider():
    provider_name = (settings.ai_provider or "mock").lower()

    if provider_name == "openai" and OpenAIProvider is not None:
        return OpenAIProvider()

    if provider_name == "gemini" and GeminiProvider is not None:
        return GeminiProvider()

    # default to mock provider
    return MockProvider()
