"""
Base repository class
Provides common CRUD operations for all repositories
"""

import logging
from typing import Dict, Any, List, Optional, Type, TypeVar, Generic
from uuid import uuid4

from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.models.base import BaseModel

logger = logging.getLogger(__name__)

# Type variable for model
ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations
    """
    
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        Initialize repository
        
        Args:
            model: SQLAlchemy model class
            session: Async database session
        """
        self.model = model
        self.session = session
        self.logger = logging.getLogger(f"{__name__}.{model.__name__}")
    
    async def create(self, **kwargs) -> ModelType:
        """
        Create a new record
        
        Args:
            **kwargs: Fields for the new record
            
        Returns:
            Created model instance
        """
        # Generate ID if not provided
        if 'id' not in kwargs:
            kwargs['id'] = str(uuid4())
            
        instance = self.model(**kwargs)
        self.session.add(instance)
        
        try:
            await self.session.commit()
            await self.session.refresh(instance)
            self.logger.info(f"Created {self.model.__name__} with ID: {instance.id}")
            return instance
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Failed to create {self.model.__name__}: {e}")
            raise
    
    async def get_by_id(self, id: str) -> Optional[ModelType]:
        """
        Get record by ID
        
        Args:
            id: Record ID
            
        Returns:
            Model instance if found, None otherwise
        """
        try:
            result = await self.session.execute(
                select(self.model).where(self.model.id == id)
            )
            instance = result.scalar_one_or_none()
            
            if instance:
                self.logger.debug(f"Found {self.model.__name__} with ID: {id}")
            else:
                self.logger.debug(f"No {self.model.__name__} found with ID: {id}")
                
            return instance
            
        except Exception as e:
            self.logger.error(f"Failed to get {self.model.__name__} by ID {id}: {e}")
            raise
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get all records with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of model instances
        """
        try:
            result = await self.session.execute(
                select(self.model)
                .offset(skip)
                .limit(limit)
                .order_by(self.model.created_at.desc())
            )
            instances = result.scalars().all()
            
            self.logger.debug(f"Retrieved {len(instances)} {self.model.__name__} records")
            return list(instances)
            
        except Exception as e:
            self.logger.error(f"Failed to get all {self.model.__name__}: {e}")
            raise
    
    async def update(self, id: str, **kwargs) -> Optional[ModelType]:
        """
        Update record by ID
        
        Args:
            id: Record ID
            **kwargs: Fields to update
            
        Returns:
            Updated model instance if found, None otherwise
        """
        try:
            # Remove None values
            update_data = {k: v for k, v in kwargs.items() if v is not None}
            
            if not update_data:
                self.logger.warning(f"No data to update for {self.model.__name__} ID: {id}")
                return await self.get_by_id(id)
            
            result = await self.session.execute(
                update(self.model)
                .where(self.model.id == id)
                .values(**update_data)
                .returning(self.model)
            )
            
            instance = result.scalar_one_or_none()
            
            if instance:
                await self.session.commit()
                await self.session.refresh(instance)
                self.logger.info(f"Updated {self.model.__name__} with ID: {id}")
            else:
                self.logger.warning(f"No {self.model.__name__} found to update with ID: {id}")
                
            return instance
            
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Failed to update {self.model.__name__} ID {id}: {e}")
            raise
    
    async def delete(self, id: str) -> bool:
        """
        Delete record by ID
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            result = await self.session.execute(
                delete(self.model).where(self.model.id == id)
            )
            
            if result.rowcount > 0:
                await self.session.commit()
                self.logger.info(f"Deleted {self.model.__name__} with ID: {id}")
                return True
            else:
                self.logger.warning(f"No {self.model.__name__} found to delete with ID: {id}")
                return False
                
        except Exception as e:
            await self.session.rollback()
            self.logger.error(f"Failed to delete {self.model.__name__} ID {id}: {e}")
            raise
    
    async def count(self) -> int:
        """
        Count total records
        
        Returns:
            Total number of records
        """
        try:
            result = await self.session.execute(
                select(func.count(self.model.id))
            )
            count = result.scalar()
            
            self.logger.debug(f"Total {self.model.__name__} count: {count}")
            return count or 0
            
        except Exception as e:
            self.logger.error(f"Failed to count {self.model.__name__}: {e}")
            raise
    
    async def exists(self, id: str) -> bool:
        """
        Check if record exists by ID
        
        Args:
            id: Record ID
            
        Returns:
            True if exists, False otherwise
        """
        try:
            result = await self.session.execute(
                select(func.count(self.model.id)).where(self.model.id == id)
            )
            count = result.scalar()
            return (count or 0) > 0
            
        except Exception as e:
            self.logger.error(f"Failed to check {self.model.__name__} existence for ID {id}: {e}")
            raise 