# ruff: noqa: E402
"""
Test Configuration
───────────────────
Shared fixtures for the test suite.
Supports PostgreSQL (with containers/services) and dynamic SQLite fallback.
"""

import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.types import Uuid

# Monkeypatch PostgreSQL UUID to SQLAlchemy generic Uuid type for SQLite compatibility
pg.UUID = Uuid

import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import BigInteger, event, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.pool import NullPool, StaticPool

# Silence noisy debug logs during testing
logging.getLogger("aiosqlite").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)


# Compiler overrides for SQLite compatibility during testing
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


# Map BigInteger to INTEGER for SQLite to enable autoincrement primary keys
@compiles(BigInteger, "sqlite")
def compile_bigint_sqlite(type_, compiler, **kw):
    return "INTEGER"


# Set environment variables for testing
os.environ["APP_ENV"] = "testing"
if os.environ.get("JWT_SECRET_KEY") in (
    None,
    "change-me",
    "change-this-to-a-very-long-random-string-in-production",
):
    os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-that-is-very-long-and-secure"

if os.environ.get("SECRET_KEY") in (
    None,
    "change-me",
    "change-this-to-a-very-long-random-string-in-production",
):
    os.environ["SECRET_KEY"] = "test-secret-key-that-is-very-long-and-secure"

# Determine DB URL
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    user = os.environ.get("POSTGRES_USER", "shortener")
    password = os.environ.get("POSTGRES_PASSWORD", "test_secret")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db = os.environ.get("POSTGRES_DB", "url_shortener_test")
    database_url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

is_postgres = False
test_engine = None

if database_url.startswith("postgresql"):
    try:
        # Run a quick connection test to see if PostgreSQL is up and accepting connections
        probe_engine = create_async_engine(database_url)

        async def check_probe():
            async with probe_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(check_probe())
            is_postgres = True
        finally:
            loop.close()
            # Dispose the probe engine
            loop = asyncio.new_event_loop()
            loop.run_until_complete(probe_engine.dispose())
            loop.close()

        if is_postgres:
            test_engine = create_async_engine(database_url, poolclass=NullPool)
    except Exception as e:
        print(
            f"\n[INFO] PostgreSQL probe failed ({e}). "
            "Falling back to SQLite in-memory database for testing."
        )
        database_url = "sqlite+aiosqlite:///:memory:"
        test_engine = create_async_engine(
            database_url, poolclass=StaticPool, connect_args={"check_same_thread": False}
        )
else:
    database_url = "sqlite+aiosqlite:///:memory:"
    test_engine = create_async_engine(
        database_url, poolclass=StaticPool, connect_args={"check_same_thread": False}
    )

os.environ["DATABASE_URL"] = database_url

# For SQLite, register missing SQL functions used in server_default
if not is_postgres:

    @event.listens_for(test_engine.sync_engine, "connect")
    def register_sqlite_functions(dbapi_connection, connection_record):
        # Register NOW()
        def now():
            return datetime.now(timezone.utc).isoformat()

        dbapi_connection.create_function("NOW", 0, now)

        # Register gen_random_uuid()
        def gen_random_uuid():
            return str(uuid.uuid4())

        dbapi_connection.create_function("gen_random_uuid", 0, gen_random_uuid)


from sqlalchemy import Boolean

from app.db.base import Base
from app.dependencies import get_cache, get_db, get_redis
from app.main import app
from app.services.cache_service import CacheService


# Convert boolean server defaults to 1/0 for SQLite compatibility
@event.listens_for(Base.metadata, "before_create")
def fix_boolean_defaults(target, connection, **kw):
    if connection.dialect.name == "sqlite":
        for table in target.tables.values():
            for column in table.columns:
                if isinstance(column.type, Boolean):
                    if column.server_default is not None:
                        arg = column.server_default.arg
                        if hasattr(arg, "text"):
                            if arg.text.lower() == "true":
                                column.server_default.arg = text("1")
                            elif arg.text.lower() == "false":
                                column.server_default.arg = text("0")
                        elif isinstance(arg, str):
                            if arg.lower() == "true":
                                column.server_default.arg = "1"
                            elif arg.lower() == "false":
                                column.server_default.arg = "0"


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test to ensure a clean database state."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Test Session Factory
test_session_maker = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

from app.db import session as db_session_module

db_session_module.async_session_factory = test_session_maker


@pytest_asyncio.fixture
async def db_session():
    """Provide a database session."""
    async with test_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def test_redis():
    """Provide a Redis client connected to real Redis or fake redis."""
    redis_host = os.environ.get("REDIS_HOST", "localhost")
    redis_port = int(os.environ.get("REDIS_PORT", "6379"))

    # Try connecting to real Redis service
    real_redis = Redis(
        host=redis_host, port=redis_port, decode_responses=True, socket_connect_timeout=2
    )
    try:
        await real_redis.ping()
        yield real_redis
        await real_redis.flushdb()
        await real_redis.close()
    except Exception:
        # Fallback to fakeredis
        import fakeredis.aioredis

        fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
        yield fake_redis
        await fake_redis.close()


@pytest_asyncio.fixture
async def cache_service(test_redis):
    """Provide a functional CacheService instance (cleaned between tests)."""
    service = CacheService(test_redis)
    try:
        await test_redis.flushdb()
    except Exception:
        await test_redis.flushall()
    yield service


@pytest_asyncio.fixture
async def client(db_session, test_redis, cache_service):
    """Async HTTP client overriding FastAPI app dependencies."""

    async def override_get_db():
        yield db_session

    async def override_get_redis():
        return test_redis

    async def override_get_cache():
        return cache_service

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[get_cache] = override_get_cache

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
