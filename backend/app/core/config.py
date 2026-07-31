from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CodeMind DNA API"
    api_v1_prefix: str = "/api"

    # ==========================================================
    # Database
    # ==========================================================

    database_url: str = "sqlite:///./codemind_dna.db"

    # ==========================================================
    # Security
    # ==========================================================

    jwt_secret_key: str = "dev-secret-key-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # ==========================================================
    # CORS
    # ==========================================================

    cors_origins: str = (
        "http://localhost:5173,"
        "http://127.0.0.1:5173,"
        "http://localhost:5174,"
        "http://127.0.0.1:5174,"
        "http://localhost:5175,"
        "http://127.0.0.1:5175,"
        "https://code-mind-dnast.onrender.com,"
        "https://code-mind-dnas.onrender.com"
    )

    # ==========================================================
    # Security headers
    # ==========================================================

    security_headers_enabled: bool = True
    hsts_max_age_seconds: int = 31536000

    content_security_policy: str = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "img-src 'self' data: https://fastapi.tiangolo.com; "
        "font-src 'self' data: https://cdn.jsdelivr.net; "
        "connect-src 'self' https://codemind-dna-api.onrender.com http://localhost:*;"
    )

    # ==========================================================
    # Request limits
    # ==========================================================

    max_request_body_size_mb: int = 10

    # ==========================================================
    # Authentication
    # ==========================================================

    auth_rate_limit_attempts: int = 5
    auth_rate_limit_window_seconds: int = 900

    # ==========================================================
    # Password policy
    # ==========================================================

    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digit: bool = True
    password_require_special_char: bool = True

    # ==========================================================
    # Code execution
    # ==========================================================

    code_execution_provider: str = "local"
    code_execution_base_url: str = ""
    code_execution_api_key: str = ""
    code_execution_timeout_seconds: int = 10
    coding_session_idle_minutes: int = 30
    min_topic_attempts_for_classification: int = 3
    min_problems_for_progression: int = 5
    min_accepted_for_optimization: int = 2

    # ==========================================================
    # AI configuration
    # ==========================================================

    ai_enabled: bool = False
    ai_provider: str = "mock"

    # OpenAI

    ai_model: str = "gpt-4"
    ai_api_key: str = ""
    ai_base_url: str = ""

    # Gemini

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # Groq

    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"

    # OpenRouter

    openrouter_api_key: str = ""
    openrouter_model: str = "meta-llama/llama-3.1-8b-instruct"

    ai_request_timeout_seconds: int = 30
    ai_max_retries: int = 2
    ai_max_input_tokens: int | None = None
    ai_max_output_tokens: int | None = None

    ai_daily_limits_code_review: int = 10
    ai_daily_limits_error_explain: int = 15
    ai_daily_limits_skill_gap: int = 10
    ai_daily_limits_roadmap: int = 2

    # ==========================================================
    # Logging
    # ==========================================================

    log_level: str = "INFO"
    log_format: str = "json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> List[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def jwt_secret(self) -> str:
        return self.jwt_secret_key

    def validate_production(self) -> List[str]:
        warnings = []

        if self.jwt_secret_key == "dev-secret-key-change-me":
            warnings.append(
                "JWT_SECRET_KEY is set to the default insecure value"
            )

        if self.ai_enabled:

            if self.ai_provider == "openai" and not self.ai_api_key:
                warnings.append(
                    "AI_PROVIDER=openai but AI_API_KEY is not set"
                )

            if self.ai_provider == "gemini" and not self.gemini_api_key:
                warnings.append(
                    "AI_PROVIDER=gemini but GEMINI_API_KEY is not set"
                )

            if self.ai_provider == "groq" and not self.groq_api_key:
                warnings.append(
                    "AI_PROVIDER=groq but GROQ_API_KEY is not set"
                )

            if (
                self.ai_provider == "openrouter"
                and not self.openrouter_api_key
            ):
                warnings.append(
                    "AI_PROVIDER=openrouter but OPENROUTER_API_KEY is not set"
                )

        if self.database_url.startswith("sqlite"):
            warnings.append(
                "Using SQLite in production is not recommended."
            )

        return warnings


settings = Settings()
