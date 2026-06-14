"""
Dependency Injection
─────────────────────
FastAPI dependency functions for database, Redis, auth, and rate limiting.

WHY dependency injection?
- Clean separation of concerns
- Easy to test (swap real deps with mocks)
- Centralized resource lifecycle management
- FastAPI handles cleanup automatically
"""

import logging
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import get_db as get_db
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.cache_service import CacheService
from app.utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)
settings = get_settings()

# ── HTTP Bearer token scheme ──────────────────────────
security = HTTPBearer(auto_error=False)

# ── Global Redis connection ───────────────────────────
_redis: Redis | None = None


async def get_redis() -> Redis:
    """Get or create Redis connection."""
    global _redis
    if _redis is None:
        _redis = Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            retry_on_timeout=True,
        )
    return _redis


async def close_redis() -> None:
    """Close Redis connection (called on shutdown)."""
    global _redis
    if _redis:
        await _redis.close()
        _redis = None


# ── Cache Service ─────────────────────────────────────


async def get_cache(redis: Redis = Depends(get_redis)) -> CacheService:
    """Inject CacheService with Redis connection."""
    return CacheService(redis)


# ── Rate Limiter ──────────────────────────────────────


async def get_rate_limiter(redis: Redis = Depends(get_redis)) -> RateLimiter:
    """Inject RateLimiter with Redis connection."""
    return RateLimiter(
        redis,
        max_requests=settings.RATE_LIMIT_REQUESTS,
        window_seconds=settings.RATE_LIMIT_WINDOW_SECONDS,
    )


class RateLimitRule:
    """
    Customizable rate limiting dependency creator.

    Allows customizing max_requests and window_seconds per endpoint,
    while scoping keys to the endpoint path to prevent starvation.
    """

    def __init__(self, max_requests: int | None = None, window_seconds: int | None = None):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def __call__(
        self,
        request: Request,
        redis: Redis = Depends(get_redis),
    ):
        # Get client IP and handle proxy forwarding securely
        from app.utils.client_ip import get_client_ip

        client_ip = get_client_ip(request)

        # Scope the key to the specific endpoint path to prevent cross-endpoint starvation
        identifier = f"{client_ip}:{request.url.path}"

        # Apply limits (fallback to settings if not customized)
        limit = self.max_requests if self.max_requests is not None else settings.RATE_LIMIT_REQUESTS
        window = (
            self.window_seconds
            if self.window_seconds is not None
            else settings.RATE_LIMIT_WINDOW_SECONDS
        )

        limiter = RateLimiter(redis, max_requests=limit, window_seconds=window)
        allowed, info = await limiter.is_allowed(identifier)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=info["detail"],
                headers={"Retry-After": str(info["retry_after"])},
            )


# Default rate limit (applies settings defaults, but scoped by path)
check_rate_limit = RateLimitRule()

# Tight rate limits for sensitive/authentication endpoints (e.g., login, register)
check_auth_rate_limit = RateLimitRule(max_requests=5, window_seconds=60)


# ── Authentication ────────────────────────────────────


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Mandatory authentication dependency.
    Raises 401 if token is invalid or missing.
    Supports both Authorization Bearer header and access_token cookie.
    """
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header:
        parts = auth_header.split(" ")
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    if not token:
        token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_service = AuthService(db)
    try:
        user = await auth_service.get_current_user(token)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    Optional authentication dependency.
    Returns None if no token provided (allows anonymous access).
    Raises 401 only if token is present but invalid.
    Supports both Authorization Bearer header and access_token cookie.
    """
    token = None
    auth_header = request.headers.get("Authorization")
    if auth_header:
        parts = auth_header.split(" ")
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]

    if not token:
        token = request.cookies.get("access_token")

    if not token:
        return None

    auth_service = AuthService(db)
    try:
        user = await auth_service.get_current_user(token)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_admin(
    user: User = Depends(get_current_user),
) -> User:
    """Require admin role."""
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


# Type aliases for cleaner route signatures
DB = Annotated[AsyncSession, Depends(get_db)]
Cache = Annotated[CacheService, Depends(get_cache)]
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
AdminUser = Annotated[User, Depends(require_admin)]
