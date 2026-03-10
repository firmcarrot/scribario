"""Scribario configuration — loaded from environment variables via pydantic-settings."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # Telegram
    telegram_bot_token: str = ""

    # Anthropic (Claude)
    anthropic_api_key: str = ""

    # Kie.ai (image generation)
    kie_ai_api_key: str = ""

    # ElevenLabs (Phase 2)
    elevenlabs_api_key: str = ""

    # Postiz
    postiz_url: str = "http://localhost:5000"
    postiz_api_key: str = ""

    # Worker
    max_worker_concurrency: int = 3
    worker_poll_interval_seconds: int = 5

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    """Lazy-load settings singleton. Validates env vars only when first called."""
    return Settings()
