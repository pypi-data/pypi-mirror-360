"""Database module for Essencia application."""

from .mongodb import MongoDB
from .redis_client import RedisClient
from .sync_mongodb import Database

# Abstract database interfaces
from .abstract import (
    AbstractDatabase,
    SyncAbstractDatabase,
    AbstractModel,
    DatabaseConfig,
    DatabaseFactory,
    QueryBuilder
)

# Database adapters
from .mongodb_adapter import MongoDBAdapter, SyncMongoDBAdapter
from .postgresql_adapter import PostgreSQLAdapter

# Register adapters with factory
DatabaseFactory.register_adapter('mongodb', MongoDBAdapter)
DatabaseFactory.register_adapter('mongodb_sync', SyncMongoDBAdapter)
DatabaseFactory.register_adapter('postgresql', PostgreSQLAdapter)

__all__ = [
    # Legacy classes
    "MongoDB", 
    "RedisClient", 
    "Database",
    # Abstract interfaces
    "AbstractDatabase",
    "SyncAbstractDatabase",
    "AbstractModel",
    "DatabaseConfig",
    "DatabaseFactory",
    "QueryBuilder",
    # Adapters
    "MongoDBAdapter",
    "SyncMongoDBAdapter",
    "PostgreSQLAdapter",
]