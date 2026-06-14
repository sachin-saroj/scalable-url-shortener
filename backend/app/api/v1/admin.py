"""
Admin Endpoints
───────────────
Routes reserved exclusively for platform administration.
- POST /api/v1/admin/urls/{short_code}/deactivate
- GET  /api/v1/admin/stats
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from app.dependencies import DB, AdminUser, Cache
from app.models.url import URL
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.post(
    "/urls/{short_code}/deactivate",
    status_code=status.HTTP_200_OK,
    summary="Admin deactivation override",
)
async def admin_deactivate_url(
    short_code: str,
    db: DB,
    cache: Cache,
    admin: AdminUser,
):
    """
    Deactivate any URL regardless of ownership (e.g., in response to abuse reports).
    Also invalidates Redis cache.
    """
    query = select(URL).where((URL.short_code == short_code) | (URL.custom_alias == short_code))
    result = await db.execute(query)
    url = result.scalar_one_or_none()

    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )

    url.is_active = False
    await db.commit()

    # Clear cache entries
    if url.short_code:
        await cache.delete_url(url.short_code)
    if url.custom_alias:
        await cache.delete_url(url.custom_alias)

    return {"status": "deactivated", "short_code": short_code}


@router.get(
    "/stats",
    status_code=status.HTTP_200_OK,
    summary="Platform-wide statistics",
)
async def admin_platform_stats(
    db: DB,
    admin: AdminUser,
):
    """
    Retrieve platform-wide usage metrics (total urls, total users).
    """
    total_urls = (await db.execute(select(func.count(URL.id)))).scalar() or 0
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0

    return {
        "total_urls": total_urls,
        "total_users": total_users,
    }
