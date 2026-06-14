from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.models.url import URL
from app.services.metadata_service import fetch_url_metadata
from app.services.url_service import _fetch_and_store_metadata


@pytest.mark.asyncio
async def test_fetch_url_metadata_success():
    """Verify that fetch_url_metadata correctly parses standard HTML elements and OG tags."""
    html_content = """
    <html>
        <head>
            <title>Test Title</title>
            <meta name="description" content="Test Description">
            <meta property="og:image" content="https://example.com/test.jpg">
        </head>
        <body></body>
    </html>
    """

    mock_response = MagicMock()
    mock_response.headers = {"content-type": "text/html; charset=utf-8"}
    mock_response.text = html_content

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await fetch_url_metadata("https://example.com/some-page")

        assert result["title"] == "Test Title"
        assert result["description"] == "Test Description"
        assert result["og_image"] == "https://example.com/test.jpg"


@pytest.mark.asyncio
async def test_fetch_url_metadata_og_fallback():
    """Verify that fetch_url_metadata falls back to og:title and og:description."""
    html_content = """
    <html>
        <head>
            <meta property="og:title" content="OG Title">
            <meta property="og:description" content="OG Description">
        </head>
        <body></body>
    </html>
    """

    mock_response = MagicMock()
    mock_response.headers = {"content-type": "text/html"}
    mock_response.text = html_content

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await fetch_url_metadata("https://example.com/some-page")

        assert result["title"] == "OG Title"
        assert result["description"] == "OG Description"


@pytest.mark.asyncio
async def test_fetch_url_metadata_non_html():
    """Verify that fetch_url_metadata returns empty dict if content-type is not HTML."""
    mock_response = MagicMock()
    mock_response.headers = {"content-type": "application/json"}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await fetch_url_metadata("https://example.com/api.json")

        assert result["title"] is None
        assert result["description"] is None
        assert result["og_image"] is None


@pytest.mark.asyncio
async def test_fetch_url_metadata_exception_handled():
    """Verify that fetch_url_metadata handles exceptions gracefully and returns empty dict."""
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = httpx.TimeoutException("Connection timed out")

        result = await fetch_url_metadata("https://example.com/slow")

        assert result["title"] is None
        assert result["description"] is None
        assert result["og_image"] is None


@pytest.mark.asyncio
async def test_fetch_and_store_metadata_success(db_session):
    """Verify that background task successfully fetches and saves metadata to DB."""
    # Setup test url in database
    url = URL(original_url="https://example.com/scrape-me", short_code="sc1", is_active=True)
    db_session.add(url)
    await db_session.commit()
    await db_session.refresh(url)

    scraped_metadata = {
        "title": "A Very Nice Title",
        "og_image": "https://example.com/nice.png",
        "description": "A nice description.",
    }

    with (
        patch("app.utils.validators.is_valid_url_async", new_callable=AsyncMock) as mock_validate,
        patch(
            "app.services.metadata_service.fetch_url_metadata", new_callable=AsyncMock
        ) as mock_fetch,
    ):
        mock_validate.return_value = (True, "")
        mock_fetch.return_value = scraped_metadata

        # Execute background task
        await _fetch_and_store_metadata(url.id, url.original_url)

        # Refresh from database and check metadata
        await db_session.refresh(url)
        assert url.metadata_ == scraped_metadata


@pytest.mark.asyncio
async def test_fetch_and_store_metadata_ssrf_blocked(db_session):
    """Verify that background task blocks execution if URL fails SSRF/DNS check."""
    url = URL(original_url="http://192.168.1.1/admin", short_code="ssrf1", is_active=True)
    db_session.add(url)
    await db_session.commit()
    await db_session.refresh(url)

    with (
        patch("app.utils.validators.is_valid_url_async", new_callable=AsyncMock) as mock_validate,
        patch(
            "app.services.metadata_service.fetch_url_metadata", new_callable=AsyncMock
        ) as mock_fetch,
    ):
        mock_validate.return_value = (False, "SSRF Attempt Blocked")

        # Execute background task
        await _fetch_and_store_metadata(url.id, url.original_url)

        # Refresh from database and check that metadata remained None
        await db_session.refresh(url)
        assert url.metadata_ is None
        assert mock_fetch.call_count == 0
