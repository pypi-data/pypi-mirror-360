"""Redis connection and operations."""

import json
from typing import Any, Dict, List, Optional, Union

import redis.asyncio as redis
from redis.exceptions import ConnectionError

from essencia.core.exceptions import DatabaseConnectionError


class RedisClient:
    """Redis connection manager."""
    
    def __init__(self, connection_url: str, db: int = 0):
        """Initialize Redis connection.
        
        Args:
            connection_url: Redis connection URL
            db: Database number
        """
        self.client = redis.from_url(connection_url, db=db, decode_responses=True)
        
    async def health_check(self) -> bool:
        """Check if Redis is accessible.
        
        Returns:
            True if connection is healthy
        """
        try:
            await self.client.ping()
            return True
        except ConnectionError:
            return False
            
    async def get(self, key: str) -> Optional[str]:
        """Get value by key.
        
        Args:
            key: Key to retrieve
            
        Returns:
            Value if exists, None otherwise
        """
        return await self.client.get(key)
        
    async def set(self, key: str, value: Union[str, int, float], ttl: Optional[int] = None) -> bool:
        """Set key-value pair.
        
        Args:
            key: Key to set
            value: Value to store
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        return await self.client.set(key, value, ex=ttl)
        
    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get JSON value by key.
        
        Args:
            key: Key to retrieve
            
        Returns:
            Parsed JSON if exists, None otherwise
        """
        value = await self.get(key)
        if value:
            return json.loads(value)
        return None
        
    async def set_json(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set JSON value.
        
        Args:
            key: Key to set
            value: Dictionary to store as JSON
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        return await self.set(key, json.dumps(value), ttl)
        
    async def delete(self, key: str) -> int:
        """Delete key.
        
        Args:
            key: Key to delete
            
        Returns:
            Number of keys deleted
        """
        return await self.client.delete(key)
        
    async def exists(self, key: str) -> bool:
        """Check if key exists.
        
        Args:
            key: Key to check
            
        Returns:
            True if key exists
        """
        return await self.client.exists(key) == 1
        
    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on key.
        
        Args:
            key: Key to expire
            ttl: Time to live in seconds
            
        Returns:
            True if expiration was set
        """
        return await self.client.expire(key, ttl)
        
    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern.
        
        Args:
            pattern: Pattern to match
            
        Returns:
            List of matching keys
        """
        return await self.client.keys(pattern)
        
    async def hget(self, name: str, key: str) -> Optional[str]:
        """Get hash field value.
        
        Args:
            name: Hash name
            key: Field key
            
        Returns:
            Field value if exists
        """
        return await self.client.hget(name, key)
        
    async def hset(self, name: str, key: str, value: Union[str, int, float]) -> int:
        """Set hash field value.
        
        Args:
            name: Hash name
            key: Field key
            value: Field value
            
        Returns:
            Number of fields added
        """
        return await self.client.hset(name, key, value)
        
    async def hgetall(self, name: str) -> Dict[str, str]:
        """Get all hash fields.
        
        Args:
            name: Hash name
            
        Returns:
            Dictionary of all fields
        """
        return await self.client.hgetall(name)
        
    async def hdel(self, name: str, *keys: str) -> int:
        """Delete hash fields.
        
        Args:
            name: Hash name
            keys: Field keys to delete
            
        Returns:
            Number of fields deleted
        """
        return await self.client.hdel(name, *keys)
        
    async def close(self):
        """Close Redis connection."""
        await self.client.close()