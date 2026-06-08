"""
Test Configuration
───────────────────
Shared fixtures for the test suite.
"""

import os
# Set valid non-default secrets and database URL for testing environment
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-key-that-is-very-long-and-secure"
os.environ["SECRET_KEY"] = "test-secret-key-that-is-very-long-and-secure"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"

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
