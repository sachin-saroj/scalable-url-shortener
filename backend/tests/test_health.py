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
