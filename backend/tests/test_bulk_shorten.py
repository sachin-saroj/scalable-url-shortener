"""Tests for bulk URL shortening endpoint."""

from unittest.mock import AsyncMock, patch

import pytest
from app.schemas.bulk import BulkURLCreateRequest, BulkURLCreateResponse, BulkURLItemResult
from app.schemas.url import URLCreateRequest


class TestBulkURLSchemas:
    """Test bulk URL request/response validation."""

    def test_valid_bulk_request(self):
        request = BulkURLCreateRequest(
            urls=[
                URLCreateRequest(url="https://example.com"),
                URLCreateRequest(url="https://google.com"),
            ]
        )
        assert len(request.urls) == 2

    def test_empty_urls_rejected(self):
        with pytest.raises(Exception):
            BulkURLCreateRequest(urls=[])

    def test_exceeds_max_50_urls(self):
        urls = [URLCreateRequest(url=f"https://example.com/{i}") for i in range(51)]
        with pytest.raises(Exception):
            BulkURLCreateRequest(urls=urls)

    def test_duplicate_aliases_rejected(self):
        with pytest.raises(Exception):
            BulkURLCreateRequest(
                urls=[
                    URLCreateRequest(url="https://example.com/a", custom_alias="my-link"),
                    URLCreateRequest(url="https://example.com/b", custom_alias="my-link"),
                ]
            )

    def test_unique_aliases_accepted(self):
        request = BulkURLCreateRequest(
            urls=[
                URLCreateRequest(url="https://example.com/a", custom_alias="link-one"),
                URLCreateRequest(url="https://example.com/b", custom_alias="link-two"),
            ]
        )
        assert len(request.urls) == 2

    def test_bulk_response_model(self):
        response = BulkURLCreateResponse(
            total=3,
            succeeded=2,
            failed=1,
            results=[
                BulkURLItemResult(index=0, success=True, data=None),
                BulkURLItemResult(index=1, success=True, data=None),
                BulkURLItemResult(index=2, success=False, error="URL rejected"),
            ],
        )
        assert response.total == 3
        assert response.succeeded == 2
        assert response.failed == 1

    def test_max_boundary_50_urls_accepted(self):
        urls = [URLCreateRequest(url=f"https://example.com/{i}") for i in range(50)]
        request = BulkURLCreateRequest(urls=urls)
        assert len(request.urls) == 50
