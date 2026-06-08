"""
Analytics Schemas
──────────────────
Response models for analytics endpoints.
"""

from datetime import date, datetime

from pydantic import BaseModel


class CountryClicks(BaseModel):
    country: str
    clicks: int


class DayClicks(BaseModel):
    date: date
    total: int
    unique: int


class AnalyticsResponse(BaseModel):
    """Full analytics for a single short URL."""

    short_code: str
    original_url: str
    total_clicks: int
    unique_clicks: int
    created_at: datetime
    expires_at: datetime | None = None
    clicks_24h: int
    clicks_7d: int
    top_countries: list[CountryClicks]
    clicks_by_day: list[DayClicks]
