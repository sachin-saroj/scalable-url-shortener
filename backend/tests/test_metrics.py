"""
Tests for Prometheus Metrics
────────────────────────────
"""

import pytest


@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    """Metrics endpoint should return 200 and include default metrics."""
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

    # Check that HTTP metrics exist in payload
    content = response.text
    assert (
        "linkforge_http_requests_total" in content or "promhttp_metric_handler_requests" in content
    )


@pytest.mark.asyncio
async def test_metrics_middleware_tracks_requests(client):
    """Metrics middleware should count requests and track latency."""
    # Run a dummy request to trigger the middleware
    await client.get("/health")  # Should be excluded from tracking
    await client.get("/api/v1/urls")  # This path is not excluded, should be tracked

    response = await client.get("/metrics")
    assert response.status_code == 200
    content = response.text

    # Verify our custom HTTP counter exists in the metrics output
    assert "linkforge_http_requests_total" in content
    # Verify the path label is present
    assert 'path="/api/v1/urls"' in content
