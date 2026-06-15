"""
Tests for Request and Response Schemas
────────────────────────────────────────
"""

import pytest
from pydantic import ValidationError
from app.schemas.url import URLCreateRequest


class TestURLCreateRequestSchema:
    """Test schema validation constraints on URL creation requests."""

    def test_valid_custom_alias(self):
        req = URLCreateRequest(
            url="https://example.com",
            custom_alias="my-awesome-link-123"
        )
        assert req.custom_alias == "my-awesome-link-123"

    def test_invalid_custom_alias_characters(self):
        with pytest.raises(ValidationError) as exc_info:
            URLCreateRequest(
                url="https://example.com",
                custom_alias="my alias!"
            )
        assert "Custom alias can only contain" in str(exc_info.value)

    def test_reserved_custom_aliases_fail(self):
        for reserved in ["platform", "login", "register", "dashboard", "api", "admin", "health"]:
            with pytest.raises(ValidationError) as exc_info:
                URLCreateRequest(
                    url="https://example.com",
                    custom_alias=reserved
                )
            assert "reserved path" in str(exc_info.value)

    def test_alias_too_short(self):
        with pytest.raises(ValidationError):
            URLCreateRequest(
                url="https://example.com",
                custom_alias="ab"
            )

    def test_alias_too_long(self):
        with pytest.raises(ValidationError):
            URLCreateRequest(
                url="https://example.com",
                custom_alias="a" * 51
            )
