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

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.services.cache_service import CacheService
from app.services.auth_service import AuthService
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


async def close_redis():
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


async def check_rate_limit(
    request: Request,
    limiter: RateLimiter = Depends(get_rate_limiter),
):
    """
    Rate limiting dependency.
    
    Add to any endpoint:
        @router.post("/shorten", dependencies=[Depends(check_rate_limit)])
    """
    # Get client IP (handle proxy forwarding)
    client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    if not client_ip:
        client_ip = request.client.host if request.client else "unknown"

    allowed, info = await limiter.is_allowed(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=info["detail"],
            headers={"Retry-After": str(info["retry_after"])},
        )


# ── Authentication ────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Mandatory authentication dependency.
    Raises 401 if token is invalid or missing.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    auth_service = AuthService(db)
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    Optional authentication dependency.
    Returns None if no token provided (allows anonymous access).
    Raises 401 only if token is present but invalid.
    """
    if not credentials:
        return None

    auth_service = AuthService(db)
    try:
        user = await auth_service.get_current_user(credentials.credentials)
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
