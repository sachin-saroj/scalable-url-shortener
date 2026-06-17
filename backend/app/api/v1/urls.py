"""
URL Endpoints
──────────────
POST /api/v1/shorten — Create a short URL
GET  /api/v1/urls    — List user's URLs
DELETE /api/v1/urls/{short_code} — Deactivate a URL

DESIGN:
- Route handlers are THIN controllers
- Business logic lives in URLService
- Dependencies injected via FastAPI's Depends()
"""

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.dependencies import DB, Cache, CurrentUser, OptionalUser, check_rate_limit
from app.schemas.bulk import BulkURLCreateRequest, BulkURLCreateResponse, BulkURLItemResult
from app.schemas.dashboard_stats import DashboardStatsResponse
from app.schemas.url import URLCreateRequest, URLListItem, URLListResponse, URLResponse
from app.services.security_service import check_url_safety
from app.services.url_service import URLService

router = APIRouter()
logger = structlog.get_logger(__name__)



@router.post(
    "/shorten",
    response_model=URLResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Shorten a URL",
    description="Create a shortened URL with optional custom alias and expiry.",
    dependencies=[Depends(check_rate_limit)],
)
async def shorten_url(
    request: URLCreateRequest,
    db: DB,
    cache: Cache,
    user: OptionalUser,
    background_tasks: BackgroundTasks,
):
    """
    Create a short URL.

    - Anonymous users can create URLs (no auth required)
    - Authenticated users get URLs linked to their account
    - Rate limited to prevent abuse
    """
    # Security check
    is_safe, reason = await check_url_safety(request.url)
    if not is_safe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"URL rejected: {reason}",
        )

    url_service = URLService(db, cache)
    try:
        result = await url_service.create_short_url(
            request,
            user_id=user.id if user else None,
            background_tasks=background_tasks,
        )
        logger.info("url_shortened", short_code=result.short_code, user_id=user.id if user else None)
        return result
    except ValueError as e:
        # Determine status code based on error
        error_msg = str(e)
        logger.warning("url_shortening_failed", error=error_msg, user_id=user.id if user else None)
        if "already taken" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg,
        )


@router.post(
    "/shorten/bulk",
    response_model=BulkURLCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk shorten URLs",
    description="Create up to 50 shortened URLs in a single request. Partial failures are reported per-item.",
    dependencies=[Depends(check_rate_limit)],
)
async def bulk_shorten_urls(
    request: BulkURLCreateRequest,
    db: DB,
    cache: Cache,
    user: OptionalUser,
    background_tasks: BackgroundTasks,
):
    """
    Bulk shorten multiple URLs.

    - Processes each URL independently
    - Security checks applied per URL
    - Partial failures don't block successful items
    """
    # Pre-filter unsafe URLs
    safe_requests = []
    results: list[BulkURLItemResult] = []

    for i, url_req in enumerate(request.urls):
        is_safe, reason = await check_url_safety(url_req.url)
        if not is_safe:
            results.append(BulkURLItemResult(
                index=i, success=False, error=f"URL rejected: {reason}",
            ))
        else:
            safe_requests.append((i, url_req))

    # Process safe URLs
    url_service = URLService(db, cache)
    for orig_index, url_req in safe_requests:
        try:
            result = await url_service.create_short_url(
                url_req,
                user_id=user.id if user else None,
                background_tasks=background_tasks,
            )
            results.append(BulkURLItemResult(
                index=orig_index, success=True, data=result,
            ))
        except ValueError as e:
            results.append(BulkURLItemResult(
                index=orig_index, success=False, error=str(e),
            ))

    # Sort by original index
    results.sort(key=lambda r: r.index)
    succeeded = sum(1 for r in results if r.success)

    return BulkURLCreateResponse(
        total=len(request.urls),
        succeeded=succeeded,
        failed=len(request.urls) - succeeded,
        results=results,
    )


@router.get(
    "/urls/stats",
    response_model=DashboardStatsResponse,
    summary="Get user dashboard statistics",
    description=(
        "Get overall statistics of links created by the user "
        "(total, active, expired, clicks, average)."
    ),
)
async def get_user_dashboard_stats(
    db: DB,
    cache: Cache,
    user: CurrentUser,
):
    url_service = URLService(db, cache)
    stats = await url_service.get_dashboard_stats(user.id)
    return stats


@router.get(
    "/urls",
    response_model=URLListResponse,
    summary="List my URLs",
    description="Get paginated list of URLs created by the authenticated user.",
)
async def list_user_urls(
    db: DB,
    cache: Cache,
    user: CurrentUser,
    page: int = 1,
    per_page: int = 20,
):
    """List all URLs created by the authenticated user."""
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20

    url_service = URLService(db, cache)
    url_list, total = await url_service.get_user_urls(user.id, page, per_page)

    return URLListResponse(
        urls=[URLListItem(**u) for u in url_list],
        total=total,
        page=page,
        per_page=per_page,
    )


@router.delete(
    "/urls/{short_code}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a URL",
    description="Soft-delete a URL (only by owner).",
)
async def deactivate_url(
    short_code: str,
    db: DB,
    cache: Cache,
    user: CurrentUser,
):
    """Deactivate a short URL. Only the owner can do this."""
    url_service = URLService(db, cache)
    try:
        await url_service.deactivate_url(short_code, user.id)
    except LookupError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't own this URL",
        )
