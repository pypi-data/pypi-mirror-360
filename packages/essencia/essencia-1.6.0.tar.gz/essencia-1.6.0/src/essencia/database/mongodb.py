"""MongoDB connection and operations."""

from typing import Any, Dict, List, Optional

import motor.motor_asyncio
from pymongo.errors import ConnectionFailure

from essencia.core.exceptions import DatabaseConnectionError


class MongoDB:
    """MongoDB connection manager."""
    
    def __init__(self, connection_url: str, database_name: str):
        """Initialize MongoDB connection.
        
        Args:
            connection_url: MongoDB connection URL
            database_name: Database name to use
        """
        self.client = motor.motor_asyncio.AsyncIOMotorClient(connection_url)
        self.database = self.client[database_name]
        
    async def health_check(self) -> bool:
        """Check if MongoDB is accessible.
        
        Returns:
            True if connection is healthy
        """
        try:
            await self.client.admin.command('ping')
            return True
        except ConnectionFailure:
            return False
            
    async def find_one(self, collection: str, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document.
        
        Args:
            collection: Collection name
            filter_dict: Filter criteria
            
        Returns:
            Document if found, None otherwise
        """
        return await self.database[collection].find_one(filter_dict)
        
    async def find_many(
        self, 
        collection: str, 
        filter_dict: Dict[str, Any], 
        limit: int = 0,
        skip: int = 0,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """Find multiple documents.
        
        Args:
            collection: Collection name
            filter_dict: Filter criteria
            limit: Maximum number of documents to return
            skip: Number of documents to skip
            sort: Sort criteria
            
        Returns:
            List of documents
        """
        cursor = self.database[collection].find(filter_dict)
        
        if skip > 0:
            cursor.skip(skip)
            
        if limit > 0:
            cursor.limit(limit)
            
        if sort:
            cursor.sort(sort)
            
        return await cursor.to_list(length=None)
        
    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a single document.
        
        Args:
            collection: Collection name
            document: Document to insert
            
        Returns:
            Inserted document ID
        """
        result = await self.database[collection].insert_one(document)
        return str(result.inserted_id)
        
    async def insert_many(self, collection: str, documents: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple documents.
        
        Args:
            collection: Collection name
            documents: Documents to insert
            
        Returns:
            List of inserted document IDs
        """
        result = await self.database[collection].insert_many(documents)
        return [str(id) for id in result.inserted_ids]
        
    async def update_one(self, collection: str, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> int:
        """Update a single document.
        
        Args:
            collection: Collection name
            filter_dict: Filter criteria
            update_dict: Update operations
            
        Returns:
            Number of modified documents
        """
        result = await self.database[collection].update_one(filter_dict, {"$set": update_dict})
        return result.modified_count
        
    async def update_many(self, collection: str, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> int:
        """Update multiple documents.
        
        Args:
            collection: Collection name
            filter_dict: Filter criteria
            update_dict: Update operations
            
        Returns:
            Number of modified documents
        """
        result = await self.database[collection].update_many(filter_dict, {"$set": update_dict})
        return result.modified_count
        
    async def delete_one(self, collection: str, filter_dict: Dict[str, Any]) -> int:
        """Delete a single document.
        
        Args:
            collection: Collection name
            filter_dict: Filter criteria
            
        Returns:
            Number of deleted documents
        """
        result = await self.database[collection].delete_one(filter_dict)
        return result.deleted_count
        
    async def delete_many(self, collection: str, filter_dict: Dict[str, Any]) -> int:
        """Delete multiple documents.
        
        Args:
            collection: Collection name
            filter_dict: Filter criteria
            
        Returns:
            Number of deleted documents
        """
        result = await self.database[collection].delete_many(filter_dict)
        return result.deleted_count
        
    async def count_documents(self, collection: str, filter_dict: Dict[str, Any]) -> int:
        """Count documents matching filter.
        
        Args:
            collection: Collection name
            filter_dict: Filter criteria
            
        Returns:
            Document count
        """
        return await self.database[collection].count_documents(filter_dict)
        
    def close(self):
        """Close MongoDB connection."""
        self.client.close()