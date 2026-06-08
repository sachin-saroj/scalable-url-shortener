import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from app.config import Settings
from app.utils.validators import is_valid_url


# ── 1. Configuration Validation Tests ──────────────────
def test_settings_validation():
    # If JWT_SECRET_KEY is default
    with pytest.raises(RuntimeError) as exc_info:
        Settings(
            JWT_SECRET_KEY="change-me",
            SECRET_KEY="secure-key",
            DATABASE_URL="postgresql+asyncpg://user:pass@host/db"
        )
    assert "JWT_SECRET_KEY must be changed" in str(exc_info.value)

    # If SECRET_KEY is default
    with pytest.raises(RuntimeError) as exc_info:
        Settings(
            JWT_SECRET_KEY="secure-jwt-key",
            SECRET_KEY="change-me",
            DATABASE_URL="postgresql+asyncpg://user:pass@host/db"
        )
    assert "SECRET_KEY must be changed" in str(exc_info.value)

    # If DATABASE_URL is missing and cannot be constructed
    with pytest.raises(RuntimeError) as exc_info:
        Settings(
            JWT_SECRET_KEY="secure-jwt-key",
            SECRET_KEY="secure-key",
            DATABASE_URL=None,
            POSTGRES_USER=None,
            POSTGRES_PASSWORD=None,
            POSTGRES_HOST=None,
            POSTGRES_DB=None
        )
    assert "DATABASE_URL is missing" in str(exc_info.value)


# ── 2. CORS Production Origin Restriction Tests ─────────
def test_settings_cors_production():
    # In development, localhost allowed
    dev_settings = Settings(
        APP_ENV="development",
        JWT_SECRET_KEY="secure-jwt-key",
        SECRET_KEY="secure-key",
        DATABASE_URL="postgresql+asyncpg://user:pass@host/db",
        CORS_ORIGINS="http://localhost:3000,http://example.com,*"
    )
    assert "http://localhost:3000" in dev_settings.cors_origins_list
    assert "*" in dev_settings.cors_origins_list

    # In production, localhost and wildcard filtered out
    prod_settings = Settings(
        APP_ENV="production",
        JWT_SECRET_KEY="secure-jwt-key",
        SECRET_KEY="secure-key",
        DATABASE_URL="postgresql+asyncpg://user:pass@host/db",
        CORS_ORIGINS="http://localhost:3000,http://example.com,*,http://127.0.0.1:3000"
    )
    assert "http://localhost:3000" not in prod_settings.cors_origins_list
    assert "http://127.0.0.1:3000" not in prod_settings.cors_origins_list
    assert "*" not in prod_settings.cors_origins_list
    assert "http://example.com" in prod_settings.cors_origins_list


# ── 3. SSRF / Safe URL Validation Tests ────────────────
@pytest.mark.parametrize(
    "url, expected_valid",
    [
        ("https://google.com", True),
        ("http://github.com/path", True),
        ("http://localhost", False),
        ("http://127.0.0.1", False),
        ("http://127.0.1.1", False),
        ("http://0.0.0.0", False),
        ("http://10.0.0.1", False),
        ("http://172.16.0.1", False),
        ("http://172.31.255.255", False),
        ("http://192.168.1.1", False),
        ("http://169.254.169.254", False),
        ("javascript:alert(1)", False),
        ("data:text/html,<html>", False),
        ("file:///etc/passwd", False),
        ("ftp://ftp.example.com", False),
    ]
)
def test_url_validation_ssrf(url, expected_valid):
    valid, _ = is_valid_url(url)
    assert valid == expected_valid


# ── 4. Response & Security Headers Tests ───────────────
@pytest.mark.asyncio
async def test_security_headers(client):
    response = await client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"
    assert "Permissions-Policy" in response.headers
    assert "Strict-Transport-Security" in response.headers
    assert "X-Request-ID" in response.headers


# ── 5. Redirect and Error Handling Integration Tests ────
@pytest.mark.asyncio
@patch("app.api.v1.redirect.URLService")
@patch("app.api.v1.redirect.get_db")
@patch("app.api.v1.redirect.get_cache")
async def test_redirect_exceptions(mock_get_cache, mock_get_db, mock_url_service_class, client):
    mock_service = MagicMock()
    mock_url_service_class.return_value = mock_service

    # Test inactive link (raises LookupError)
    mock_service.get_original_url.side_effect = LookupError("Short URL not found")
    resp = await client.get("/inactive123")
    assert resp.status_code == status.HTTP_404_NOT_FOUND
    data = resp.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "request_id" in data["error"]

    # Test expired link (raises ValueError("This short URL has expired"))
    mock_service.get_original_url.side_effect = ValueError("This short URL has expired")
    resp = await client.get("/expired123")
    assert resp.status_code == status.HTTP_410_GONE
    data = resp.json()
    assert data["error"]["code"] == "GONE"

    # Test malformed destination URL (raises ValueError("Destination URL is malformed"))
    mock_service.get_original_url.side_effect = ValueError("Destination URL is malformed")
    resp = await client.get("/malformed123")
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    data = resp.json()
    assert data["error"]["code"] == "BAD_REQUEST"
