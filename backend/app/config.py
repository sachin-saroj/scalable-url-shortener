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

from pydantic import model_validator
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
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str | None = None

    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Synchronous URL for Alembic migrations."""
        if not self.DATABASE_URL:
            raise RuntimeError("DATABASE_URL is missing.")
        url = self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        return url.replace("sqlite+aiosqlite://", "sqlite://")

    # ── Redis ──────────────────────────────────
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    # ── JWT ────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me"
    SECRET_KEY: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Rate Limiting ─────────────────────────
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ── Celery ─────────────────────────────────
    @property
    def CELERY_BROKER_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/1"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/1"

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/2"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/2"

    # ── Cache ──────────────────────────────────
    URL_CACHE_TTL: int = 86400  # 24 hours

    # ── External APIs ──────────────────────────
    GOOGLE_SAFE_BROWSING_API_KEY: str = ""

    # ── CORS ───────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # ── Trusted Proxies ────────────────────────
    TRUSTED_PROXIES: str = ""  # comma-separated IPs of reverse proxies (e.g., "172.18.0.1")

    @property
    def trusted_proxies_list(self) -> list[str]:
        return [ip.strip() for ip in self.TRUSTED_PROXIES.split(",") if ip.strip()]

    @property
    def cors_origins_list(self) -> list[str]:
        if not self.CORS_ORIGINS:
            return []
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        if self.APP_ENV.lower() == "production":
            # Remove localhost, 127.0.0.1, 0.0.0.0, and wildcard in production
            filtered = []
            for origin in origins:
                lower_origin = origin.lower()
                if (
                    "localhost" in lower_origin
                    or "127.0.0.1" in lower_origin
                    or "0.0.0.0" in lower_origin
                ):
                    continue
                if origin == "*":
                    continue
                filtered.append(origin)
            return filtered
        return origins

    @model_validator(mode="after")
    def validate_secrets(self) -> "Settings":
        # Check JWT_SECRET_KEY
        if self.JWT_SECRET_KEY in (
            "change-this-to-a-very-long-random-string-in-production",
            "change-me",
            "",
        ):
            raise RuntimeError("JWT_SECRET_KEY must be changed from the default value.")

        # Check SECRET_KEY
        if self.SECRET_KEY in (
            "change-me",
            "change-this-to-a-very-long-random-string-in-production",
            "",
        ):
            raise RuntimeError("SECRET_KEY must be changed from the default value.")

        # Construct or validate DATABASE_URL
        if not self.DATABASE_URL:
            if (
                self.POSTGRES_USER
                and self.POSTGRES_PASSWORD
                and self.POSTGRES_HOST
                and self.POSTGRES_DB
            ):
                self.DATABASE_URL = (
                    f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                    f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
                )
            else:
                raise RuntimeError("DATABASE_URL is missing from environment.")

        return self


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance.

    WHY lru_cache?
    - Settings are read-only after startup
    - Parsing .env on every request is wasteful
    - Single instance shared across the app
    """
    return Settings()
