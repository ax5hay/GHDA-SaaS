"""Base model for SQLAlchemy."""

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, DateTime, func

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
