"""
Application Configuration
─────────────────────────
Centralized settings loaded from environment variables.
Uses pydantic-settings for type-safe, validated configuration.

WHY pydantic-settings?
- Auto-loads from .env files
- Type coercion (str → int, bool)
- Validation at startup (fail fast, not at runtime)
- Immutable after creation (prevents accidental mutation)
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All application settings in one place."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ────────────────────────────
    APP_NAME: str = "url-shortener"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    BASE_URL: str = "http://localhost:8000"
    API_V1_PREFIX: str = "/api/v1"

    # ── Database ───────────────────────────────
    POSTGRES_USER: str = "shortener"
    POSTGRES_PASSWORD: str = "shortener_secret_2026"
    POSTGRES_DB: str = "url_shortener"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Synchronous URL for Alembic migrations."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ── Redis ──────────────────────────────────
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # ── JWT ────────────────────────────────────
    JWT_SECRET_KEY: str = "change-this-to-a-very-long-random-string-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Rate Limiting ─────────────────────────
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ── Celery ─────────────────────────────────
    @property
    def CELERY_BROKER_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/2"

    # ── Cache ──────────────────────────────────
    URL_CACHE_TTL: int = 86400  # 24 hours

    # ── External APIs ──────────────────────────
    GOOGLE_SAFE_BROWSING_API_KEY: str = ""

    # ── CORS ───────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    
    WHY lru_cache?
    - Settings are read-only after startup
    - Parsing .env on every request is wasteful
    - Single instance shared across the app
    """
    return Settings()
