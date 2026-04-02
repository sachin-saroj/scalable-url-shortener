"""
URL Schemas (Pydantic)
──────────────────────
Request/Response validation models for URL endpoints.

WHY Pydantic schemas separate from ORM models?
- ORM models = database structure (internal)
- Pydantic schemas = API contract (external)
- Never expose internal DB structure to clients
- Validate input strictly before touching the database
"""

from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, field_validator
import re


class URLCreateRequest(BaseModel):
    """Request body for POST /shorten"""
    url: str = Field(
        ...,
        min_length=5,
        max_length=2048,
        description="The original URL to shorten",
        examples=["https://example.com/very/long/path?query=value"],
    )
    custom_alias: str | None = Field(
        None,
        min_length=3,
        max_length=50,
        description="Optional custom alias (3-50 chars, alphanumeric + hyphens)",
        examples=["my-brand"],
    )
    expires_in_hours: int | None = Field(
        None,
        ge=1,
        le=8760,  # Max 1 year
        description="Hours until the link expires (1-8760)",
        examples=[48],
    )

    @field_validator("url")
    @classmethod
    def validate_url_format(cls, v: str) -> str:
        """Ensure URL has a valid scheme."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("custom_alias")
    @classmethod
    def validate_custom_alias(cls, v: str | None) -> str | None:
        """Ensure alias contains only safe characters."""
        if v is None:
            return v
        if not re.match(r"^[a-zA-Z0-9\-_]+$", v):
            raise ValueError(
                "Custom alias can only contain letters, numbers, hyphens, and underscores"
            )
        # Prevent reserved paths
        reserved = {"api", "admin", "health", "docs", "redoc", "openapi.json"}
        if v.lower() in reserved:
            raise ValueError(f"'{v}' is a reserved path and cannot be used as an alias")
        return v


class URLResponse(BaseModel):
    """Response body for successful URL creation."""
    short_code: str
    short_url: str
    original_url: str
    created_at: datetime
    expires_at: datetime | None = None
    custom_alias: str | None = None

    model_config = {"from_attributes": True}


class URLListItem(BaseModel):
    """Single URL item in the user's URL list."""
    short_code: str
    short_url: str
    original_url: str
    total_clicks: int = 0
    created_at: datetime
    expires_at: datetime | None = None
    is_active: bool = True
    custom_alias: str | None = None

    model_config = {"from_attributes": True}


class URLListResponse(BaseModel):
    """Paginated list of user's URLs."""
    urls: list[URLListItem]
    total: int
    page: int
    per_page: int
