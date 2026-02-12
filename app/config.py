from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    cors_origins: str = "http://localhost:5173"
    model_dir: str = str(Path(__file__).resolve().parent.parent / "models")
    supabase_url: str | None = None
    supabase_service_key: str | None = None
    legal_generation_limit: int = 64
    legal_generation_window_minutes: int = 60
    default_steps: int = 16

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow",
        protected_namespaces=("settings_",),
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
