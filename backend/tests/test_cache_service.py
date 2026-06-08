"""
Tests for CacheService
──────────────────────
Unit tests verifying the Redis cache interface, key setting, deletion, unique click tracking, and error resilience.
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.services.cache_service import CacheService

@pytest.mark.asyncio
class TestCacheService:
    """Test suite for CacheService operations."""

    async def test_set_and_get_url_success(self, cache_service):
        assert await cache_service.set_url("short1", "https://google.com", ttl=100) is True
        
        cached = await cache_service.get_url("short1")
        assert cached == "https://google.com"

    async def test_get_url_miss(self, cache_service):
        cached = await cache_service.get_url("nonexistent")
        assert cached is None

    async def test_delete_url(self, cache_service):
        await cache_service.set_url("short_del", "https://yahoo.com")
        assert await cache_service.delete_url("short_del") is True
        
        cached = await cache_service.get_url("short_del")
        assert cached is None

    async def test_track_unique_click(self, cache_service):
        # First click from IP should be unique
        assert await cache_service.track_unique_click("code1", "192.168.1.10", "2026-06-08") is True
        # Second click from same IP on same date should not be unique
        assert await cache_service.track_unique_click("code1", "192.168.1.10", "2026-06-08") is False
        # Click from different IP should be unique
        assert await cache_service.track_unique_click("code1", "192.168.1.20", "2026-06-08") is True

        # Check unique count
        count = await cache_service.get_unique_count("code1", "2026-06-08")
        assert count == 2

    async def test_analytics_cache(self, cache_service):
        analytics_data = {"clicks": 15, "uniques": 3}
        assert await cache_service.set_analytics("code_anal", analytics_data, ttl=60) is True
        
        cached = await cache_service.get_analytics("code_anal")
        assert cached == analytics_data

    async def test_ping(self, cache_service):
        assert await cache_service.ping() is True

    async def test_flush_pattern(self, cache_service):
        await cache_service.set_url("test_key:1", "val1")
        await cache_service.set_url("test_key:2", "val2")
        await cache_service.set_url("other_key:1", "val3")

        flushed = await cache_service.flush_pattern("url:test_key:*")
        assert flushed == 2

        assert await cache_service.get_url("test_key:1") is None
        assert await cache_service.get_url("test_key:2") is None
        assert await cache_service.get_url("other_key:1") == "val3"

    async def test_graceful_degradation_on_redis_errors(self, test_redis):
        # We patch redis methods to raise Exception to test graceful degradation
        with patch.object(test_redis, "get", side_effect=Exception("Redis connection error")), \
             patch.object(test_redis, "setex", side_effect=Exception("Redis connection error")), \
             patch.object(test_redis, "delete", side_effect=Exception("Redis connection error")), \
             patch.object(test_redis, "sadd", side_effect=Exception("Redis connection error")), \
             patch.object(test_redis, "scard", side_effect=Exception("Redis connection error")), \
             patch.object(test_redis, "ping", side_effect=Exception("Redis connection error")):
            
            degraded_service = CacheService(test_redis)
            
            assert await degraded_service.get_url("any") is None
            assert await degraded_service.set_url("any", "val") is False
            assert await degraded_service.delete_url("any") is False
            # SADD fallback returns True (assumes unique)
            assert await degraded_service.track_unique_click("any", "ip", "date") is True
            assert await degraded_service.get_unique_count("any", "date") == 0
            assert await degraded_service.get_analytics("any") is None
            assert await degraded_service.set_analytics("any", {}) is False
            assert await degraded_service.ping() is False
