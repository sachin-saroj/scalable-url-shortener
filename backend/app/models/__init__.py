"""
Models Package
──────────────
Exports all ORM models so Alembic can discover them.
"""

from app.models.user import User
from app.models.url import URL
from app.models.click import Click
from app.models.daily_analytics import DailyAnalytics

__all__ = ["User", "URL", "Click", "DailyAnalytics"]
