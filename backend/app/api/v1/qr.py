"""
QR Code Endpoint
─────────────────
GET /api/v1/qr/{short_code} — Generate QR code for a short URL
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models.url import URL
from app.services.qr_service import generate_qr_code
from app.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get(
    "/qr/{short_code}",
    summary="Generate QR code",
    description="Generate a QR code PNG image for a short URL.",
    responses={
        200: {"content": {"image/png": {}}, "description": "QR code image"},
        404: {"description": "Short URL not found"},
    },
)
async def get_qr_code(
    short_code: str,
    size: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """Generate a QR code image for the given short URL."""
    # Validate the short code exists
    query = select(URL).where(
        (URL.short_code == short_code) | (URL.custom_alias == short_code)
    )
    result = await db.execute(query)
    url_record = result.scalar_one_or_none()

    if not url_record or not url_record.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )

    # Clamp size
    size = max(5, min(20, size))

    # Generate QR code for the full short URL
    full_url = f"{settings.BASE_URL}/{url_record.effective_code}"
    qr_bytes = generate_qr_code(full_url, size=size)

    return Response(
        content=qr_bytes,
        media_type="image/png",
        headers={
            "Content-Disposition": f'inline; filename="{short_code}.png"',
            "Cache-Control": "public, max-age=3600",
        },
    )
