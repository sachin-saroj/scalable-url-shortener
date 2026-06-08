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

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config import get_settings

settings = get_settings()

# ── Async Engine ───────────────────────────────────────
engine_kwargs = {
    "echo": settings.APP_DEBUG,           # Log SQL in dev mode
    "pool_pre_ping": True,                # Test connections before use
}
if not settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["pool_size"] = 20       # Persistent connections
    engine_kwargs["max_overflow"] = 10    # Burst connections
    engine_kwargs["pool_recycle"] = 3600  # Recycle connections every hour

engine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs
)

# ── Session Factory ────────────────────────────────────
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,            # Keep objects usable after commit
)


async def get_db() -> AsyncSession:
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
