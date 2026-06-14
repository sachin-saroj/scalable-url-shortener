import pytest


@pytest.mark.asyncio
async def test_cookie_register_and_login_flow(client):
    # 1. Register a new user
    reg_payload = {
        "email": "cookieuser@example.com",
        "username": "cookieuser",
        "password": "SecurePassword123",
    }
    response = await client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201

    # Assert that register endpoint set HTTP cookies
    cookies = response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies

    # Clear client cookies to test login
    client.cookies.clear()

    # 2. Login user
    login_payload = {
        "email": "cookieuser@example.com",
        "password": "SecurePassword123",
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)
    assert response.status_code == 200

    cookies = response.cookies
    assert "access_token" in cookies
    assert "refresh_token" in cookies

    # 3. Access authenticated route /me (cookies sent automatically)
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 200
    assert response.json()["username"] == "cookieuser"

    # 4. Refresh token using cookies
    # We clear the access token cookie to force refresh scenario
    client.cookies.delete("access_token")

    response = await client.post("/api/v1/auth/refresh")
    assert response.status_code == 200
    assert "access_token" in response.cookies

    # Me endpoint should work again
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 200

    # 5. Logout user
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 200

    # Depending on how the client updates cookies,
    # let's verify if access_token cookie is deleted or empty
    access_cookie = response.cookies.get("access_token")
    assert access_cookie is None or access_cookie == ""

    # 6. Access /me again (should be unauthenticated)
    # Clear client cookies to simulate final unauthenticated state
    client.cookies.clear()
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_cookie_expiry_alignment(client):
    from app.config import get_settings

    settings = get_settings()

    reg_payload = {
        "email": "expirytest@example.com",
        "username": "expirytest",
        "password": "SecurePassword123",
    }
    response = await client.post("/api/v1/auth/register", json=reg_payload)
    assert response.status_code == 201

    set_cookies = response.headers.get_list("set-cookie")
    access_cookie = next((c for c in set_cookies if "access_token" in c), None)
    refresh_cookie = next((c for c in set_cookies if "refresh_token" in c), None)

    assert access_cookie is not None
    assert refresh_cookie is not None

    # Verify Max-Age values match configurations
    expected_access_max_age = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    expected_refresh_max_age = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    assert f"max-age={expected_access_max_age}" in access_cookie.lower()
    assert f"max-age={expected_refresh_max_age}" in refresh_cookie.lower()
