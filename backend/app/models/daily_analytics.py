"""
Daily Analytics Model
──────────────────────
Pre-aggregated daily metrics per URL.

WHY PRE-AGGREGATE?
- Counting clicks on every analytics API call is expensive (full table scan)
- Background worker aggregates hourly/daily into this table
- Analytics API reads from here = O(1) instead of O(n)

COMMON MISTAKE:
- Computing COUNT(*) on clicks table for every analytics request
- This is O(n) and gets slower as clicks grow
- Pre-aggregation is O(1) read, amortized O(1) write
"""

from datetime import date

from sqlalchemy import BigInteger, Integer, Date, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DailyAnalytics(Base):
    __tablename__ = "daily_analytics"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    url_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("urls.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(
        Date, nullable=False
    )
    total_clicks: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    unique_clicks: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    # ── Composite Index for Efficient Lookups ──────────
    __table_args__ = (
        Index("idx_daily_analytics_url_date", "url_id", "date", unique=True),
    )

    def __repr__(self) -> str:
        return f"<DailyAnalytics url_id={self.url_id} date={self.date} clicks={self.total_clicks}>"
