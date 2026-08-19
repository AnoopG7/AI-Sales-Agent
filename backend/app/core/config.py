"""
Core configuration module.

Loads all environment variables via pydantic-settings and exposes
a singleton `settings` object used throughout the application.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- App ---
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    SECRET_KEY: str = "change-me-in-production-min-32-chars"
    LOG_LEVEL: str = "INFO"
    FRONTEND_URL: str = "http://localhost:5173"
    BACKEND_URL: str = "http://localhost:8000"

    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/leadgen"

    # --- LLM Provider ---
    LLM_PROVIDER: str = "groq"  # "groq" or "ollama"
    OLLAMA_MODEL: str = "qwen3:8b"

    # --- Groq ---
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # --- WhatsApp Business API ---
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = ""
    WHATSAPP_APP_SECRET: str = ""
    WHATSAPP_API_VERSION: str = "v23.0"

    # --- Google Calendar ---
    GOOGLE_SERVICE_ACCOUNT_JSON: str = ""
    GOOGLE_CALENDAR_ID: str = "primary"
    GOOGLE_CALENDAR_TIMEZONE: str = "Asia/Dubai"

    # --- Email (SMTP) ---
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    FROM_EMAIL: str = "noreply@example.com"

    # --- Admin ---
    ADMIN_EMAIL: str = ""
    ADMIN_WHATSAPP_NUMBER: str = ""

    # --- Derived ---
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def smtp_is_configured(self) -> bool:
        return bool(self.SMTP_HOST and self.SMTP_USER and self.SMTP_PASS)

    @property
    def cors_origins(self) -> list[str]:
        if self.is_production:
            return [self.FRONTEND_URL]
        return ["*"]

    @property
    def whatsapp_api_url(self) -> str:
        return (
            f"https://graph.facebook.com/{self.WHATSAPP_API_VERSION}"
            f"/{self.WHATSAPP_PHONE_NUMBER_ID}/messages"
        )


@lru_cache
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
