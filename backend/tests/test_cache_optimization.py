"""
Tests for Redis Cache URL Resolution Optimization
─────────────────────────────────────────────────
Verifies that cache hits perform zero database queries, cache misses
perform exactly one database query, and metadata-driven validation
(active status, expiration) operates correctly without querying PostgreSQL.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
import sqlalchemy as sa

from app.db.session import async_session_factory
from app.models.click import Click
from app.models.url import URL
from app.services.url_service import URLService


@pytest.mark.asyncio
async def test_cache_hit_performs_zero_database_queries(db_session, cache_service):
    # 1. Create a URL
    url = URL(original_url="https://target.com/page", short_code="hit0", is_active=True)
    db_session.add(url)
    await db_session.commit()
    await db_session.refresh(url)

    # 2. Populate cache with optimized metadata format
    url_data = {
        "id": url.id,
        "original_url": url.original_url,
        "is_active": url.is_active,
        "expires_at": None,
    }
    await cache_service.set_url_data("hit0", url_data)

    service = URLService(db_session, cache_service)

    # Spy on db_session.execute to count queries
    original_execute = db_session.execute
    query_count = 0

    async def spy_execute(*args, **kwargs):
        nonlocal query_count
        query_count += 1
        return await original_execute(*args, **kwargs)

    with patch.object(db_session, "execute", side_effect=spy_execute):
        resolved_url, url_id = await service.get_original_url("hit0")
        assert resolved_url == "https://target.com/page"
        assert url_id == url.id
        assert query_count == 0  # CRITICAL: 0 database queries on cache hit!


@pytest.mark.asyncio
async def test_cache_miss_performs_one_database_query(db_session, cache_service):
    # 1. Create a URL
    url = URL(original_url="https://target.com/page-miss", short_code="miss1", is_active=True)
    db_session.add(url)
    await db_session.commit()
    await db_session.refresh(url)

    # 2. Ensure cache is clear
    await cache_service.delete_url("miss1")

    service = URLService(db_session, cache_service)

    # Spy on db_session.execute
    original_execute = db_session.execute
    query_count = 0

    async def spy_execute(*args, **kwargs):
        nonlocal query_count
        query_count += 1
        return await original_execute(*args, **kwargs)

    with patch.object(db_session, "execute", side_effect=spy_execute):
        resolved_url, url_id = await service.get_original_url("miss1")
        assert resolved_url == "https://target.com/page-miss"
        assert url_id == url.id
        assert query_count == 1  # CRITICAL: exactly 1 database query on cache miss!

    # 3. Verify it was correctly cached as a JSON metadata object
    cached_data = await cache_service.get_url_data("miss1")
    assert cached_data is not None
    assert cached_data["id"] == url.id
    assert cached_data["original_url"] == "https://target.com/page-miss"
    assert cached_data["is_active"] is True
    assert cached_data["expires_at"] is None


@pytest.mark.asyncio
async def test_expired_url_from_cache_fails_and_deletes_key(db_session, cache_service):
    # Setup cache with expired URL metadata
    url_data = {
        "id": 999,
        "original_url": "https://expired-cached.com",
        "is_active": True,
        "expires_at": (datetime.now(timezone.utc) - timedelta(seconds=10)).isoformat(),
    }
    await cache_service.set_url_data("exp", url_data)

    service = URLService(db_session, cache_service)

    # Spy on db_session.execute
    original_execute = db_session.execute
    query_count = 0

    async def spy_execute(*args, **kwargs):
        nonlocal query_count
        query_count += 1
        return await original_execute(*args, **kwargs)

    with patch.object(db_session, "execute", side_effect=spy_execute):
        with pytest.raises(ValueError, match="expired"):
            await service.get_original_url("exp")
        assert query_count == 0  # Checked entirely in cache!

    # Cache should be cleared
    cached_data = await cache_service.get_url_data("exp")
    assert cached_data is None


@pytest.mark.asyncio
async def test_inactive_url_from_cache_fails_and_deletes_key(db_session, cache_service):
    # Setup cache with deactivated URL metadata
    url_data = {
        "id": 888,
        "original_url": "https://inactive-cached.com",
        "is_active": False,
        "expires_at": None,
    }
    await cache_service.set_url_data("inac", url_data)

    service = URLService(db_session, cache_service)

    # Spy on db_session.execute
    original_execute = db_session.execute
    query_count = 0

    async def spy_execute(*args, **kwargs):
        nonlocal query_count
        query_count += 1
        return await original_execute(*args, **kwargs)

    with patch.object(db_session, "execute", side_effect=spy_execute):
        with pytest.raises(LookupError, match="not found"):
            await service.get_original_url("inac")
        assert query_count == 0  # Checked entirely in cache!

    # Cache should be cleared
    cached_data = await cache_service.get_url_data("inac")
    assert cached_data is None


@pytest.mark.asyncio
async def test_analytics_recording_still_functions_on_optimized_cache_hit(
    client, db_session, cache_service
):
    # 1. Create a URL in DB
    url = URL(original_url="https://google.com/analytics-hit", short_code="anahit", is_active=True)
    db_session.add(url)
    await db_session.commit()
    await db_session.refresh(url)

    # 2. Cache the metadata JSON
    url_data = {
        "id": url.id,
        "original_url": url.original_url,
        "is_active": url.is_active,
        "expires_at": None,
    }
    await cache_service.set_url_data("anahit", url_data)

    # Spy on db_session.execute for the redirect request
    original_execute = db_session.execute
    query_count = 0

    async def spy_execute(*args, **kwargs):
        nonlocal query_count
        query_count += 1
        return await original_execute(*args, **kwargs)

    # 3. Request redirection
    with patch.object(db_session, "execute", side_effect=spy_execute):
        response = await client.get("/anahit", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["Location"] == "https://google.com/analytics-hit"
        # The main redirect resolution should make 0 DB queries!
        assert query_count == 0

    # 4. Trigger the background task and verify that it successfully writes click to DB
    for _ in range(10):
        async with async_session_factory() as verify_session:
            res = await verify_session.execute(sa.select(Click).where(Click.url_id == url.id))
            clicks = res.scalars().all()
            if len(clicks) == 1:
                assert clicks[0].ip_address in ("127.0.0.1", "localhost", "test", "unknown")
                break
        await asyncio.sleep(0.1)
    else:
        pytest.fail("Click was not recorded in the database by background tasks within timeout")
