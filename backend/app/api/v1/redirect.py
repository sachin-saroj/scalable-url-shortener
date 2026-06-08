"""
Redirect Endpoint
──────────────────
GET /{short_code} — The HOT PATH

This is the most critical endpoint in the system.
Every microsecond of latency here matters.

DESIGN DECISIONS:
- Mounted at root level (not under /api/v1) for shortest possible URLs
- 302 redirect (not 301) to preserve analytics on repeat visits
- Click recording is fire-and-forget (BackgroundTasks)
- Redis checked first, DB only on cache miss
"""

from fastapi import APIRouter, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.dependencies import get_db, get_cache
from app.services.url_service import URLService
from app.services.analytics_service import AnalyticsService
from app.services.cache_service import CacheService
from app.services.geo_service import get_location
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get(
    "/{short_code}",
    summary="Redirect to original URL",
    description="Resolve short code and redirect to the original URL.",
    response_class=RedirectResponse,
    status_code=status.HTTP_302_FOUND,
)
async def redirect_to_url(
    short_code: str,
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    cache: CacheService = Depends(get_cache),
):
    """
    The redirect endpoint — HOT PATH.
    
    Flow:
    1. Resolve short_code → original_url (cache → DB)
    2. Fire background task to record click
    3. Return 302 redirect immediately
    
    WHY BackgroundTasks?
    - Click recording happens AFTER the response is sent
    - User doesn't wait for DB write
    - Redirect latency = cache lookup time only (~1ms)
    """
    url_service = URLService(db, cache)

    try:
        original_url, url_id = await url_service.get_original_url(short_code)
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )
    except ValueError as e:
        if "malformed" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail=str(e),
        )

    # Extract client info for analytics
    client_ip = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    if not client_ip:
        client_ip = request.client.host if request.client else None

    user_agent = request.headers.get("User-Agent")
    referer = request.headers.get("Referer")

    # Fire-and-forget click recording
    background_tasks.add_task(
        _record_click_background,
        db=db,
        cache=cache,
        url_id=url_id,
        short_code=short_code,
        ip_address=client_ip,
        user_agent=user_agent,
        referer=referer,
    )

    return RedirectResponse(url=original_url, status_code=status.HTTP_302_FOUND)


async def _record_click_background(
    db: AsyncSession,
    cache: CacheService,
    url_id: int,
    short_code: str,
    ip_address: str | None,
    user_agent: str | None,
    referer: str | None,
):
    """
    Background task to record a click.
    
    Runs after the redirect response is sent.
    Failure here does NOT affect the user experience.
    """
    try:
        # Resolve geo-location
        geo = get_location(ip_address) if ip_address else {"country": None, "city": None}

        analytics_service = AnalyticsService(db, cache)
        await analytics_service.record_click(
            url_id=url_id,
            short_code=short_code,
            ip_address=ip_address,
            user_agent=user_agent,
            referer=referer,
            country=geo["country"],
            city=geo["city"],
        )
    except Exception as e:
        # Log but don't crash — analytics failure is non-critical
        import logging
        logging.getLogger(__name__).error(f"Click recording failed: {e}")
