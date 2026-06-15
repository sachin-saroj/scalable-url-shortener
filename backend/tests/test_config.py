"""
Tests for Application Configuration
─────────────────────────────────────
"""

import pytest
from app.config import Settings


class TestConfiguration:
    """Test configuration settings, validation, and normalization."""

    def test_base_url_trailing_slash_stripped(self):
        settings = Settings(
            JWT_SECRET_KEY="test-key-long-enough-for-validation-purposes-only",
            SECRET_KEY="test-key-long-enough-for-validation-purposes-only",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            BASE_URL="https://linkforge.sh/",
        )
        assert settings.BASE_URL == "https://linkforge.sh"

    def test_trusted_proxies_list_parsing(self):
        settings = Settings(
            JWT_SECRET_KEY="test-key-long-enough-for-validation-purposes-only",
            SECRET_KEY="test-key-long-enough-for-validation-purposes-only",
            DATABASE_URL="sqlite+aiosqlite:///:memory:",
            TRUSTED_PROXIES="192.168.1.1, 10.0.0.2 ,172.16.0.5",
        )
        assert settings.trusted_proxies_list == ["192.168.1.1", "10.0.0.2", "172.16.0.5"]

    def test_invalid_secrets_raise_runtime_error(self):
        with pytest.raises(RuntimeError) as exc_info:
            Settings(
                JWT_SECRET_KEY="change-me",
                SECRET_KEY="change-me",
                DATABASE_URL="sqlite+aiosqlite:///:memory:",
            )
        assert "JWT_SECRET_KEY" in str(exc_info.value)
