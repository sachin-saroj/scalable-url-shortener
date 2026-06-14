import pytest
import sqlalchemy as sa

from app.models.url import URL
from app.models.user import User


@pytest.mark.asyncio
async def test_admin_stats_access(client, db_session):
    """Test accessing stats endpoint as admin, regular user, and anonymous."""

    # 1. Anonymous Access -> 401
    response = await client.get("/api/v1/admin/stats")
    assert response.status_code == 401

    # 2. Register and Login a regular user -> 403
    reg_payload = {
        "email": "user@example.com",
        "username": "regularuser",
        "password": "Password123",
    }
    await client.post("/api/v1/auth/register", json=reg_payload)
    # login is automatic on register, cookies are populated

    response = await client.get("/api/v1/admin/stats")
    assert response.status_code == 403

    # 3. Elevate user to Admin role in DB
    query = sa.select(User).where(User.email == "user@example.com")
    res = await db_session.execute(query)
    user = res.scalar_one()
    user.role = "admin"
    await db_session.commit()

    # Re-login to get new JWT with elevated role
    client.cookies.clear()
    login_payload = {
        "email": "user@example.com",
        "password": "Password123",
    }
    await client.post("/api/v1/auth/login", json=login_payload)

    # Admin Access -> 200
    response = await client.get("/api/v1/admin/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_urls" in data
    assert "total_users" in data
    assert data["total_users"] == 1


@pytest.mark.asyncio
async def test_admin_deactivate_override(client, db_session):
    """Test that admin user can deactivate any URL, while regular users cannot."""

    # 1. Create a regular user who owns a URL
    user_payload = {
        "email": "owner@example.com",
        "username": "urlowner",
        "password": "Password123",
    }
    await client.post("/api/v1/auth/register", json=user_payload)

    # Create a short URL
    create_resp = await client.post("/api/v1/shorten", json={"url": "https://google.com"})
    assert create_resp.status_code == 201
    short_code = create_resp.json()["short_code"]

    # 2. Create another regular user (non-owner)
    client.cookies.clear()
    other_payload = {
        "email": "other@example.com",
        "username": "otheruser",
        "password": "Password123",
    }
    await client.post("/api/v1/auth/register", json=other_payload)

    # Try to deactivate using normal endpoint (should fail because not owner)
    deact_resp = await client.delete(f"/api/v1/urls/{short_code}")
    assert deact_resp.status_code == 403

    # Try to deactivate using admin override endpoint (should fail with 403 as regular user)
    admin_deact_resp = await client.post(f"/api/v1/admin/urls/{short_code}/deactivate")
    assert admin_deact_resp.status_code == 403

    # 3. Create Admin user
    client.cookies.clear()
    admin_payload = {
        "email": "admin@example.com",
        "username": "adminuser",
        "password": "Password123",
    }
    await client.post("/api/v1/auth/register", json=admin_payload)

    # Elevate role in DB
    query = sa.select(User).where(User.email == "admin@example.com")
    res = await db_session.execute(query)
    admin_user = res.scalar_one()
    admin_user.role = "admin"
    await db_session.commit()

    # Re-login admin
    client.cookies.clear()
    await client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "Password123",
        },
    )

    # Admin overrides deactivation -> 200
    admin_deact_resp = await client.post(f"/api/v1/admin/urls/{short_code}/deactivate")
    assert admin_deact_resp.status_code == 200
    assert admin_deact_resp.json()["status"] == "deactivated"

    # Verify database reflects deactivation
    query_url = sa.select(URL).where(URL.short_code == short_code)
    url_res = await db_session.execute(query_url)
    url = url_res.scalar_one()
    assert url.is_active is False

    # Admin deactivating non-existent URL -> 404
    admin_deact_resp_404 = await client.post("/api/v1/admin/urls/nonexistent/deactivate")
    assert admin_deact_resp_404.status_code == 404
