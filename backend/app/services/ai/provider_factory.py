from app.core.config import settings
from .client import MockProvider
from .provider_manager import ProviderManager

try:
    from .openai_provider import OpenAIProvider
except Exception:
    OpenAIProvider = None


def get_provider():
    provider_name = (settings.ai_provider or "mock").lower()

    if provider_name == "openai" and OpenAIProvider is not None:
        return OpenAIProvider()

    if provider_name == "gemini":
        return ProviderManager()

    return MockProvider()
