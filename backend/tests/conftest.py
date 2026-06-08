"""
Test Configuration
───────────────────
Shared fixtures for the test suite.
"""

import os
# Set fallback env variables for testing if not already provided
if os.environ.get("JWT_SECRET_KEY") in (None, "change-me", "change-this-to-a-very-long-random-string-in-production"):
    os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-that-is-very-long-and-secure"

if os.environ.get("SECRET_KEY") in (None, "change-me", "change-this-to-a-very-long-random-string-in-production"):
    os.environ["SECRET_KEY"] = "test-secret-key-that-is-very-long-and-secure"

if not os.environ.get("DATABASE_URL"):
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "postgres")
    host = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5432")
    db = os.environ.get("POSTGRES_DB", "test_db")
    os.environ["DATABASE_URL"] = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest_asyncio.fixture
async def client():
    """Async HTTP client for testing FastAPI endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
