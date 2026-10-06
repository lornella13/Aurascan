from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # "gemini" (free key from Google AI Studio) or "anthropic" (paid)
    vision_provider: str = "gemini"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5-5"

    max_upload_mb: int = 8
    allowed_origins: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()
