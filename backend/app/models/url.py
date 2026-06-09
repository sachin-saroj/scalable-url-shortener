"""
URL Model
─────────
Core model mapping short codes to original URLs.

DESIGN DECISIONS:
- BigInt auto-increment ID: Used for Base62 encoding → short code
- short_code with unique index: The HOT PATH lookup field
- custom_alias: Optional user-provided alias (separate unique index)
- user_id nullable: Allows anonymous URL creation
- expires_at nullable: Only set when expiry is requested
- is_active: Soft-delete (admin can deactivate malicious links)
- metadata (JSONB): Flexible storage for og:title, og:image, og:description

INDEXING STRATEGY:
- short_code: UNIQUE index (primary lookup, must be fast)
- custom_alias: UNIQUE partial index (only non-null values)
- user_id: Index for "my URLs" queries
- expires_at: Partial index for cleanup job (only active + has expiry)
"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    text,
    func,
    true,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    short_code: Mapped[str | None] = mapped_column(
        String(10), unique=True, nullable=True, index=True
    )
    custom_alias: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
        index=True,
    )
    user_id = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)

    # Relationships
    user = relationship("User", back_populates="urls", lazy="selectin")
    clicks = relationship("Click", back_populates="url", lazy="noload")

    # ── Partial Indexes (PostgreSQL-specific) ──────────
    __table_args__ = (
        Index(
            "idx_urls_expires_at_active",
            "expires_at",
            postgresql_where=text("expires_at IS NOT NULL AND is_active = true"),
        ),
    )

    @property
    def is_expired(self) -> bool:
        """Check if the URL has expired."""
        if self.expires_at is None:
            return False
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) >= expires_at

    @property
    def effective_code(self) -> str:
        """Return custom_alias if set, otherwise short_code."""
        return self.custom_alias or self.short_code or ""

    def __repr__(self) -> str:
        return f"<URL {self.short_code} → {self.original_url[:50]}>"
