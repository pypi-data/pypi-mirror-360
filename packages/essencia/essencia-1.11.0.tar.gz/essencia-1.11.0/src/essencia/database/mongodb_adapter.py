"""MongoDB adapter implementing the abstract database interface."""
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from bson import ObjectId

from .abstract import AbstractDatabase, SyncAbstractDatabase, DatabaseConfig, QueryBuilder


logger = logging.getLogger(__name__)


class MongoQueryBuilder(QueryBuilder):
    """MongoDB-specific query builder."""
    
    def __init__(self):
        self.filter = {}
        self.options = {}
    
    def where(self, **kwargs) -> 'MongoQueryBuilder':
        """Add WHERE conditions (MongoDB filter)."""
        self.filter.update(kwargs)
        return self
    
    def order_by(self, field: str, desc: bool = False) -> 'MongoQueryBuilder':
        """Add ORDER BY clause (MongoDB sort)."""
        if 'sort' not in self.options:
            self.options['sort'] = []
        self.options['sort'].append((field, -1 if desc else 1))
        return self
    
    def limit(self, n: int) -> 'MongoQueryBuilder':
        """Add LIMIT clause."""
        self.options['limit'] = n
        return self
    
    def offset(self, n: int) -> 'MongoQueryBuilder':
        """Add OFFSET clause (MongoDB skip)."""
        self.options['skip'] = n
        return self
    
    def build(self) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """Build the final query object."""
        return self.filter, self.options


class MongoDBAdapter(AbstractDatabase):
    """Async MongoDB adapter."""
    
    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self) -> None:
        """Establish MongoDB connection."""
        try:
            self.client = AsyncIOMotorClient(
                self.config.url,
                serverSelectionTimeoutMS=5000,
                **self.config.options
            )
            self.database = self.client[self.config.database_name]
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB: {self.config.database_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def is_connected(self) -> bool:
        """Check if MongoDB is connected."""
        if not self.client:
            return False
        try:
            await self.client.admin.command('ping')
            return True
        except:
            return False
    
    async def execute(self, query: Any, **kwargs) -> Any:
        """Execute a raw MongoDB command."""
        if not self.database:
            raise RuntimeError("Database not connected")
        return await self.database.command(query, **kwargs)
    
    def _convert_id(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB _id to string id."""
        if doc and '_id' in doc:
            doc['id'] = str(doc['_id'])
            del doc['_id']
        return doc
    
    def _prepare_filter(self, filter: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare filter for MongoDB, converting id to _id."""
        if 'id' in filter:
            filter = filter.copy()
            try:
                filter['_id'] = ObjectId(filter.pop('id'))
            except:
                filter['_id'] = filter.pop('id')
        return filter
    
    async def find_one(self, collection: str, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        filter = self._prepare_filter(filter)
        doc = await self.database[collection].find_one(filter)
        return self._convert_id(doc) if doc else None
    
    async def find_many(self, collection: str, filter: Dict[str, Any], 
                       limit: Optional[int] = None, skip: Optional[int] = None,
                       sort: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
        """Find multiple documents."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        filter = self._prepare_filter(filter)
        cursor = self.database[collection].find(filter)
        
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        
        docs = []
        async for doc in cursor:
            docs.append(self._convert_id(doc))
        return docs
    
    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a single document and return its ID."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        # Remove 'id' field if present
        document = document.copy()
        document.pop('id', None)
        
        result = await self.database[collection].insert_one(document)
        return str(result.inserted_id)
    
    async def insert_many(self, collection: str, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents and return their IDs."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        # Remove 'id' fields
        docs = []
        for doc in documents:
            doc_copy = doc.copy()
            doc_copy.pop('id', None)
            docs.append(doc_copy)
        
        result = await self.database[collection].insert_many(docs)
        return [str(id) for id in result.inserted_ids]
    
    async def update_one(self, collection: str, filter: Dict[str, Any], 
                        update: Dict[str, Any]) -> int:
        """Update a single document and return affected count."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        filter = self._prepare_filter(filter)
        
        # Ensure update has MongoDB update operators
        if not any(key.startswith('$') for key in update.keys()):
            update = {"$set": update}
        
        result = await self.database[collection].update_one(filter, update)
        return result.modified_count
    
    async def update_many(self, collection: str, filter: Dict[str, Any], 
                         update: Dict[str, Any]) -> int:
        """Update multiple documents and return affected count."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        filter = self._prepare_filter(filter)
        
        # Ensure update has MongoDB update operators
        if not any(key.startswith('$') for key in update.keys()):
            update = {"$set": update}
        
        result = await self.database[collection].update_many(filter, update)
        return result.modified_count
    
    async def delete_one(self, collection: str, filter: Dict[str, Any]) -> int:
        """Delete a single document and return affected count."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        filter = self._prepare_filter(filter)
        result = await self.database[collection].delete_one(filter)
        return result.deleted_count
    
    async def delete_many(self, collection: str, filter: Dict[str, Any]) -> int:
        """Delete multiple documents and return affected count."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        filter = self._prepare_filter(filter)
        result = await self.database[collection].delete_many(filter)
        return result.deleted_count
    
    async def count(self, collection: str, filter: Dict[str, Any]) -> int:
        """Count documents matching filter."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        filter = self._prepare_filter(filter)
        return await self.database[collection].count_documents(filter)
    
    async def create_index(self, collection: str, keys: List[tuple], unique: bool = False) -> None:
        """Create an index on the collection."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        await self.database[collection].create_index(keys, unique=unique)
    
    def get_query_builder(self) -> QueryBuilder:
        """Get a MongoDB query builder."""
        return MongoQueryBuilder()


class SyncMongoDBAdapter(SyncAbstractDatabase):
    """Synchronous MongoDB adapter."""
    
    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        self.client: Optional[MongoClient] = None
        self.database: Optional[Any] = None
    
    def connect(self) -> None:
        """Establish MongoDB connection."""
        try:
            self.client = MongoClient(
                self.config.url,
                serverSelectionTimeoutMS=5000,
                **self.config.options
            )
            self.database = self.client[self.config.database_name]
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB (sync): {self.config.database_name}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB (sync)")
    
    def is_connected(self) -> bool:
        """Check if MongoDB is connected."""
        if not self.client:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except:
            return False
    
    def execute(self, query: Any, **kwargs) -> Any:
        """Execute a raw MongoDB command."""
        if not self.database:
            raise RuntimeError("Database not connected")
        return self.database.command(query, **kwargs)
    
    def _convert_id(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB _id to string id."""
        if doc and '_id' in doc:
            doc['id'] = str(doc['_id'])
            del doc['_id']
        return doc
    
    def _prepare_filter(self, filter: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare filter for MongoDB, converting id to _id."""
        if 'id' in filter:
            filter = filter.copy()
            try:
                filter['_id'] = ObjectId(filter.pop('id'))
            except:
                filter['_id'] = filter.pop('id')
        return filter
    
    def find_one(self, collection: str, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        filter = self._prepare_filter(filter)
        doc = self.database[collection].find_one(filter)
        return self._convert_id(doc) if doc else None
    
    def find_many(self, collection: str, filter: Dict[str, Any], 
                  limit: Optional[int] = None, skip: Optional[int] = None,
                  sort: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
        """Find multiple documents."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        filter = self._prepare_filter(filter)
        cursor = self.database[collection].find(filter)
        
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        if sort:
            cursor = cursor.sort(sort)
        
        return [self._convert_id(doc) for doc in cursor]
    
    def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a single document and return its ID."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        # Remove 'id' field if present
        document = document.copy()
        document.pop('id', None)
        
        result = self.database[collection].insert_one(document)
        return str(result.inserted_id)
    
    def update_one(self, collection: str, filter: Dict[str, Any], 
                   update: Dict[str, Any]) -> int:
        """Update a single document and return affected count."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        filter = self._prepare_filter(filter)
        
        # Ensure update has MongoDB update operators
        if not any(key.startswith('$') for key in update.keys()):
            update = {"$set": update}
        
        result = self.database[collection].update_one(filter, update)
        return result.modified_count
    
    def delete_one(self, collection: str, filter: Dict[str, Any]) -> int:
        """Delete a single document and return affected count."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        filter = self._prepare_filter(filter)
        result = self.database[collection].delete_one(filter)
        return result.deleted_count
    
    def count(self, collection: str, filter: Dict[str, Any]) -> int:
        """Count documents matching filter."""
        if not self.database:
            raise RuntimeError("Database not connected")
        
        filter = self._prepare_filter(filter)
        return self.database[collection].count_documents(filter)