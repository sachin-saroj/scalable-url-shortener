"""
URL Export Endpoint
────────────────────
GET /api/v1/urls/export — Export user's URLs in CSV or JSON format.

Uses streaming responses for large datasets to avoid
loading all URLs into memory at once.
"""

import csv
import io
import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import noload

from app.dependencies import DB, CurrentUser
from app.models.url import URL

router = APIRouter()


@router.get(
    "/urls/export",
    summary="Export URLs",
    description="Export all URLs owned by the authenticated user in CSV or JSON format.",
)
async def export_urls(
    db: DB,
    user: CurrentUser,
    format: str = Query(
        default="csv",
        description="Export format: csv or json",
        pattern="^(csv|json)$",
    ),
):
    """
    Export user's URLs as a downloadable file.

    Supports CSV and JSON formats. Uses streaming to handle
    large numbers of URLs without excessive memory usage.
    """
    # Fetch all active URLs for the user
    query = (
        select(URL)
        .options(noload(URL.user))
        .where(URL.user_id == user.id, URL.is_active.is_(True))
        .order_by(URL.created_at.desc())
    )
    result = await db.execute(query)
    urls = result.scalars().all()

    if format == "csv":
        return _export_csv(urls)
    else:
        return _export_json(urls)


def _export_csv(urls: list[URL]) -> StreamingResponse:
    """Generate CSV export as a streaming response."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
        "short_code",
        "original_url",
        "custom_alias",
        "created_at",
        "expires_at",
        "is_active",
    ])

    # Data rows
    for url in urls:
        writer.writerow([
            url.effective_code,
            url.original_url,
            url.custom_alias or "",
            url.created_at.isoformat() if url.created_at else "",
            url.expires_at.isoformat() if url.expires_at else "",
            url.is_active,
        ])

    output.seek(0)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"urls_export_{timestamp}.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _export_json(urls: list[URL]) -> StreamingResponse:
    """Generate JSON export as a streaming response."""
    data = []
    for url in urls:
        data.append({
            "short_code": url.effective_code,
            "original_url": url.original_url,
            "custom_alias": url.custom_alias,
            "created_at": url.created_at.isoformat() if url.created_at else None,
            "expires_at": url.expires_at.isoformat() if url.expires_at else None,
            "is_active": url.is_active,
        })

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"urls_export_{timestamp}.json"
    json_content = json.dumps(data, indent=2)

    return StreamingResponse(
        iter([json_content]),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
