"""
GLOWUP AI — Configurazione centralizzata
Carica da .env con fallback sensati. Usa Pydantic per validazione.
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ─── ENVIRONMENT ───
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # ─── DATABASE ───
    database_url: str = "postgresql://postgres:postgres@localhost:54322/glowup_ai"
    database_pool_size: int = 10
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    jwt_secret: str = "dev-secret-change-me-in-production"

    # ─── REDIS ───
    redis_url: str = "redis://localhost:6379/0"

    # ─── STORAGE ───
    r2_endpoint: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = "glowup-uploads"
    r2_public_url: str = ""

    # ─── LLM ───
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    mistral_api_key: str = ""
    mistral_model: str = "mistral-large-latest"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    llm_provider: str = "deepseek"  # deepseek | mistral | openai

    # ─── STRIPE ───
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_id: str = ""

    # ─── EMAIL ───
    resend_api_key: str = ""
    email_from: str = "glowup@example.com"

    # ─── ANALISI ───
    max_photo_size_mb: int = 10
    allowed_photo_formats: str = "jpg,jpeg,png,webp"
    required_photo_count: int = 6
    min_face_confidence: float = 0.95
    analysis_timeout_seconds: int = 600

    # ─── SICUREZZA ───
    encryption_key: str = "dev-key-change-me"
    cors_origins: str = "http://localhost:3000"
    rate_limit_per_minute: int = 30

    # ─── SENTRY ───
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 0.1

    # ─── FAL.AI (Face transformation) ───
    replicate_api_token: str = ""
    fal_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
