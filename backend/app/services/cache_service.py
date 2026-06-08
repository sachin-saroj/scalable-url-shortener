"""
Cache Service (Redis)
──────────────────────
Abstracts all Redis operations behind a clean interface.

PATTERN: Cache-Aside (Lazy Loading)
────────────────────────────────────
READ:  Check cache → if miss → query DB → write to cache → return
WRITE: Write to DB → write to cache

WHY abstract Redis behind a service?
- Swappable: can replace Redis with Memcached or in-memory cache
- Testable: can mock this service in unit tests
- Centralized: single place to manage TTLs, key patterns, error handling
- Resilient: handles Redis failures gracefully

KEY NAMING CONVENTION:
- url:{short_code}          → original URL (string)
- rate:{ip}:{window}        → request count (string)
- unique:{short_code}:{date} → set of IPs for unique tracking
- analytics:{short_code}     → cached analytics response (JSON)
"""

import json
import logging
from typing import Any, cast

from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class CacheService:
    """
    Redis cache service with graceful degradation.

    All methods catch Redis errors and return None/False
    to allow the application to function without cache.
    """

    def __init__(self, redis: Redis):
        self.redis = redis

    # ── URL Cache ──────────────────────────────────────

    async def get_url(self, short_code: str) -> str | None:
        """
        Get original URL from cache.

        Returns None on cache miss or Redis error.
        """
        try:
            result = await self.redis.get(f"url:{short_code}")
            if result:
                logger.debug(f"Cache HIT for {short_code}")
                return result.decode() if isinstance(result, bytes) else result
            logger.debug(f"Cache MISS for {short_code}")
            return None
        except Exception as e:
            logger.warning(f"Redis GET error (degraded): {e}")
            return None

    async def set_url(self, short_code: str, original_url: str, ttl: int = 86400) -> bool:
        """
        Cache a URL mapping.

        Args:
            short_code: The short code key
            original_url: The URL value to cache
            ttl: Time-to-live in seconds (default 24h)
        """
        try:
            await self.redis.setex(f"url:{short_code}", ttl, original_url)
            return True
        except Exception as e:
            logger.warning(f"Redis SET error (degraded): {e}")
            return False

    async def delete_url(self, short_code: str) -> bool:
        """Remove a URL from cache (used when URL is deactivated)."""
        try:
            await self.redis.delete(f"url:{short_code}")
            return True
        except Exception as e:
            logger.warning(f"Redis DELETE error: {e}")
            return False

    # ── Unique Click Tracking ──────────────────────────

    async def track_unique_click(self, short_code: str, ip: str, date_str: str) -> bool:
        """
        Track unique clicks using Redis SET.

        Returns True if this is a NEW unique click (IP not seen today).
        Returns False if IP already clicked today.

        WHY Redis SET?
        - O(1) membership check (SISMEMBER)
        - O(1) add (SADD)
        - Auto-expires (no manual cleanup)
        - Memory efficient for IP tracking
        """
        try:
            key = f"unique:{short_code}:{date_str}"
            # SADD returns 1 if new member, 0 if already exists
            result = await cast(Any, self.redis.sadd(key, ip))
            # Set TTL to 48h (covers timezone edge cases)
            await cast(Any, self.redis.expire(key, 172800))
            return cast(bool, result == 1)
        except Exception as e:
            logger.warning(f"Redis unique tracking error: {e}")
            return True  # Assume unique on error (over-count vs under-count)

    async def get_unique_count(self, short_code: str, date_str: str) -> int:
        """Get unique click count for a URL on a specific date."""
        try:
            return cast(int, await cast(Any, self.redis.scard(f"unique:{short_code}:{date_str}")))
        except Exception as e:
            logger.warning(f"Redis SCARD error: {e}")
            return 0

    # ── Analytics Cache ────────────────────────────────

    async def get_analytics(self, short_code: str) -> dict[str, Any] | None:
        """Get cached analytics response."""
        try:
            result = await cast(Any, self.redis.get(f"analytics:{short_code}"))
            if result:
                data = result.decode() if isinstance(result, bytes) else result
                return cast(dict[str, Any], json.loads(data))
            return None
        except Exception as e:
            logger.warning(f"Redis analytics GET error: {e}")
            return None

    async def set_analytics(
        self, short_code: str, data: dict[str, Any], ttl: int = 60
    ) -> bool:
        """Cache analytics response (short TTL since data changes frequently)."""
        try:
            await cast(
                Any,
                self.redis.setex(
                    f"analytics:{short_code}",
                    ttl,
                    json.dumps(data, default=str),
                ),
            )
            return True
        except Exception as e:
            logger.warning(f"Redis analytics SET error: {e}")
            return False

    # ── Generic Operations ─────────────────────────────

    async def ping(self) -> bool:
        """Check Redis connectivity."""
        try:
            return cast(bool, await cast(Any, self.redis.ping()))
        except Exception:
            return False

    async def flush_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern. Use with caution."""
        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern, count=100):
                keys.append(key)
            if keys:
                return cast(int, await cast(Any, self.redis.delete(*keys)))
            return 0
        except Exception as e:
            logger.warning(f"Redis flush error: {e}")
            return 0
