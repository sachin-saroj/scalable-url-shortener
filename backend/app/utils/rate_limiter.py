"""
Rate Limiter (Redis-backed)
────────────────────────────
Sliding window rate limiting per IP address.

ALGORITHM: Sliding Window Counter
─────────────────────────────────
Uses two fixed windows and interpolates:
  rate = prev_window_count * (1 - elapsed/window_size) + current_window_count

WHY NOT Fixed Window?
- Fixed window allows burst at boundaries
- Example: 100 requests at 0:59 + 100 at 1:00 = 200 in 2 seconds
- Sliding window smooths this out

WHY NOT Token Bucket?
- More complex, requires continuous token refill
- Sliding window is simpler and sufficient for our scale

IMPLEMENTATION:
- Two Redis keys per IP: current window + previous window
- Each expires after 2x window duration
- Rate calculated by weighted sum

FAILURE MODE:
- If Redis is down → fail-open (allow requests with warning log)
- Reason: availability > perfect rate limiting
"""

import logging
import time
from typing import Any

from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Redis-backed sliding window rate limiter.

    Usage:
        limiter = RateLimiter(redis, max_requests=100, window_seconds=60)
        allowed, info = await limiter.is_allowed("192.168.1.1")
        if not allowed:
            raise HTTPException(429, detail=info)
    """

    def __init__(
        self,
        redis: Redis,
        max_requests: int = 100,
        window_seconds: int = 60,
    ):
        self.redis = redis
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def _get_window_key(self, identifier: str, window: int) -> str:
        """Generate Redis key for a specific window."""
        return f"rate:{identifier}:{window}"

    async def is_allowed(self, identifier: str) -> tuple[bool, dict[str, Any]]:
        """
        Check if request from identifier is within rate limit.

        Args:
            identifier: Client IP address or API key

        Returns:
            Tuple of (allowed: bool, info: dict with remaining/retry_after)
        """
        try:
            now = time.time()
            current_window = int(now // self.window_seconds)
            previous_window = current_window - 1
            elapsed = now - (current_window * self.window_seconds)

            # Get counts for current and previous windows
            current_key = self._get_window_key(identifier, current_window)
            previous_key = self._get_window_key(identifier, previous_window)

            pipe = self.redis.pipeline()
            pipe.get(current_key)
            pipe.get(previous_key)
            results = await pipe.execute()

            current_count = int(results[0] or 0)
            previous_count = int(results[1] or 0)

            # Sliding window calculation
            weight = 1 - (elapsed / self.window_seconds)
            weighted_count = previous_count * weight + current_count

            if weighted_count >= self.max_requests:
                # Calculate retry-after
                retry_after = int(self.window_seconds - elapsed) + 1

                # Extract client IP and path from scoped identifier for auditing
                parts = identifier.split(":", 1)
                ip = parts[0] if parts else identifier
                path = parts[1] if len(parts) > 1 else "unknown"
                logger.warning(
                    f"Rate limit exceeded for client {ip} on path {path}. "
                    f"Weighted count: {weighted_count:.1f}/{self.max_requests}."
                )

                return False, {
                    "detail": f"Rate limit exceeded. Try again in {retry_after} seconds.",
                    "retry_after": retry_after,
                    "limit": self.max_requests,
                    "remaining": 0,
                }

            # Increment current window
            pipe = self.redis.pipeline()
            pipe.incr(current_key)
            pipe.expire(current_key, self.window_seconds * 2)
            await pipe.execute()

            remaining = max(0, int(self.max_requests - weighted_count - 1))
            return True, {
                "limit": self.max_requests,
                "remaining": remaining,
                "reset": int((current_window + 1) * self.window_seconds),
            }

        except Exception as e:
            # Fail-open: allow request if Redis is down
            logger.warning(f"Rate limiter Redis error (fail-open): {e}")
            return True, {
                "limit": self.max_requests,
                "remaining": self.max_requests,
                "reset": 0,
            }
