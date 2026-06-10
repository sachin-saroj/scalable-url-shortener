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
