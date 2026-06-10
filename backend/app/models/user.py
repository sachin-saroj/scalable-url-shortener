"""
User Model
──────────
Represents registered users who can create and manage short URLs.

DESIGN DECISIONS:
- UUID primary key: Non-sequential, prevents enumeration attacks
- Unique email + username: Two ways to identify a user
- Role field: Simple RBAC (user/admin), extensible to more roles
- is_active: Soft-delete capability (never hard-delete user data)
- Timestamps: Audit trail (created_at, updated_at)
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String, func, text, true
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, server_default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=true())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    urls = relationship("URL", back_populates="user", lazy="selectin")

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.email})>"
