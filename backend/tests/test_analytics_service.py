"""
Tests for AnalyticsService
──────────────────────────
Unit and integration tests for recording click events, calculating analytics timelines, and aggregating daily reports.
"""

import pytest
from datetime import datetime, date, timezone, timedelta
from app.services.analytics_service import AnalyticsService
from app.models.url import URL
from app.models.click import Click
from app.models.daily_analytics import DailyAnalytics

@pytest.mark.asyncio
class TestAnalyticsService:
    """Test suite for AnalyticsService."""

    async def _setup_test_url(self, db) -> URL:
        url = URL(
            original_url="https://google.com/search",
            short_code="search1",
            is_active=True
        )
        db.add(url)
        await db.commit()
        await db.refresh(url)
        return url

    async def test_record_click_success(self, db_session, cache_service):
        service = AnalyticsService(db_session, cache_service)
        url = await self._setup_test_url(db_session)

        # Record click
        await service.record_click(
            url_id=url.id,
            short_code=url.short_code,
            ip_address="192.168.1.15",
            user_agent="Firefox",
            referer="https://t.co",
            country="US",
            city="New York"
        )

        # Verify DB entry
        import sqlalchemy as sa
        res = await db_session.execute(sa.select(Click).where(Click.url_id == url.id))
        clicks = res.scalars().all()
        assert len(clicks) == 1
        assert clicks[0].ip_address == "192.168.1.15"
        assert clicks[0].user_agent == "Firefox"
        assert clicks[0].referer == "https://t.co"
        assert clicks[0].country == "US"
        assert clicks[0].city == "New York"

    async def test_get_analytics_cached(self, db_session, cache_service):
        service = AnalyticsService(db_session, cache_service)
        url = await self._setup_test_url(db_session)

        # Seed analytics cache manually
        cached_data = {
            "short_code": url.short_code,
            "total_clicks": 999,
            "unique_clicks": 111,
            "clicks_24h": 22,
            "clicks_7d": 77,
            "top_countries": [{"country": "IN", "clicks": 999}],
            "clicks_by_day": []
        }
        await cache_service.set_analytics(url.short_code, cached_data, ttl=60)

        # Call get_analytics (should fetch from cache directly)
        res = await service.get_analytics(url.short_code, url.id)
        assert res == cached_data

    async def test_get_analytics_uncached_aggregation(self, db_session, cache_service):
        service = AnalyticsService(db_session, cache_service)
        url = await self._setup_test_url(db_session)

        now = datetime.now(timezone.utc)
        # Create some historical click records
        c1 = Click(url_id=url.id, ip_address="1.1.1.1", country="IN", clicked_at=now - timedelta(hours=2))
        c2 = Click(url_id=url.id, ip_address="1.1.1.1", country="IN", clicked_at=now - timedelta(hours=5)) # non-unique IP
        c3 = Click(url_id=url.id, ip_address="2.2.2.2", country="US", clicked_at=now - timedelta(days=2))
        
        db_session.add_all([c1, c2, c3])
        await db_session.commit()

        # Calculate analytics
        analytics = await service.get_analytics(url.short_code, url.id)
        assert analytics["total_clicks"] == 3
        assert analytics["unique_clicks"] == 2
        assert analytics["clicks_24h"] == 2
        assert analytics["clicks_7d"] == 3
        
        # Verify top countries list sorted by count desc
        top_countries = analytics["top_countries"]
        assert len(top_countries) == 2
        assert top_countries[0]["country"] == "IN"
        assert top_countries[0]["clicks"] == 2
        assert top_countries[1]["country"] == "US"
        assert top_countries[1]["clicks"] == 1

        # Check clicks by day
        by_day = analytics["clicks_by_day"]
        assert len(by_day) >= 2

    async def test_aggregate_daily_success(self, db_session, cache_service):
        service = AnalyticsService(db_session, cache_service)
        url = await self._setup_test_url(db_session)

        target_date = date(2026, 6, 8)
        start_time = datetime.combine(target_date, datetime.min.time()).replace(tzinfo=timezone.utc)

        # Create clicks for target_date
        c1 = Click(url_id=url.id, ip_address="192.168.1.1", clicked_at=start_time + timedelta(hours=2))
        c2 = Click(url_id=url.id, ip_address="192.168.1.2", clicked_at=start_time + timedelta(hours=4))
        c3 = Click(url_id=url.id, ip_address="192.168.1.1", clicked_at=start_time + timedelta(hours=6)) # duplicate IP

        db_session.add_all([c1, c2, c3])
        await db_session.commit()

        # Perform daily aggregation
        upserted_count = await service.aggregate_daily(target_date)
        assert upserted_count == 1

        # Verify daily_analytics record
        import sqlalchemy as sa
        res = await db_session.execute(
            sa.select(DailyAnalytics).where(
                DailyAnalytics.url_id == url.id,
                DailyAnalytics.date == target_date
            )
        )
        record = res.scalar_one_or_none()
        assert record is not None
        assert record.total_clicks == 3
        assert record.unique_clicks == 2

        # Rerun aggregation to test upsert update branch
        # Add a new click on the same day
        c4 = Click(url_id=url.id, ip_address="192.168.1.3", clicked_at=start_time + timedelta(hours=8))
        db_session.add(c4)
        await db_session.commit()

        upserted_count2 = await service.aggregate_daily(target_date)
        assert upserted_count2 == 1

        # Refresh from db and assert
        db_session.expire(record)
        res = await db_session.execute(
            sa.select(DailyAnalytics).where(
                DailyAnalytics.url_id == url.id,
                DailyAnalytics.date == target_date
            )
        )
        record = res.scalar_one()
        assert record.total_clicks == 4
        assert record.unique_clicks == 3
