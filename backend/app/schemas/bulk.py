"""
Bulk URL Schemas (Pydantic)
────────────────────────────
Request/Response validation models for bulk URL shortening.

Separating bulk schemas keeps the single-URL schema clean and
allows independent validation rules (e.g., max 50 URLs per batch).
"""

from pydantic import BaseModel, Field, field_validator

from app.schemas.url import URLCreateRequest, URLResponse


class BulkURLCreateRequest(BaseModel):
    """Request body for POST /api/v1/shorten/bulk"""

    urls: list[URLCreateRequest] = Field(
        ...,
        min_length=1,
        max_length=50,
        description="List of URLs to shorten (1-50 per request)",
    )

    @field_validator("urls")
    @classmethod
    def validate_no_duplicate_aliases(
        cls, v: list[URLCreateRequest],
    ) -> list[URLCreateRequest]:
        """Reject requests containing duplicate custom aliases."""
        aliases = [
            item.custom_alias for item in v if item.custom_alias is not None
        ]
        if len(aliases) != len(set(aliases)):
            raise ValueError(
                "Duplicate custom aliases found in bulk request"
            )
        return v


class BulkURLItemResult(BaseModel):
    """Result for a single URL in a bulk operation."""

    index: int = Field(description="Zero-based index of the URL in the request")
    success: bool
    data: URLResponse | None = None
    error: str | None = None


class BulkURLCreateResponse(BaseModel):
    """Response body for POST /api/v1/shorten/bulk"""

    total: int = Field(description="Total URLs submitted")
    succeeded: int = Field(description="Number of successfully shortened URLs")
    failed: int = Field(description="Number of URLs that failed")
    results: list[BulkURLItemResult]
