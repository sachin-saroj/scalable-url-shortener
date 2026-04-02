"""
Analytics Endpoints
────────────────────
GET /api/v1/analytics/{short_code} — Get URL analytics
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import DB, Cache, CurrentUser, get_db, get_cache
from app.models.url import URL
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import AnalyticsResponse

router = APIRouter()


@router.get(
    "/analytics/{short_code}",
    response_model=AnalyticsResponse,
    summary="Get URL analytics",
    description="Get comprehensive click analytics for a short URL. Requires authentication.",
)
async def get_url_analytics(
    short_code: str,
    db: DB,
    cache: Cache,
    user: CurrentUser,
):
    """
    Get analytics for a short URL.
    
    Only the URL owner can view analytics.
    Response is cached for 60 seconds.
    """
    # Find the URL and verify ownership
    query = select(URL).where(
        (URL.short_code == short_code) | (URL.custom_alias == short_code)
    )
    result = await db.execute(query)
    url_record = result.scalar_one_or_none()

    if not url_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )

    # Allow admins to see any URL's analytics
    if url_record.user_id != user.id and user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this URL's analytics",
        )

    analytics_service = AnalyticsService(db, cache)
    analytics_data = await analytics_service.get_analytics(short_code, url_record.id)

    return AnalyticsResponse(
        short_code=short_code,
        original_url=url_record.original_url,
        total_clicks=analytics_data["total_clicks"],
        unique_clicks=analytics_data["unique_clicks"],
        created_at=url_record.created_at,
        expires_at=url_record.expires_at,
        clicks_24h=analytics_data["clicks_24h"],
        clicks_7d=analytics_data["clicks_7d"],
        top_countries=analytics_data["top_countries"],
        clicks_by_day=analytics_data["clicks_by_day"],
    )
