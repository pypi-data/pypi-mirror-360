"""Abstract database interfaces for multi-database support.

This module provides the foundation for supporting multiple database backends
(MongoDB, PostgreSQL, etc.) in the Essencia framework.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Protocol, Type, TypeVar, Union
from datetime import datetime
from contextlib import asynccontextmanager

from pydantic import BaseModel


T = TypeVar('T', bound='AbstractModel')


class DatabaseConfig(BaseModel):
    """Base configuration for database connections."""
    url: str
    database_name: str
    options: Dict[str, Any] = {}


class QueryBuilder(Protocol):
    """Protocol for building database-agnostic queries."""
    
    def where(self, **kwargs) -> 'QueryBuilder':
        """Add WHERE conditions."""
        ...
    
    def order_by(self, field: str, desc: bool = False) -> 'QueryBuilder':
        """Add ORDER BY clause."""
        ...
    
    def limit(self, n: int) -> 'QueryBuilder':
        """Add LIMIT clause."""
        ...
    
    def offset(self, n: int) -> 'QueryBuilder':
        """Add OFFSET clause."""
        ...
    
    def build(self) -> Any:
        """Build the final query object."""
        ...


class AbstractDatabase(ABC):
    """Abstract base class for database implementations."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._connection = None
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish database connection."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if database is connected."""
        pass
    
    @abstractmethod
    async def execute(self, query: Any, **kwargs) -> Any:
        """Execute a raw query."""
        pass
    
    @abstractmethod
    async def find_one(self, collection: str, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document/record."""
        pass
    
    @abstractmethod
    async def find_many(self, collection: str, filter: Dict[str, Any], 
                       limit: Optional[int] = None, skip: Optional[int] = None,
                       sort: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
        """Find multiple documents/records."""
        pass
    
    @abstractmethod
    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a single document/record and return its ID."""
        pass
    
    @abstractmethod
    async def insert_many(self, collection: str, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents/records and return their IDs."""
        pass
    
    @abstractmethod
    async def update_one(self, collection: str, filter: Dict[str, Any], 
                        update: Dict[str, Any]) -> int:
        """Update a single document/record and return affected count."""
        pass
    
    @abstractmethod
    async def update_many(self, collection: str, filter: Dict[str, Any], 
                         update: Dict[str, Any]) -> int:
        """Update multiple documents/records and return affected count."""
        pass
    
    @abstractmethod
    async def delete_one(self, collection: str, filter: Dict[str, Any]) -> int:
        """Delete a single document/record and return affected count."""
        pass
    
    @abstractmethod
    async def delete_many(self, collection: str, filter: Dict[str, Any]) -> int:
        """Delete multiple documents/records and return affected count."""
        pass
    
    @abstractmethod
    async def count(self, collection: str, filter: Dict[str, Any]) -> int:
        """Count documents/records matching filter."""
        pass
    
    @abstractmethod
    async def create_index(self, collection: str, keys: List[tuple], unique: bool = False) -> None:
        """Create an index on the collection."""
        pass
    
    @abstractmethod
    def get_query_builder(self) -> QueryBuilder:
        """Get a query builder for this database type."""
        pass
    
    @asynccontextmanager
    async def transaction(self):
        """Context manager for database transactions."""
        # Default implementation - override in subclasses that support transactions
        yield self


class SyncAbstractDatabase(ABC):
    """Abstract base class for synchronous database implementations."""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._connection = None
    
    @abstractmethod
    def connect(self) -> None:
        """Establish database connection."""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if database is connected."""
        pass
    
    @abstractmethod
    def execute(self, query: Any, **kwargs) -> Any:
        """Execute a raw query."""
        pass
    
    @abstractmethod
    def find_one(self, collection: str, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document/record."""
        pass
    
    @abstractmethod
    def find_many(self, collection: str, filter: Dict[str, Any], 
                  limit: Optional[int] = None, skip: Optional[int] = None,
                  sort: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
        """Find multiple documents/records."""
        pass
    
    @abstractmethod
    def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a single document/record and return its ID."""
        pass
    
    @abstractmethod
    def update_one(self, collection: str, filter: Dict[str, Any], 
                   update: Dict[str, Any]) -> int:
        """Update a single document/record and return affected count."""
        pass
    
    @abstractmethod
    def delete_one(self, collection: str, filter: Dict[str, Any]) -> int:
        """Delete a single document/record and return affected count."""
        pass
    
    @abstractmethod
    def count(self, collection: str, filter: Dict[str, Any]) -> int:
        """Count documents/records matching filter."""
        pass


class AbstractModel(BaseModel):
    """Abstract base model for database records."""
    
    # Class attributes to be set by subclasses
    __database__: Optional[Union[AbstractDatabase, SyncAbstractDatabase]] = None
    __collection_name__: Optional[str] = None
    __primary_key__: str = "id"
    
    @classmethod
    def get_collection_name(cls) -> str:
        """Get the collection/table name for this model."""
        if cls.__collection_name__:
            return cls.__collection_name__
        # Default to lowercase class name with underscores
        import re
        name = cls.__name__
        return re.sub('(?<!^)(?=[A-Z])', '_', name).lower()
    
    @classmethod
    def get_database(cls) -> Union[AbstractDatabase, SyncAbstractDatabase]:
        """Get the database instance for this model."""
        if not cls.__database__:
            raise ValueError(f"No database configured for {cls.__name__}")
        return cls.__database__
    
    @classmethod
    async def find_by_id(cls: Type[T], id: Any) -> Optional[T]:
        """Find a record by its primary key."""
        db = cls.get_database()
        if not isinstance(db, AbstractDatabase):
            raise TypeError("Async operation requires async database")
        
        filter = {cls.__primary_key__: id}
        doc = await db.find_one(cls.get_collection_name(), filter)
        if doc:
            return cls(**doc)
        return None
    
    @classmethod
    async def find_one(cls: Type[T], **kwargs) -> Optional[T]:
        """Find a single record matching the criteria."""
        db = cls.get_database()
        if not isinstance(db, AbstractDatabase):
            raise TypeError("Async operation requires async database")
        
        doc = await db.find_one(cls.get_collection_name(), kwargs)
        if doc:
            return cls(**doc)
        return None
    
    @classmethod
    async def find_many(cls: Type[T], limit: Optional[int] = None, 
                       skip: Optional[int] = None, **kwargs) -> List[T]:
        """Find multiple records matching the criteria."""
        db = cls.get_database()
        if not isinstance(db, AbstractDatabase):
            raise TypeError("Async operation requires async database")
        
        docs = await db.find_many(
            cls.get_collection_name(), 
            kwargs, 
            limit=limit, 
            skip=skip
        )
        return [cls(**doc) for doc in docs]
    
    async def save(self: T) -> T:
        """Save this record to the database."""
        db = self.get_database()
        if not isinstance(db, AbstractDatabase):
            raise TypeError("Async operation requires async database")
        
        data = self.model_dump(exclude={self.__primary_key__}, exclude_unset=True)
        
        # Check if this is an update or insert
        pk_value = getattr(self, self.__primary_key__, None)
        if pk_value:
            # Update existing
            filter = {self.__primary_key__: pk_value}
            await db.update_one(self.get_collection_name(), filter, {"$set": data})
        else:
            # Insert new
            new_id = await db.insert_one(self.get_collection_name(), data)
            setattr(self, self.__primary_key__, new_id)
        
        return self
    
    async def delete(self) -> int:
        """Delete this record from the database."""
        db = self.get_database()
        if not isinstance(db, AbstractDatabase):
            raise TypeError("Async operation requires async database")
        
        pk_value = getattr(self, self.__primary_key__, None)
        if not pk_value:
            raise ValueError("Cannot delete record without primary key")
        
        filter = {self.__primary_key__: pk_value}
        return await db.delete_one(self.get_collection_name(), filter)
    
    @classmethod
    async def count(cls, **kwargs) -> int:
        """Count records matching the criteria."""
        db = cls.get_database()
        if not isinstance(db, AbstractDatabase):
            raise TypeError("Async operation requires async database")
        
        return await db.count(cls.get_collection_name(), kwargs)


class DatabaseFactory:
    """Factory for creating database instances."""
    
    _databases: Dict[str, Union[AbstractDatabase, SyncAbstractDatabase]] = {}
    _adapters: Dict[str, Type[Union[AbstractDatabase, SyncAbstractDatabase]]] = {}
    
    @classmethod
    def register_adapter(cls, name: str, adapter_class: Type[Union[AbstractDatabase, SyncAbstractDatabase]]):
        """Register a database adapter."""
        cls._adapters[name] = adapter_class
    
    @classmethod
    def create_database(cls, name: str, db_type: str, config: DatabaseConfig) -> Union[AbstractDatabase, SyncAbstractDatabase]:
        """Create a database instance."""
        if db_type not in cls._adapters:
            raise ValueError(f"Unknown database type: {db_type}")
        
        adapter_class = cls._adapters[db_type]
        db = adapter_class(config)
        cls._databases[name] = db
        return db
    
    @classmethod
    def get_database(cls, name: str) -> Optional[Union[AbstractDatabase, SyncAbstractDatabase]]:
        """Get a database instance by name."""
        return cls._databases.get(name)