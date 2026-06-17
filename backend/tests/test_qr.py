"""
Tests for QR Code Endpoint
────────────────────────────
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch
from app.models.url import URL


class TestQREndpoint:
    """Test QR code generation API endpoint."""

    @pytest.mark.asyncio
    @patch("app.api.v1.qr.generate_qr_code")
    async def test_generate_qr_success(self, mock_gen_qr, client: AsyncClient, db_session):
        # Setup dummy URL
        url_record = URL(
            original_url="https://example.com",
            short_code="qrtest",
            is_active=True
        )
        db_session.add(url_record)
        await db_session.commit()

        mock_gen_qr.return_value = b"dummy_png_data"

        response = await client.get("/api/v1/qr/qrtest?size=15")
        assert response.status_code == 200
        assert response.content == b"dummy_png_data"
        assert response.headers["content-type"] == "image/png"
        mock_gen_qr.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_qr_not_found(self, client: AsyncClient):
        response = await client.get("/api/v1/qr/doesnotexist")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_generate_qr_invalid_size_too_small(self, client: AsyncClient):
        response = await client.get("/api/v1/qr/doesnotexist?size=2")
        assert response.status_code == 422  # validation error from ge=5

    @pytest.mark.asyncio
    async def test_generate_qr_invalid_size_too_large(self, client: AsyncClient):
        response = await client.get("/api/v1/qr/doesnotexist?size=25")
        assert response.status_code == 422  # validation error from le=20
