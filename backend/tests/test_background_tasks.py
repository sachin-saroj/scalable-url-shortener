import pytest
import sqlalchemy as sa

from app.api.v1.redirect import _record_click_background
from app.db.session import async_session_factory
from app.models.click import Click
from app.models.url import URL


@pytest.mark.asyncio
async def test_record_click_background_success(db_session, cache_service):
    # Setup a test URL
    url = URL(original_url="https://example.com/target", short_code="testbg", is_active=True)
    db_session.add(url)
    await db_session.commit()
    await db_session.refresh(url)

    # Call the background task directly to ensure it opens its own session and writes to DB
    await _record_click_background(
        url_id=url.id,
        short_code=url.short_code,
        ip_address="1.2.3.4",
        user_agent="TestAgent",
        referer="https://referer.com",
    )

    # Verify that the click was successfully written
    async with async_session_factory() as db:
        res = await db.execute(sa.select(Click).where(Click.url_id == url.id))
        clicks = res.scalars().all()
        assert len(clicks) == 1
        assert clicks[0].ip_address == "1.2.3.4"
        assert clicks[0].user_agent == "TestAgent"
        assert clicks[0].referer == "https://referer.com"


@pytest.mark.asyncio
async def test_redirect_endpoint_triggers_background_task(client, db_session):
    # Setup a test URL
    url = URL(original_url="https://example.com/target", short_code="testredirect", is_active=True)
    db_session.add(url)
    await db_session.commit()
    await db_session.refresh(url)

    # Perform redirect request
    response = await client.get(f"/{url.short_code}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"] == "https://example.com/target"

    # Verify that the click was successfully written to DB by the background task
    async with async_session_factory() as db:
        res = await db.execute(sa.select(Click).where(Click.url_id == url.id))
        clicks = res.scalars().all()
        assert len(clicks) == 1
        assert clicks[0].ip_address in ("127.0.0.1", "localhost", "test", "unknown")
