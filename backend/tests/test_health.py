"""
Tests for API Health Check
───────────────────────────
"""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """Health endpoint should return 200 with service name."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert "service" in data


@pytest.mark.asyncio
async def test_liveness_check(client):
    """Liveness endpoint should return 200 and healthy status."""
    response = await client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


@pytest.mark.asyncio
async def test_readiness_check(client):
    """Readiness endpoint should return 200 and connect statuses for all deps."""
    response = await client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["postgres"] == "connected"
    assert data["redis"] == "connected"
    assert "postgres_dialect" in data
    assert "postgres_driver" in data


@pytest.mark.asyncio
async def test_readiness_check_postgres_failure(client):
    """Readiness endpoint should return 503 when Postgres is down."""
    from unittest.mock import AsyncMock

    from app.dependencies import get_db

    mock_session = AsyncMock()
    mock_session.execute.side_effect = Exception("DB Connection refused")
    mock_session.bind = None

    async def override_get_db():
        yield mock_session

    from app.main import app

    app.dependency_overrides[get_db] = override_get_db

    try:
        response = await client.get("/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["postgres"] == "disconnected"
        assert data["redis"] == "connected"
    finally:
        if get_db in app.dependency_overrides:
            del app.dependency_overrides[get_db]


@pytest.mark.asyncio
async def test_readiness_check_redis_failure(client):
    """Readiness endpoint should return 503 when Redis is down."""
    from unittest.mock import AsyncMock

    from app.dependencies import get_redis

    mock_redis = AsyncMock()
    mock_redis.ping.side_effect = Exception("Redis Connection refused")

    async def override_get_redis():
        return mock_redis

    from app.main import app

    app.dependency_overrides[get_redis] = override_get_redis

    try:
        response = await client.get("/health/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"
        assert data["postgres"] == "connected"
        assert data["redis"] == "disconnected"
    finally:
        if get_redis in app.dependency_overrides:
            del app.dependency_overrides[get_redis]
