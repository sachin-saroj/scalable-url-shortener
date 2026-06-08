"""
URL Service
────────────
Core business logic for URL shortening and retrieval.

ARCHITECTURE:
- This is the SERVICE LAYER (business logic only)
- It receives clean inputs from the API layer
- It interacts with the database and cache
- It does NOT handle HTTP concerns (status codes, headers)

COMMON MISTAKES AVOIDED:
1. Putting business logic in route handlers (untestable)
2. Direct DB access from routes (no caching layer)
3. Not checking URL validity before storing
4. Generating short codes with collision risk
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.click import Click
from app.models.url import URL
from app.schemas.url import URLCreateRequest, URLResponse
from app.services.cache_service import CacheService
from app.utils.base62 import encode_id
from app.utils.validators import is_valid_url, sanitize_url

logger = logging.getLogger(__name__)
settings = get_settings()


class URLService:
    """
    Handles URL creation, retrieval, and management.

    DEPENDENCY INJECTION:
    - db: AsyncSession (database operations)
    - cache: CacheService (Redis caching)

    WHY inject dependencies?
    - Testable: mock db/cache in unit tests
    - Flexible: swap implementations without changing logic
    - Clean: service doesn't know about FastAPI or Redis internals
    """

    def __init__(self, db: AsyncSession, cache: CacheService):
        self.db = db
        self.cache = cache

    async def create_short_url(
        self,
        request: URLCreateRequest,
        user_id: UUID | None = None,
    ) -> URLResponse:
        """
        Create a shortened URL.

        FLOW:
        1. Sanitize and validate the URL
        2. Check for duplicate (idempotent for same user + URL)
        3. If custom alias → check uniqueness
        4. Insert into database → get auto-increment ID
        5. Generate Base62 short code from ID
        6. Update record with short code
        7. Cache in Redis
        8. Return response

        IDEMPOTENCY:
        If the same user submits the same URL again, we return the
        existing short code instead of creating a duplicate.
        This is good API design — same input → same output.
        """
        # Step 1: Sanitize and validate
        clean_url = sanitize_url(request.url)
        is_valid, error_msg = is_valid_url(clean_url)
        if not is_valid:
            raise ValueError(error_msg)

        # Step 2: Check for existing URL (idempotency)
        existing = await self._find_existing_url(clean_url, user_id)
        if existing and not request.custom_alias:
            return self._build_response(existing)

        # Step 3: Handle custom alias
        if request.custom_alias:
            alias_exists = await self._check_alias_exists(request.custom_alias)
            if alias_exists:
                raise ValueError(f"Custom alias '{request.custom_alias}' is already taken")

        # Step 4: Calculate expiry
        expires_at = None
        if request.expires_in_hours:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=request.expires_in_hours)

        # Step 5: Insert URL record
        url_record = URL(
            original_url=clean_url,
            custom_alias=request.custom_alias,
            user_id=user_id,
            expires_at=expires_at,
        )
        self.db.add(url_record)
        await self.db.flush()  # Get the auto-increment ID without committing

        # Step 6: Generate short code from ID
        short_code = encode_id(url_record.id)
        url_record.short_code = short_code
        await self.db.commit()
        await self.db.refresh(url_record)

        # Step 7: Cache in Redis
        cache_ttl = settings.URL_CACHE_TTL
        if expires_at:
            # Cache TTL = time until expiry (don't cache longer than URL lives)
            remaining = (expires_at - datetime.now(timezone.utc)).total_seconds()
            cache_ttl = min(cache_ttl, int(remaining))

        effective_code = url_record.custom_alias or short_code
        await self.cache.set_url(effective_code, clean_url, ttl=cache_ttl)

        logger.info(f"Created short URL: {effective_code} → {clean_url[:80]}")

        # Step 8: Build and return response
        return self._build_response(url_record)

    async def get_original_url(self, code: str) -> tuple[str, int]:
        """
        Resolve a short code to the original URL.

        This is the HOT PATH — must be as fast as possible.

        FLOW:
        1. Check Redis cache (sub-ms)
        2. If miss → query PostgreSQL
        3. Check if expired → return 410
        4. Cache the result for next time
        5. Return original URL + URL id (for click tracking)

        Returns:
            Tuple of (original_url, url_id)

        Raises:
            LookupError: URL not found (404)
            ValueError: URL has expired (410)
        """
        # Step 1: Check cache
        cached_url = await self.cache.get_url(code)
        if cached_url:
            # Still need the URL ID for click tracking
            url_record = await self._find_by_code(code)
            if url_record and (not url_record.is_active):
                await self.cache.delete_url(code)
                raise LookupError("Short URL not found")
            if url_record and url_record.is_expired:
                await self.cache.delete_url(code)
                raise ValueError("This short URL has expired")
            # Check if cached destination URL is malformed
            is_valid, _ = is_valid_url(cached_url)
            if not is_valid:
                await self.cache.delete_url(code)
                raise ValueError("Destination URL is malformed")
            if url_record:
                return cached_url, url_record.id
            # Cache has stale data — URL was deleted from DB
            await self.cache.delete_url(code)

        # Step 2: Query database
        url_record = await self._find_by_code(code)
        if not url_record or not url_record.is_active:
            raise LookupError("Short URL not found")

        # Step 3: Check expiry
        if url_record.is_expired:
            raise ValueError("This short URL has expired")

        # Check if destination URL is malformed
        is_valid, _ = is_valid_url(url_record.original_url)
        if not is_valid:
            raise ValueError("Destination URL is malformed")

        # Step 4: Cache for next time
        cache_ttl = settings.URL_CACHE_TTL
        if url_record.expires_at:
            remaining = (url_record.expires_at - datetime.now(timezone.utc)).total_seconds()
            cache_ttl = min(cache_ttl, int(remaining))
        await self.cache.set_url(code, url_record.original_url, ttl=cache_ttl)

        return url_record.original_url, url_record.id

    async def get_user_urls(
        self,
        user_id: UUID,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        """
        Get paginated list of URLs created by a user.

        Returns:
            Tuple of (url_list, total_count)
        """
        # Count total
        count_query = select(func.count(URL.id)).where(
            URL.user_id == user_id,
            URL.is_active.is_(True),
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Fetch page
        offset = (page - 1) * per_page
        query = (
            select(URL)
            .where(URL.user_id == user_id, URL.is_active.is_(True))
            .order_by(URL.created_at.desc())
            .offset(offset)
            .limit(per_page)
        )
        result = await self.db.execute(query)
        urls = result.scalars().all()

        # Enrich with click counts
        url_list = []
        for url in urls:
            click_count = await self._get_click_count(url.id)
            url_list.append(
                {
                    "short_code": url.effective_code,
                    "short_url": f"{settings.BASE_URL}/{url.effective_code}",
                    "original_url": url.original_url,
                    "total_clicks": click_count,
                    "created_at": url.created_at,
                    "expires_at": url.expires_at,
                    "is_active": url.is_active,
                    "custom_alias": url.custom_alias,
                }
            )

        return url_list, total

    async def deactivate_url(self, code: str, user_id: UUID) -> bool:
        """Soft-delete a URL (only by owner)."""
        url_record = await self._find_by_code(code)
        if not url_record:
            raise LookupError("Short URL not found")
        if url_record.user_id != user_id:
            raise PermissionError("You don't own this URL")

        url_record.is_active = False
        await self.db.commit()
        await self.cache.delete_url(code)
        return True

    # ── Private Helpers ────────────────────────────────

    async def _find_existing_url(self, original_url: str, user_id: UUID | None) -> URL | None:
        """Find existing URL for idempotency check."""
        query = select(URL).where(
            URL.original_url == original_url,
            URL.is_active.is_(True),
        )
        if user_id:
            query = query.where(URL.user_id == user_id)
        else:
            query = query.where(URL.user_id.is_(None))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _find_by_code(self, code: str) -> URL | None:
        """Find URL by short_code or custom_alias."""
        query = select(URL).where((URL.short_code == code) | (URL.custom_alias == code))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _check_alias_exists(self, alias: str) -> bool:
        """Check if a custom alias is already taken."""
        query = select(func.count(URL.id)).where(URL.custom_alias == alias)
        result = await self.db.execute(query)
        return (result.scalar() or 0) > 0

    async def _get_click_count(self, url_id: int) -> int:
        """Get total click count for a URL."""
        query = select(func.count(Click.id)).where(Click.url_id == url_id)
        result = await self.db.execute(query)
        return result.scalar() or 0

    def _build_response(self, url: URL) -> URLResponse:
        """Build API response from URL model."""
        effective_code = url.custom_alias or url.short_code
        return URLResponse(
            short_code=effective_code,
            short_url=f"{settings.BASE_URL}/{effective_code}",
            original_url=url.original_url,
            created_at=url.created_at,
            expires_at=url.expires_at,
            custom_alias=url.custom_alias,
        )
