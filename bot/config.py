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

    # Meta (Facebook / Instagram / Threads)
    facebook_app_id: str = ""
    facebook_app_secret: str = ""

    # Postiz
    postiz_url: str = "https://postiz.scribario.com"
    postiz_api_key: str = ""
    postiz_org_id: str = ""
    postiz_session_token: str = ""
    postiz_jwt_secret: str = ""

    # OAuth connect proxy
    connect_base_url: str = "https://connect.scribario.com"

    # Stripe
    stripe_api_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_starter_price_id: str = ""
    stripe_growth_price_id: str = ""
    stripe_pro_price_id: str = ""

    # Redis (FSM storage for bot state)
    redis_url: str = "redis://localhost:6379/0"

    # Worker
    max_worker_concurrency: int = 3
    worker_poll_interval_seconds: int = 5

    # Long video pipeline
    long_video_max_cost_usd: float = 10.0

    # Autopilot hard ceilings
    autopilot_max_daily_posts: int = 10
    autopilot_max_monthly_cost_usd: float = 100.0

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    """Lazy-load settings singleton. Validates env vars only when first called."""
    return Settings()
