"""SQL-based model base classes for PostgreSQL and other SQL databases."""
from typing import Any, ClassVar, Dict, List, Optional, Type, TypeVar, Union
from datetime import datetime
import uuid
from pydantic import Field, field_validator, ConfigDict

from ..database.abstract import AbstractModel, AbstractDatabase, SyncAbstractDatabase
from ..database.postgresql_adapter import PostgreSQLAdapter


T = TypeVar('T', bound='SQLModel')


class SQLModel(AbstractModel):
    """Base model for SQL databases (PostgreSQL, MySQL, SQLite).
    
    This model provides a MongoDB-like interface for SQL databases,
    storing data in a flexible JSONB format while maintaining compatibility
    with the existing model structure.
    """
    
    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            uuid.UUID: lambda v: str(v)
        }
    )
    
    # Override primary key to use UUID by default
    __primary_key__: str = "id"
    
    # ID field - can be overridden in subclasses
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Timestamps
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    
    @field_validator('id', mode='before')
    @classmethod
    def ensure_string_id(cls, v):
        """Ensure ID is always a string."""
        if v is None:
            return str(uuid.uuid4())
        return str(v)
    
    def model_dump_for_db(self) -> Dict[str, Any]:
        """Prepare model data for database storage.
        
        Separates system fields (id, timestamps) from user data.
        """
        data = self.model_dump(exclude_unset=True)
        
        # Extract system fields
        id_value = data.pop('id', None)
        created_at = data.pop('created_at', None)
        updated_at = data.pop('updated_at', None)
        
        # The rest goes into the JSONB data column
        return {
            'id': id_value,
            'created_at': created_at,
            'updated_at': updated_at,
            'data': data
        }
    
    @classmethod
    def from_db_row(cls: Type[T], row: Dict[str, Any]) -> T:
        """Create model instance from database row."""
        data = row.get('data', {}).copy()
        data['id'] = row.get('id')
        data['created_at'] = row.get('created_at')
        data['updated_at'] = row.get('updated_at')
        return cls(**data)
    
    # Sync methods for compatibility
    
    @classmethod
    def find_by_id(cls: Type[T], id: Any) -> Optional[T]:
        """Synchronous find by ID - requires sync database."""
        db = cls.get_database()
        if not isinstance(db, SyncAbstractDatabase):
            raise TypeError("Sync operation requires sync database")
        
        doc = db.find_one(cls.get_collection_name(), {'id': str(id)})
        if doc:
            return cls(**doc)
        return None
    
    @classmethod
    def find_one(cls: Type[T], **kwargs) -> Optional[T]:
        """Synchronous find one - requires sync database."""
        db = cls.get_database()
        if not isinstance(db, SyncAbstractDatabase):
            raise TypeError("Sync operation requires sync database")
        
        doc = db.find_one(cls.get_collection_name(), kwargs)
        if doc:
            return cls(**doc)
        return None
    
    @classmethod
    def find(cls: Type[T], filter: Optional[Dict[str, Any]] = None, 
             limit: Optional[int] = None, skip: Optional[int] = None,
             sort: Optional[List[tuple]] = None) -> List[T]:
        """Synchronous find many - requires sync database."""
        db = cls.get_database()
        if not isinstance(db, SyncAbstractDatabase):
            raise TypeError("Sync operation requires sync database")
        
        filter = filter or {}
        docs = db.find_many(
            cls.get_collection_name(), 
            filter, 
            limit=limit, 
            skip=skip,
            sort=sort
        )
        return [cls(**doc) for doc in docs]
    
    def save_self(self: T) -> T:
        """Synchronous save - requires sync database."""
        db = self.get_database()
        if not isinstance(db, SyncAbstractDatabase):
            raise TypeError("Sync operation requires sync database")
        
        # Update timestamp
        self.updated_at = datetime.utcnow()
        
        data = self.model_dump(exclude={'id'}, exclude_unset=True)
        
        if self.id:
            # Update existing
            db.update_one(
                self.get_collection_name(), 
                {'id': self.id}, 
                data
            )
        else:
            # Insert new
            self.id = db.insert_one(self.get_collection_name(), data)
        
        return self
    
    def update_self(self: T, **kwargs) -> T:
        """Synchronous update - requires sync database."""
        db = self.get_database()
        if not isinstance(db, SyncAbstractDatabase):
            raise TypeError("Sync operation requires sync database")
        
        if not self.id:
            raise ValueError("Cannot update record without ID")
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.updated_at = datetime.utcnow()
        
        data = self.model_dump(exclude={'id'}, exclude_unset=True)
        db.update_one(
            self.get_collection_name(), 
            {'id': self.id}, 
            data
        )
        
        return self
    
    def delete_self(self) -> int:
        """Synchronous delete - requires sync database."""
        db = self.get_database()
        if not isinstance(db, SyncAbstractDatabase):
            raise TypeError("Sync operation requires sync database")
        
        if not self.id:
            raise ValueError("Cannot delete record without ID")
        
        return db.delete_one(self.get_collection_name(), {'id': self.id})
    
    @classmethod
    def count_documents(cls, filter: Optional[Dict[str, Any]] = None) -> int:
        """Synchronous count - requires sync database."""
        db = cls.get_database()
        if not isinstance(db, SyncAbstractDatabase):
            raise TypeError("Sync operation requires sync database")
        
        filter = filter or {}
        return db.count(cls.get_collection_name(), filter)
    
    # Additional SQL-specific methods
    
    @classmethod
    async def create_table(cls):
        """Ensure table exists in database (PostgreSQL-specific)."""
        db = cls.get_database()
        if isinstance(db, PostgreSQLAdapter):
            await db._ensure_table_exists(cls.get_collection_name())
    
    @classmethod
    def sync_create_table(cls):
        """Synchronous version of create_table."""
        # This would need to be implemented in a sync PostgreSQL adapter
        pass
    
    # Query builder support
    
    @classmethod
    def query(cls):
        """Get a query builder for this model."""
        db = cls.get_database()
        if hasattr(db, 'get_query_builder'):
            return db.get_query_builder()
        raise NotImplementedError("Query builder not available for this database")
    
    # Transaction support
    
    @classmethod
    async def transaction(cls):
        """Get a transaction context manager."""
        db = cls.get_database()
        if isinstance(db, AbstractDatabase):
            return db.transaction()
        raise NotImplementedError("Transactions not available for this database")


class TimestampedSQLModel(SQLModel):
    """SQL model with automatic timestamp management."""
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def model_dump_for_db(self) -> Dict[str, Any]:
        """Update timestamps before saving."""
        self.updated_at = datetime.utcnow()
        return super().model_dump_for_db()


class SoftDeleteSQLModel(TimestampedSQLModel):
    """SQL model with soft delete support."""
    
    deleted_at: Optional[datetime] = None
    is_deleted: bool = Field(default=False)
    
    @classmethod
    async def find_many(cls: Type[T], limit: Optional[int] = None, 
                       skip: Optional[int] = None, include_deleted: bool = False,
                       **kwargs) -> List[T]:
        """Find many with soft delete filter."""
        if not include_deleted:
            kwargs['is_deleted'] = False
        return await super().find_many(limit=limit, skip=skip, **kwargs)
    
    @classmethod
    def find(cls: Type[T], filter: Optional[Dict[str, Any]] = None, 
             limit: Optional[int] = None, skip: Optional[int] = None,
             sort: Optional[List[tuple]] = None, include_deleted: bool = False) -> List[T]:
        """Sync find with soft delete filter."""
        filter = filter or {}
        if not include_deleted:
            filter['is_deleted'] = False
        return super().find(filter=filter, limit=limit, skip=skip, sort=sort)
    
    async def soft_delete(self) -> None:
        """Mark record as deleted without removing from database."""
        self.deleted_at = datetime.utcnow()
        self.is_deleted = True
        await self.save()
    
    def sync_soft_delete(self) -> None:
        """Sync version of soft delete."""
        self.deleted_at = datetime.utcnow()
        self.is_deleted = True
        self.save_self()
    
    async def restore(self) -> None:
        """Restore a soft-deleted record."""
        self.deleted_at = None
        self.is_deleted = False
        await self.save()
    
    def sync_restore(self) -> None:
        """Sync version of restore."""
        self.deleted_at = None
        self.is_deleted = False
        self.save_self()