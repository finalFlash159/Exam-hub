"""
Base models and database setup
Provides common functionality for all database models
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Create base class for all models
class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class BaseModel(Base):
    """
    Abstract base model with common fields
    All models should inherit from this
    """
    __abstract__ = True
    
    # Primary key
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=lambda: str(uuid.uuid4()),
        index=True
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>" 