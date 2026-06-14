"""
Tests for URLService
────────────────────
Unit and integration tests for URL shortening, custom aliases, resolution,
expiration, deactivation, and caching.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from app.models.user import User
from app.schemas.url import URLCreateRequest
from app.services.url_service import URLService


@pytest.mark.asyncio
class TestURLService:
    """Test suite for URLService business logic."""

    async def _setup_user(self, db):
        user = User(
            id=uuid4(), email="owner@example.com", username="owneruser", password_hash="hash"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    async def test_create_short_url_success(self, db_session, cache_service):
        service = URLService(db_session, cache_service)
        request = URLCreateRequest(url="https://github.com/google")

        response = await service.create_short_url(request)
        assert response.original_url == "https://github.com/google"
        assert response.short_code is not None
        assert response.short_url.endswith(response.short_code)

        # Check that it's cached
        cached = await cache_service.get_url(response.short_code)
        assert cached == "https://github.com/google"

    async def test_create_short_url_invalid(self, db_session, cache_service):
        service = URLService(db_session, cache_service)
        request = URLCreateRequest.model_construct(url="not-a-valid-url")

        with pytest.raises(ValueError, match="URL scheme must be http or https"):
            await service.create_short_url(request)

    async def test_create_short_url_idempotency(self, db_session, cache_service):
        service = URLService(db_session, cache_service)
        request = URLCreateRequest(url="https://wikipedia.org")

        resp1 = await service.create_short_url(request)
        resp2 = await service.create_short_url(request)

        assert resp1.short_code == resp2.short_code

    async def test_create_short_url_custom_alias_success(self, db_session, cache_service):
        service = URLService(db_session, cache_service)
        request = URLCreateRequest(url="https://python.org", custom_alias="my-python")

        response = await service.create_short_url(request)
        assert response.short_code == "my-python"

        cached = await cache_service.get_url("my-python")
        assert cached == "https://python.org"

    async def test_create_short_url_custom_alias_duplicate(self, db_session, cache_service):
        service = URLService(db_session, cache_service)
        request1 = URLCreateRequest(url="https://python.org", custom_alias="duplicate-alias")
        await service.create_short_url(request1)

        request2 = URLCreateRequest(url="https://ruby-lang.org", custom_alias="duplicate-alias")
        with pytest.raises(ValueError, match="Custom alias 'duplicate-alias' is already taken"):
            await service.create_short_url(request2)

    async def test_get_original_url_cache_hit(self, db_session, cache_service):
        service = URLService(db_session, cache_service)
        # Create and verify URL
        request = URLCreateRequest(url="https://rust-lang.org")
        response = await service.create_short_url(request)

        # Resolve URL (should fetch from cache)
        url, url_id = await service.get_original_url(response.short_code)
        assert url == "https://rust-lang.org"
        assert url_id > 0

    async def test_get_original_url_cache_miss_db_hit(self, db_session, cache_service):
        service = URLService(db_session, cache_service)
        request = URLCreateRequest(url="https://elixir-lang.org")
        response = await service.create_short_url(request)

        # Evict cache to simulate cache miss
        await cache_service.delete_url(response.short_code)

        # Resolve URL (should fetch from DB and re-cache)
        url, _url_id = await service.get_original_url(response.short_code)
        assert url == "https://elixir-lang.org"

        # Verify it was re-cached
        cached = await cache_service.get_url(response.short_code)
        assert cached == "https://elixir-lang.org"

    async def test_get_original_url_expired(self, db_session, cache_service):
        service = URLService(db_session, cache_service)
        request = URLCreateRequest(url="https://expired-link.org", expires_in_hours=1)
        response = await service.create_short_url(request)

        # Manually alter expires_at in DB to past
        db_url = await service._find_by_code(response.short_code)
        db_url.expires_at = datetime.now(timezone.utc) - timedelta(seconds=10)
        await db_session.commit()
        await cache_service.delete_url(response.short_code)

        # Resolve URL (should fail with ValueError due to expiration)
        with pytest.raises(ValueError, match="expired"):
            await service.get_original_url(response.short_code)

    async def test_get_original_url_inactive(self, db_session, cache_service):
        service = URLService(db_session, cache_service)
        user = await self._setup_user(db_session)
        request = URLCreateRequest(url="https://inactive-link.org")
        response = await service.create_short_url(request, user_id=user.id)

        # Soft delete
        await service.deactivate_url(response.short_code, user.id)

        # Resolve URL should fail
        with pytest.raises(LookupError, match="not found"):
            await service.get_original_url(response.short_code)

    async def test_deactivate_url_not_owner(self, db_session, cache_service):
        service = URLService(db_session, cache_service)
        user1 = await self._setup_user(db_session)
        user2_id = uuid4()  # different user

        request = URLCreateRequest(url="https://own-check.org")
        response = await service.create_short_url(request, user_id=user1.id)

        # Try deactivating as user2
        with pytest.raises(PermissionError, match="own this URL"):
            await service.deactivate_url(response.short_code, user2_id)

    async def test_get_user_urls_paginated(self, db_session, cache_service):
        service = URLService(db_session, cache_service)
        user = await self._setup_user(db_session)

        # Create 3 URLs
        await service.create_short_url(URLCreateRequest(url="https://link1.org"), user_id=user.id)
        await service.create_short_url(URLCreateRequest(url="https://link2.org"), user_id=user.id)
        await service.create_short_url(URLCreateRequest(url="https://link3.org"), user_id=user.id)

        url_list, total = await service.get_user_urls(user.id, page=1, per_page=2)
        assert total == 3
        assert len(url_list) == 2

    async def test_get_user_urls_query_count(self, db_session, cache_service):
        service = URLService(db_session, cache_service)
        user = await self._setup_user(db_session)

        # Create 5 URLs to ensure we have multiple records
        for i in range(5):
            await service.create_short_url(
                URLCreateRequest(url=f"https://link-{i}.org"), user_id=user.id
            )

        # Track query count using SQLAlchemy connection event listener
        query_count = 0
        from sqlalchemy import event

        sync_engine = db_session.bind.sync_engine

        @event.listens_for(sync_engine, "before_cursor_execute")
        def count_query(conn, cursor, statement, parameters, context, executemany):
            nonlocal query_count
            query_count += 1

        try:
            url_list, total = await service.get_user_urls(user.id, page=1, per_page=5)
            assert total == 5
            assert len(url_list) == 5
            # We expect exactly 2 queries: 1 count query + 1 paginated fetch query
            assert query_count <= 2
        finally:
            event.remove(sync_engine, "before_cursor_execute", count_query)
