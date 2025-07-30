"""
Async MongoDB database module using Motor.

This module provides async database operations for high-performance
MongoDB interactions using the Motor async driver.
"""

import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

try:
    import motor.motor_asyncio
    from pymongo import ASCENDING, DESCENDING, TEXT
    from pymongo.errors import DuplicateKeyError, OperationFailure
    from pymongo.server_api import ServerApi
    MOTOR_AVAILABLE = True
except ImportError:
    MOTOR_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Motor not installed. Async MongoDB operations will not be available.")

from essencia.core import Config

logger = logging.getLogger(__name__)

# Global async database instance
_async_db_instance = None


class AsyncMongoDB:
    """
    Async database class for managing MongoDB connections and operations using Motor.
    """
    
    def __init__(self, database_name: str = None):
        """
        Initializes the Async Database instance.
        
        Args:
            database_name: The name of the database to connect to.
        """
        if not MOTOR_AVAILABLE:
            raise ImportError(
                "Motor is not installed. Install with: pip install motor"
            )
        
        self.config = Config.from_env()
        self.database_name = database_name or self.config.database.mongodb_database
        self._connected = False
        
        # Create async MongoDB client
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            self.config.database.mongodb_url,
            server_api=ServerApi('1'),
            maxPoolSize=100,
            minPoolSize=10,
            maxIdleTimeMS=45000,
            connectTimeoutMS=30000,
            serverSelectionTimeoutMS=30000,
            retryWrites=True,
            retryReads=True
        )
        
        self.db = self.client[self.database_name]
    
    async def initialize(self):
        """Initialize database connection and create indexes."""
        try:
            # Test connection
            self._connected = await self.ping()
            if self._connected:
                logger.info(f"Async MongoDB connected to database: {self.database_name}")
        except Exception as e:
            logger.error(f"Failed to initialize async MongoDB connection: {e}")
            self._connected = False
    
    async def ping(self) -> bool:
        """
        Pings the MongoDB server to check the connection status.
        
        Returns:
            bool: True if connected, False otherwise.
        """
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Failed to ping MongoDB: {e}")
            return False
    
    async def find(self, collection: str, query: dict) -> List[dict]:
        """
        Find documents in a collection.
        
        Args:
            collection: Collection name
            query: MongoDB query
            
        Returns:
            List of documents
        """
        try:
            import asyncio
            # Check if we have a running event loop
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                logger.warning("No running event loop for async find operation")
                return []
            
            cursor = self.db[collection].find(query)
            return await cursor.to_list(length=None)
        except asyncio.CancelledError:
            logger.debug("Find operation cancelled")
            return []
        except RuntimeError as e:
            if "Event loop is closed" in str(e):
                logger.debug("Event loop closed, ignoring find operation")
                return []
            logger.error(f"Runtime error in find operation: {e}")
            return []
        except Exception as e:
            logger.error(f"Error in find operation: {e}")
            return []
    
    async def find_one(self, collection: str, query: dict) -> Optional[dict]:
        """
        Find a single document in a collection.
        
        Args:
            collection: Collection name
            query: MongoDB query
            
        Returns:
            Document or None
        """
        try:
            import asyncio
            # Check if we have a running event loop
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                logger.warning("No running event loop for async find_one operation")
                return None
            
            return await self.db[collection].find_one(query)
        except asyncio.CancelledError:
            logger.debug("Find_one operation cancelled")
            return None
        except RuntimeError as e:
            if "Event loop is closed" in str(e):
                logger.debug("Event loop closed, ignoring find_one operation")
                return None
            logger.error(f"Runtime error in find_one operation: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in find_one operation: {e}")
            return None
    
    async def save_one(self, collection: str, document: dict) -> dict:
        """
        Save a document (insert or update).
        
        Args:
            collection: Collection name
            document: Document to save
            
        Returns:
            Saved document with _id
        """
        try:
            if '_id' in document and document['_id'] is not None:
                # Update existing document
                await self.db[collection].replace_one(
                    {'_id': document['_id']},
                    document
                )
            else:
                # Insert new document
                result = await self.db[collection].insert_one(document)
                document['_id'] = result.inserted_id
            
            return document
        except Exception as e:
            logger.error(f"Error saving document: {e}")
            raise
    
    async def update_one(self, collection: str, query: dict, update: dict) -> bool:
        """
        Update a single document.
        
        Args:
            collection: Collection name
            query: Query to find document
            update: Update operations
            
        Returns:
            True if successful
        """
        try:
            result = await self.db[collection].update_one(query, update)
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False
    
    async def update_many(self, collection: str, query: dict, update: dict) -> int:
        """
        Update multiple documents.
        
        Args:
            collection: Collection name
            query: Query to find documents
            update: Update operations
            
        Returns:
            Number of documents updated
        """
        try:
            result = await self.db[collection].update_many(query, update)
            return result.modified_count
        except Exception as e:
            logger.error(f"Error updating documents: {e}")
            return 0
    
    async def delete_one(self, collection: str, query: dict) -> bool:
        """
        Delete a single document.
        
        Args:
            collection: Collection name
            query: Query to find document
            
        Returns:
            True if successful
        """
        try:
            result = await self.db[collection].delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False
    
    async def count(self, collection: str, query: dict = None) -> int:
        """
        Count documents in a collection.
        
        Args:
            collection: Collection name
            query: Optional query filter
            
        Returns:
            Document count
        """
        try:
            query = query or {}
            return await self.db[collection].count_documents(query)
        except Exception as e:
            logger.error(f"Error counting documents: {e}")
            return 0
    
    async def aggregate(self, collection: str, pipeline: list) -> List[dict]:
        """
        Execute aggregation pipeline.
        
        Args:
            collection: Collection name
            pipeline: Aggregation pipeline
            
        Returns:
            Aggregation results
        """
        try:
            cursor = self.db[collection].aggregate(pipeline)
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Error in aggregation: {e}")
            return []
    
    async def find_paginated(self, collection: str, query: dict,
                           page: int = 1, page_size: int = 50,
                           sort: Optional[List[tuple]] = None) -> Dict[str, Any]:
        """
        Find documents with pagination.
        
        Args:
            collection: Collection name
            query: MongoDB query
            page: Page number (1-based)
            page_size: Items per page
            sort: Sort specification
            
        Returns:
            Paginated results
        """
        try:
            # Calculate skip
            skip = (page - 1) * page_size
            
            # Get total count
            total = await self.count(collection, query)
            
            # Get results
            cursor = self.db[collection].find(query)
            
            if sort:
                cursor = cursor.sort(sort)
            
            cursor = cursor.skip(skip).limit(page_size)
            results = await cursor.to_list(length=page_size)
            
            # Calculate pagination info
            pages = (total + page_size - 1) // page_size
            
            return {
                'results': results,
                'page': page,
                'pages': pages,
                'total': total,
                'has_next': page < pages,
                'has_prev': page > 1
            }
        except Exception as e:
            logger.error(f"Error in paginated query: {e}")
            return {
                'results': [],
                'page': page,
                'pages': 0,
                'total': 0,
                'has_next': False,
                'has_prev': False
            }
    
    async def bulk_insert(self, collection: str, documents: List[dict]) -> bool:
        """
        Insert multiple documents.
        
        Args:
            collection: Collection name
            documents: List of documents
            
        Returns:
            True if successful
        """
        try:
            if documents:
                await self.db[collection].insert_many(documents)
            return True
        except Exception as e:
            logger.error(f"Error in bulk insert: {e}")
            return False
    
    async def create_index(self, collection: str, keys: List[tuple], **kwargs):
        """
        Create an index on a collection.
        
        Args:
            collection: Collection name
            keys: Index specification
            **kwargs: Additional index options
        """
        try:
            await self.db[collection].create_index(keys, **kwargs)
        except Exception as e:
            logger.error(f"Error creating index: {e}")
    
    # Transaction support
    async def start_transaction(self):
        """Start a new transaction session."""
        return await self.client.start_session()
    
    async def commit_transaction(self, session):
        """Commit a transaction."""
        await session.commit_transaction()
        session.end_session()
    
    async def abort_transaction(self, session):
        """Abort a transaction."""
        await session.abort_transaction()
        session.end_session()


async def get_async_db() -> AsyncMongoDB:
    """
    Get or create the global async database instance.
    
    Returns:
        AsyncMongoDB instance
    """
    global _async_db_instance
    
    if _async_db_instance is None:
        _async_db_instance = AsyncMongoDB()
        await _async_db_instance.initialize()
    
    return _async_db_instance


def create_async_db(database_name: str = None) -> AsyncMongoDB:
    """
    Create a new async database instance.
    
    Args:
        database_name: Optional database name
        
    Returns:
        New AsyncMongoDB instance
    """
    return AsyncMongoDB(database_name)