"""
Click Model
────────────
Records every click/redirect event for analytics.

DESIGN DECISIONS:
- Separate table from URLs: Clicks are high-volume append-only data
- ip_address: For unique click tracking and geo-location
- user_agent: Browser/device analytics
- country/city: Pre-resolved geo-data (avoids re-lookups)
- referer: Where the click came from
- clicked_at indexed: Time-series queries (last 24h, last 7d)
- Composite index (url_id, clicked_at): Efficient per-URL time queries

SCALABILITY NOTE:
- This table will grow fast. In production, consider:
  - Table partitioning by date (PostgreSQL native partitioning)
  - Archiving old clicks to cold storage
  - Pre-aggregating into daily_analytics table
"""

from datetime import datetime

from sqlalchemy import BigInteger, String, Text, DateTime, ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Click(Base):
    __tablename__ = "clicks"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    url_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("urls.id", ondelete="CASCADE"),
        nullable=False,
    )
    ip_address: Mapped[str | None] = mapped_column(
        String(45), nullable=True  # IPv6 max length is 45
    )
    user_agent: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    country: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    city: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    referer: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )

    # Relationships
    url = relationship("URL", back_populates="clicks", lazy="selectin")

    # ── Composite Index for Analytics Queries ──────────
    __table_args__ = (
        Index("idx_clicks_url_id_clicked_at", "url_id", "clicked_at"),
    )

    def __repr__(self) -> str:
        return f"<Click url_id={self.url_id} at {self.clicked_at}>"
