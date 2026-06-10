from pydantic import BaseModel, Field


class DashboardStatsResponse(BaseModel):
    """Schema for dashboard overall statistics response."""

    total_links: int = Field(description="Total count of active (non-deactivated) links")
    active_links: int = Field(description="Count of active links that are not expired")
    expired_links: int = Field(description="Count of active links that have expired")
    total_clicks: int = Field(description="Total number of clicks across all active links")
    average_clicks_per_link: float = Field(description="Average number of clicks per active link")
