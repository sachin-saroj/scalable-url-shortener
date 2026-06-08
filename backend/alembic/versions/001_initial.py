"""Initial schema - all tables

Revision ID: 001_initial
Revises:
Create Date: 2026-04-01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers
revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Users Table ────────────────────────────────
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("username", sa.String(50), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), server_default="user", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_username", "users", ["username"])

    # ── URLs Table ─────────────────────────────────
    op.create_table(
        "urls",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("short_code", sa.String(20), nullable=True),
        sa.Column("original_url", sa.Text(), nullable=False),
        sa.Column("custom_alias", sa.String(50), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("short_code"),
        sa.UniqueConstraint("custom_alias"),
    )
    op.create_index("ix_urls_short_code", "urls", ["short_code"], unique=True)
    op.create_index("ix_urls_user_id", "urls", ["user_id"])
    op.create_index(
        "idx_urls_expires_at_active",
        "urls",
        ["expires_at"],
        postgresql_where=sa.text("expires_at IS NOT NULL AND is_active = true"),
    )

    # ── Clicks Table ───────────────────────────────
    op.create_table(
        "clicks",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("url_id", sa.BigInteger(), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("referer", sa.Text(), nullable=True),
        sa.Column(
            "clicked_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["url_id"], ["urls.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_clicks_url_id_clicked_at", "clicks", ["url_id", "clicked_at"])

    # ── Daily Analytics Table ──────────────────────
    op.create_table(
        "daily_analytics",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("url_id", sa.BigInteger(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("total_clicks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unique_clicks", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["url_id"], ["urls.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_daily_analytics_url_date", "daily_analytics", ["url_id", "date"], unique=True
    )


def downgrade() -> None:
    op.drop_table("daily_analytics")
    op.drop_table("clicks")
    op.drop_table("urls")
    op.drop_table("users")
