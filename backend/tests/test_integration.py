"""
Integration Tests
──────────────────
Tests verification of API endpoints under real/simulated service connections.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.models.url import URL


@pytest.mark.asyncio
class TestIntegration:
    """End-to-end integration tests for LinkForge API."""

    async def test_auth_registration_and_login_cycle(self, client):
        # 1. Register User
        reg_payload = {
            "email": "inttest@example.com",
            "username": "intuser",
            "password": "IntSecurePassword123",
        }
        res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res_reg.status_code == 201
        reg_data = res_reg.json()
        assert reg_data["user"]["email"] == "inttest@example.com"
        assert "access_token" in res_reg.cookies
        assert "refresh_token" in res_reg.cookies
        assert "tokens" not in reg_data

        # 2. Duplicate registration should fail with 409 Conflict
        res_dup = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res_dup.status_code == 409

        # 3. Login User
        login_payload = {"email": "inttest@example.com", "password": "IntSecurePassword123"}
        res_login = await client.post("/api/v1/auth/login", json=login_payload)
        assert res_login.status_code == 200
        login_data = res_login.json()
        assert login_data["user"]["username"] == "intuser"
        assert "access_token" in res_login.cookies
        assert "refresh_token" in res_login.cookies
        assert "tokens" not in login_data

    async def test_url_creation_and_resolution_cycle(self, client):
        # 1. Anonymous URL Shortening
        payload = {"url": "https://news.ycombinator.com"}
        res_create = await client.post("/api/v1/shorten", json=payload)
        assert res_create.status_code == 201
        data_create = res_create.json()
        short_code = data_create["short_code"]
        assert short_code is not None

        # 2. Redirect Flow
        res_redirect = await client.get(f"/{short_code}", follow_redirects=False)
        assert res_redirect.status_code == 302
        assert res_redirect.headers["Location"] == "https://news.ycombinator.com"

        # 3. Check safety validation block (triggers Pydantic validator yielding 422)
        unsafe_payload = {"url": "http://127.0.0.1/admin"}
        res_unsafe = await client.post("/api/v1/shorten", json=unsafe_payload)
        assert res_unsafe.status_code == 422
        assert "private/internal addresses" in res_unsafe.json()["error"]["message"]

    async def test_authenticated_url_management(self, client):
        # 1. Register and Login to get Auth cookies
        reg_payload = {
            "email": "owner_int@example.com",
            "username": "owner_int",
            "password": "Password123",
        }
        await client.post("/api/v1/auth/register", json=reg_payload)

        login_payload = {"email": "owner_int@example.com", "password": "Password123"}
        await client.post("/api/v1/auth/login", json=login_payload)

        # 2. Create custom alias URL
        payload = {"url": "https://crates.io", "custom_alias": "my-crates"}
        res_create = await client.post("/api/v1/shorten", json=payload)
        assert res_create.status_code == 201

        # 3. List URLs
        res_list = await client.get("/api/v1/urls")
        assert res_list.status_code == 200
        list_data = res_list.json()
        assert list_data["total"] == 1
        assert list_data["urls"][0]["short_code"] == "my-crates"

        # 4. Deactivate URL
        res_delete = await client.delete("/api/v1/urls/my-crates")
        assert res_delete.status_code == 204

        # 5. List URLs again (should be empty list as deactivated)
        res_list_after = await client.get("/api/v1/urls")
        assert res_list_after.json()["total"] == 0

        # 6. Resolution of deactivated URL should return 404
        res_res = await client.get("/my-crates", follow_redirects=False)
        assert res_res.status_code == 404

    async def test_expired_url_redirect(self, client, db_session, cache_service):
        # Create expired URL
        url = URL(
            original_url="https://expired-integration.com",
            short_code="exp123",
            expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
            is_active=True,
        )
        db_session.add(url)
        await db_session.commit()
        await db_session.refresh(url)

        # Clear cache to force DB evaluation
        await cache_service.delete_url("exp123")

        # Resolve expired URL -> 410 Gone
        res = await client.get("/exp123")
        assert res.status_code == 410
        assert "expired" in res.json()["error"]["message"]

    async def test_url_not_found(self, client):
        res = await client.get("/nonexistent-code")
        assert res.status_code == 404
