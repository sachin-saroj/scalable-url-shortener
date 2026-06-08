"""
Models Package
──────────────
Exports all ORM models so Alembic can discover them.
"""

from app.models.click import Click
from app.models.daily_analytics import DailyAnalytics
from app.models.url import URL
from app.models.user import User

__all__ = ["URL", "Click", "DailyAnalytics", "User"]
