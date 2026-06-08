"""
Database Base Model
───────────────────
Declarative base for all SQLAlchemy ORM models.

WHY a separate base module?
- Avoids circular imports (models import Base, session imports Base)
- Single source of truth for the declarative base
- Clean separation of concerns
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass
