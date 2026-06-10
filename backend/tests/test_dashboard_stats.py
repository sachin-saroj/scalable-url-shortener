from datetime import datetime, timedelta, timezone

import pytest

from app.models.click import Click
from app.models.url import URL
from app.models.user import User
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_dashboard_stats_scenarios(client, db_session):
    # 1. Create a user and get auth token
    user = User(email="statsuser@example.com", username="statsuser", password_hash="hashed")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    auth_service = AuthService(db_session)
    tokens = auth_service._create_tokens(user)
    headers = {"Authorization": f"Bearer {tokens.access_token}"}

    response = await client.get("/api/v1/urls/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_links"] == 0
    assert data["active_links"] == 0
    assert data["expired_links"] == 0
    assert data["total_clicks"] == 0
    assert data["average_clicks_per_link"] == 0.0

    # Scenario B: User with less than one page (3 active, 2 expired, some clicks)
    url1 = URL(user_id=user.id, original_url="https://google.com", short_code="g1", is_active=True)
    url2 = URL(user_id=user.id, original_url="https://github.com", short_code="g2", is_active=True)
    url3 = URL(user_id=user.id, original_url="https://gitlab.com", short_code="g3", is_active=True)

    url4 = URL(
        user_id=user.id,
        original_url="https://yahoo.com",
        short_code="y1",
        is_active=True,
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    url5 = URL(
        user_id=user.id,
        original_url="https://bing.com",
        short_code="b1",
        is_active=True,
        expires_at=datetime.now(timezone.utc) - timedelta(hours=2),
    )
    # 1 deactivated link (should be ignored):
    url6 = URL(
        user_id=user.id, original_url="https://ignored.com", short_code="i1", is_active=False
    )

    db_session.add_all([url1, url2, url3, url4, url5, url6])
    await db_session.commit()
    await db_session.refresh(url1)
    await db_session.refresh(url2)
    await db_session.refresh(url3)
    await db_session.refresh(url4)
    await db_session.refresh(url5)

    # Let's add some clicks:
    # url1: 3 clicks
    c1 = Click(url_id=url1.id, ip_address="1.1.1.1")
    c2 = Click(url_id=url1.id, ip_address="2.2.2.2")
    c3 = Click(url_id=url1.id, ip_address="3.3.3.3")
    # url2: 1 click
    c4 = Click(url_id=url2.id, ip_address="4.4.4.4")
    # url4 (expired): 2 clicks
    c5 = Click(url_id=url4.id, ip_address="5.5.5.5")
    c6 = Click(url_id=url4.id, ip_address="6.6.6.6")

    db_session.add_all([c1, c2, c3, c4, c5, c6])
    await db_session.commit()

    # Query statistics
    response = await client.get("/api/v1/urls/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_links"] == 5
    assert data["active_links"] == 3
    assert data["expired_links"] == 2
    assert data["total_clicks"] == 6
    assert data["average_clicks_per_link"] == 1.2

    # Scenario C: User with multiple pages of URLs
    # Add 25 more active links to exceed page 1 (total active 28, expired 2, deactivated 1)
    more_urls = []
    for i in range(25):
        more_urls.append(
            URL(
                user_id=user.id,
                original_url=f"https://link-{i}.com",
                short_code=f"code{i}",
                is_active=True,
            )
        )
    db_session.add_all(more_urls)
    await db_session.commit()

    # Query stats again
    response = await client.get("/api/v1/urls/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_links"] == 30
    assert data["active_links"] == 28
    assert data["expired_links"] == 2
    assert data["total_clicks"] == 6
    assert data["average_clicks_per_link"] == 0.2
