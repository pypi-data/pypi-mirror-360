"""
Async model mixins for MongoDB operations.

This module provides async capabilities for essencia models, enabling
high-performance database operations using Motor (async MongoDB driver).
"""

import logging
from typing import Optional, List, Dict, Any, Type, TypeVar
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

T = TypeVar('T', bound='AsyncModelMixin')


class AsyncModelMixin:
    """
    Mixin class to add async capabilities to MongoModel classes.
    
    This mixin provides async versions of all database operations,
    including find, save, update, delete, and aggregation operations.
    """
    
    @staticmethod
    async def _get_async_db():
        """Get async database instance."""
        from essencia.database.async_mongodb import get_async_db
        return await get_async_db()
    
    @staticmethod
    def _get_cache():
        """Get cache instance."""
        try:
            from essencia.cache import async_cache
            return async_cache
        except ImportError:
            # Return a dummy cache if not available
            class DummyCache:
                def get(self, key): return None
                def set(self, key, value, ttl=None): pass
                def delete(self, key): pass
            return DummyCache()
    
    @classmethod
    async def afind(cls: Type[T], query: dict) -> List[T]:
        """
        Execute async MongoDB find query.
        
        Args:
            query: MongoDB query dictionary
            
        Returns:
            List of model instances
        """
        try:
            db = await cls._get_async_db()
            docs = await db.find(cls.validate_collection_name(), query)
            results = []
            for doc in docs:
                instance = cls(**doc)
                if '_id' in doc:
                    setattr(instance, '_id', doc['_id'])
                results.append(instance)
            return results
        except Exception as e:
            logger.error(f"Error finding {cls.__name__} documents: {e}")
            return []
    
    @classmethod
    async def afind_one(cls: Type[T], query: dict) -> Optional[T]:
        """
        Execute async MongoDB find_one query.
        
        Args:
            query: MongoDB query dictionary
            
        Returns:
            Model instance or None
        """
        try:
            db = await cls._get_async_db()
            data = await db.find_one(cls.validate_collection_name(), query)
            if data:
                instance = cls(**data)
                if '_id' in data:
                    setattr(instance, '_id', data['_id'])
                return instance
            return None
        except Exception as e:
            logger.error(f"Error finding {cls.__name__} document: {e}")
            return None
    
    @classmethod
    async def afind_by_key(cls: Type[T], key: str) -> Optional[T]:
        """
        Find a document by its key asynchronously.
        
        Args:
            key: Document key
            
        Returns:
            Model instance or None
        """
        cache_key = f"{cls.__name__.lower()}:{key}"
        
        # Try cache first
        cache = cls._get_cache()
        cached = cache.get(cache_key)
        if cached:
            return cls(**cached)
        
        # Fetch from database
        result = await cls.afind_one({'key': key})
        
        # Cache the result
        if result:
            cache.set(cache_key, result.model_dump(mode='json'), ttl=300)
        
        return result
    
    async def asave(self: T) -> T:
        """
        Save the current instance asynchronously.
        
        Returns:
            Updated model instance
        """
        try:
            db = await self._get_async_db()
            data = self.model_dump(by_alias=True, mode='json')
            
            # Remove _id if it's None
            if '_id' in data and data['_id'] is None:
                del data['_id']
            
            # Add timestamps
            if not hasattr(self, '_id') or self._id is None:
                data['created_at'] = datetime.utcnow()
            data['updated_at'] = datetime.utcnow()
            
            result = await db.save_one(self.validate_collection_name(), data)
            
            if result:
                # Update instance with saved data
                for key, value in result.items():
                    if hasattr(self, key) and not hasattr(type(self), key):
                        # Only set if it's an instance attribute, not a property/computed field
                        setattr(self, key, value)
                    elif key == '_id':
                        # Always set _id
                        setattr(self, '_id', value)
                
                # Invalidate cache
                if hasattr(self, 'key'):
                    cache_key = f"{self.__class__.__name__.lower()}:{self.key}"
                    self._get_cache().delete(cache_key)
                
            return self
        except Exception as e:
            logger.error(f"Error saving {self.__class__.__name__}: {e}")
            raise
    
    async def aupdate(self: T, updates: dict) -> T:
        """
        Update the document asynchronously.
        
        Args:
            updates: MongoDB update operations
            
        Returns:
            Updated model instance
        """
        try:
            db = await self._get_async_db()
            
            # Ensure we have an ID
            if not hasattr(self, '_id') or self._id is None:
                raise ValueError("Cannot update document without _id")
            
            success = await db.update_one(
                self.validate_collection_name(),
                {'_id': self._id},
                updates
            )
            
            if success:
                # Reload the document
                updated = await self.afind_one({'_id': self._id})
                if updated:
                    # Update instance attributes
                    for key, value in updated.model_dump().items():
                        if hasattr(self, key) and not hasattr(type(self), key):
                            # Only set if it's an instance attribute, not a property/computed field
                            setattr(self, key, value)
                
                # Invalidate cache
                if hasattr(self, 'key'):
                    cache_key = f"{self.__class__.__name__.lower()}:{self.key}"
                    self._get_cache().delete(cache_key)
            
            return self
        except Exception as e:
            logger.error(f"Error updating {self.__class__.__name__}: {e}")
            raise
    
    async def adelete(self) -> bool:
        """
        Delete the document asynchronously.
        
        Returns:
            True if successful
        """
        try:
            db = await self._get_async_db()
            
            # Ensure we have an ID
            if not hasattr(self, '_id') or self._id is None:
                raise ValueError("Cannot delete document without _id")
            
            success = await db.delete_one(
                self.validate_collection_name(),
                {'_id': self._id}
            )
            
            if success:
                # Invalidate cache
                if hasattr(self, 'key'):
                    cache_key = f"{self.__class__.__name__.lower()}:{self.key}"
                    self._get_cache().delete(cache_key)
            
            return success
        except Exception as e:
            logger.error(f"Error deleting {self.__class__.__name__}: {e}")
            raise
    
    @classmethod
    async def afind_paginated(cls: Type[T], query: dict, 
                            page: int = 1, page_size: int = 50,
                            sort: Optional[List[tuple]] = None) -> Dict[str, Any]:
        """
        Find documents with pagination asynchronously.
        
        Args:
            query: MongoDB query
            page: Page number (1-based)
            page_size: Items per page
            sort: Sort specification
            
        Returns:
            Paginated results dictionary
        """
        try:
            db = await cls._get_async_db()
            result = await db.find_paginated(
                cls.validate_collection_name(),
                query,
                page=page,
                page_size=page_size,
                sort=sort
            )
            
            # Convert documents to model instances
            instances = []
            for doc in result['results']:
                instance = cls(**doc)
                if '_id' in doc:
                    setattr(instance, '_id', doc['_id'])
                instances.append(instance)
            result['results'] = instances
            
            return result
        except Exception as e:
            logger.error(f"Error in paginated query for {cls.__name__}: {e}")
            return {
                'results': [],
                'page': page,
                'pages': 0,
                'total': 0,
                'has_next': False,
                'has_prev': False
            }
    
    @classmethod
    async def aaggregate(cls: Type[T], pipeline: list) -> List[dict]:
        """
        Execute aggregation pipeline asynchronously.
        
        Args:
            pipeline: MongoDB aggregation pipeline
            
        Returns:
            List of aggregation results
        """
        try:
            db = await cls._get_async_db()
            return await db.aggregate(cls.validate_collection_name(), pipeline)
        except Exception as e:
            logger.error(f"Error in aggregation for {cls.__name__}: {e}")
            return []
    
    @classmethod
    async def acount(cls: Type[T], query: dict = None) -> int:
        """
        Count documents asynchronously.
        
        Args:
            query: Optional query filter
            
        Returns:
            Document count
        """
        try:
            db = await cls._get_async_db()
            query = query or {}
            return await db.count(cls.validate_collection_name(), query)
        except Exception as e:
            logger.error(f"Error counting {cls.__name__} documents: {e}")
            return 0
    
    @classmethod
    async def abulk_create(cls: Type[T], documents: List[Dict[str, Any]]) -> List[T]:
        """
        Create multiple documents asynchronously.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            List of created model instances
        """
        try:
            db = await cls._get_async_db()
            
            # Add timestamps
            for doc in documents:
                doc['created_at'] = datetime.utcnow()
                doc['updated_at'] = datetime.utcnow()
            
            # Insert all documents
            result = await db.bulk_insert(cls.validate_collection_name(), documents)
            
            # Return created instances
            if result:
                return [cls(**doc) for doc in documents]
            
            return []
        except Exception as e:
            logger.error(f"Error in bulk create for {cls.__name__}: {e}")
            raise
    
    @classmethod
    async def abulk_update(cls: Type[T], updates: List[tuple]) -> int:
        """
        Update multiple documents asynchronously.
        
        Args:
            updates: List of (query, update) tuples
            
        Returns:
            Number of documents updated
        """
        try:
            db = await cls._get_async_db()
            
            # Execute updates concurrently
            tasks = []
            for query, update in updates:
                update.setdefault('$set', {})['updated_at'] = datetime.utcnow()
                task = db.update_many(cls.validate_collection_name(), query, update)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            return sum(results)
        except Exception as e:
            logger.error(f"Error in bulk update for {cls.__name__}: {e}")
            return 0


class AsyncTransactionContext:
    """
    Async context manager for MongoDB transactions.
    
    Usage:
        async with AsyncTransactionContext() as session:
            # Perform transactional operations
            await model.asave()
    """
    
    def __init__(self):
        self.session = None
        self.db = None
    
    async def __aenter__(self):
        """Start a transaction."""
        from essencia.database.async_mongodb import get_async_db
        self.db = await get_async_db()
        self.session = await self.db.start_transaction()
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Commit or rollback the transaction."""
        if exc_type:
            await self.db.abort_transaction(self.session)
        else:
            await self.db.commit_transaction(self.session)


# Decorator for async caching
def async_cache_result(ttl_seconds: int = 300, key_prefix: str = None):
    """
    Decorator to cache async function results.
    
    Args:
        ttl_seconds: Time to live in seconds
        key_prefix: Optional prefix for cache key
        
    Usage:
        @async_cache_result(ttl_seconds=600)
        async def get_expensive_data(user_id: str):
            # Expensive operation
            return data
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_parts = [key_prefix or func.__name__]
            
            for arg in args:
                if hasattr(arg, 'key'):
                    cache_key_parts.append(arg.key)
                else:
                    cache_key_parts.append(str(arg))
            
            for k, v in sorted(kwargs.items()):
                cache_key_parts.append(f"{k}={v}")
            
            cache_key = ":".join(cache_key_parts)
            
            # Try cache
            try:
                from essencia.cache import async_cache
                cached_value = async_cache.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Cache hit for {cache_key}")
                    return cached_value
            except ImportError:
                pass
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            try:
                from essencia.cache import async_cache
                async_cache.set(cache_key, result, ttl_seconds)
            except ImportError:
                pass
            
            return result
        
        return wrapper
    return decorator