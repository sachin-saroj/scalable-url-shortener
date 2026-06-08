"""
Database Session Management
────────────────────────────
Async SQLAlchemy session factory with connection pooling.

KEY DECISIONS:
- AsyncSession: Non-blocking DB queries (matches FastAPI's async nature)
- Connection pooling: pool_size=20, max_overflow=10 (handles burst traffic)
- expire_on_commit=False: Prevents lazy-load issues after commit

SCALABILITY:
- Pool size should be tuned based on expected concurrent connections
- PostgreSQL default max_connections=100, so pool_size + max_overflow < 100
"""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

settings = get_settings()

# Ensure DATABASE_URL is not None for MyPy
db_url = settings.DATABASE_URL
assert db_url is not None, "DATABASE_URL is not configured"

# ── Async Engine ───────────────────────────────────────
engine_kwargs: dict[str, Any] = {
    "echo": settings.APP_DEBUG,  # Log SQL in dev mode
    "pool_pre_ping": True,  # Test connections before use
}
if not db_url.startswith("sqlite"):
    engine_kwargs["pool_size"] = 20  # Persistent connections
    engine_kwargs["max_overflow"] = 10  # Burst connections
    engine_kwargs["pool_recycle"] = 3600  # Recycle connections every hour

engine = create_async_engine(db_url, **engine_kwargs)

# ── Session Factory ────────────────────────────────────
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Keep objects usable after commit
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection for database sessions.

    Usage in FastAPI:
        @router.get("/")
        async def handler(db: AsyncSession = Depends(get_db)):
            ...

    WHY async context manager?
    - Ensures session is always closed (even on exceptions)
    - Automatic rollback on unhandled errors
    - Clean resource lifecycle management
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
