"""
V1 API Router
──────────────
Aggregates all v1 API routes under /api/v1 prefix.
"""

from fastapi import APIRouter

from app.api.v1 import analytics, auth, qr, urls

router = APIRouter(prefix="/api/v1")

router.include_router(urls.router, tags=["URLs"])
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(analytics.router, tags=["Analytics"])
router.include_router(qr.router, tags=["QR Code"])
