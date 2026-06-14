from unittest.mock import MagicMock, patch

import pytest
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
            DATABASE_URL="postgresql+asyncpg://user:pass@host/db",
        )
    assert "JWT_SECRET_KEY must be changed" in str(exc_info.value)

    # If SECRET_KEY is default
    with pytest.raises(RuntimeError) as exc_info:
        Settings(
            JWT_SECRET_KEY="secure-jwt-key",
            SECRET_KEY="change-me",
            DATABASE_URL="postgresql+asyncpg://user:pass@host/db",
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
            POSTGRES_DB=None,
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
        CORS_ORIGINS="http://localhost:3000,http://example.com,*",
    )
    assert "http://localhost:3000" in dev_settings.cors_origins_list
    assert "*" in dev_settings.cors_origins_list

    # In production, localhost and wildcard filtered out
    prod_settings = Settings(
        APP_ENV="production",
        JWT_SECRET_KEY="secure-jwt-key",
        SECRET_KEY="secure-key",
        DATABASE_URL="postgresql+asyncpg://user:pass@host/db",
        CORS_ORIGINS="http://localhost:3000,http://example.com,*,http://127.0.0.1:3000",
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
    ],
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


# ── 6. Phase 2 Security Hardening Tests ────────────────
@pytest.mark.asyncio
async def test_xff_ignored_when_not_trusted_proxy(client, test_redis):
    await test_redis.flushdb()
    response = await client.get("/api/v1/qr/test123", headers={"X-Forwarded-For": "1.2.3.4"})
    assert response.status_code == status.HTTP_404_NOT_FOUND

    keys = await test_redis.keys("rate:*")
    assert len(keys) > 0
    for key in keys:
        assert "1.2.3.4" not in key
        assert "testclient" in key or "127.0.0.1" in key


@pytest.mark.asyncio
async def test_xff_honored_when_trusted_proxy(monkeypatch, client, test_redis):
    await test_redis.flushdb()
    from app.utils.client_ip import settings

    monkeypatch.setattr(settings, "TRUSTED_PROXIES", "testclient, 127.0.0.1")

    response = await client.get("/api/v1/qr/test123", headers={"X-Forwarded-For": "1.2.3.4"})
    assert response.status_code == status.HTTP_404_NOT_FOUND

    keys = await test_redis.keys("rate:*")
    assert len(keys) > 0
    found_xff_ip = False
    for key in keys:
        if "1.2.3.4" in key:
            found_xff_ip = True
    assert found_xff_ip, f"Expected 1.2.3.4 in keys: {keys}"


@pytest.mark.asyncio
async def test_login_response_excludes_raw_tokens(client):
    # Register first
    reg_payload = {
        "email": "excludetokens@example.com",
        "username": "excludetokens",
        "password": "SecurePassword123",
    }
    reg_res = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == status.HTTP_201_CREATED

    # Login
    login_payload = {
        "email": "excludetokens@example.com",
        "password": "SecurePassword123",
    }
    res = await client.post("/api/v1/auth/login", json=login_payload)
    assert res.status_code == status.HTTP_200_OK
    body = res.json()
    assert "access_token" not in body
    assert "refresh_token" not in body
    assert "tokens" not in body
    assert "access_token" in res.cookies
    assert "refresh_token" in res.cookies


@pytest.mark.asyncio
async def test_qr_endpoint_rate_limited(client, test_redis):
    await test_redis.flushdb()

    # Send 100 requests (which should not hit rate limits)
    for _ in range(100):
        response = await client.get("/api/v1/qr/rate-limit-test")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # The 101st request should trigger rate limit (429)
    response = await client.get("/api/v1/qr/rate-limit-test")
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "TOO_MANY_REQUESTS"
    assert "Rate limit exceeded" in data["error"]["message"]
