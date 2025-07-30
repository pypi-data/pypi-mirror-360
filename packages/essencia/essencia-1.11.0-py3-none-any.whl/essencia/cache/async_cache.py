"""
Async caching system for improved performance.
Supports both Redis and in-memory caching with automatic fallback.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Optional
import asyncio

logger = logging.getLogger(__name__)

# Temporarily disabled for PyInstaller compatibility
# try:
#     import aioredis
#     AIOREDIS_AVAILABLE = True
# except ImportError:
AIOREDIS_AVAILABLE = False
logger.warning("aioredis disabled for PyInstaller compatibility, using in-memory cache")


class AsyncCacheManager:
    """Async Redis-based caching with fallback to in-memory"""
    
    def __init__(self):
        self.use_redis = False
        self.redis_client = None
        self.memory_cache = {}
        self.cache_timestamps = {}
        self._lock = asyncio.Lock()
        self._initialized = False
    
    async def initialize(self, redis_url: Optional[str] = None):
        """Initialize the cache connection."""
        if self._initialized:
            return
            
        async with self._lock:
            if self._initialized:
                return
                
            if AIOREDIS_AVAILABLE and redis_url:
                try:
                    # Connect to Redis
                    self.redis_client = await aioredis.from_url(
                        redis_url,
                        encoding="utf-8",
                        decode_responses=True,
                        socket_keepalive=True,
                        socket_connect_timeout=5
                    )
                    
                    # Test connection
                    await self.redis_client.ping()
                    self.use_redis = True
                    logger.info("Async Redis cache connected")
                except Exception as e:
                    logger.warning(f"Async Redis connection failed: {e}, using in-memory cache")
                    self.redis_client = None
            else:
                logger.info("Using in-memory cache")
            
            self._initialized = True
    
    def _make_key(self, key: str) -> str:
        """Create a namespaced cache key"""
        return f"essencia:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache asynchronously"""
        await self.initialize()
        
        full_key = self._make_key(key)
        
        if self.use_redis and self.redis_client:
            try:
                value = await self.redis_client.get(full_key)
                return json.loads(value) if value else None
            except Exception as e:
                logger.error(f"Redis get error: {e}")
                return None
        else:
            # Check in-memory cache
            async with self._lock:
                if full_key in self.memory_cache:
                    timestamp = self.cache_timestamps.get(full_key)
                    if timestamp and datetime.now() < timestamp:
                        return self.memory_cache[full_key]
                    else:
                        # Expired, remove it
                        self.memory_cache.pop(full_key, None)
                        self.cache_timestamps.pop(full_key, None)
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache asynchronously with TTL in seconds"""
        await self.initialize()
        
        full_key = self._make_key(key)
        
        if self.use_redis and self.redis_client:
            try:
                serialized = json.dumps(value, default=str)
                await self.redis_client.setex(full_key, ttl, serialized)
                return True
            except Exception as e:
                logger.error(f"Redis set error: {e}")
                return False
        else:
            # Use in-memory cache
            async with self._lock:
                self.memory_cache[full_key] = value
                self.cache_timestamps[full_key] = datetime.now() + timedelta(seconds=ttl)
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete a specific key from cache asynchronously"""
        await self.initialize()
        
        full_key = self._make_key(key)
        
        if self.use_redis and self.redis_client:
            try:
                result = await self.redis_client.delete(full_key)
                return bool(result)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
                return False
        else:
            async with self._lock:
                self.memory_cache.pop(full_key, None)
                self.cache_timestamps.pop(full_key, None)
            return True
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache keys matching pattern asynchronously"""
        await self.initialize()
        
        count = 0
        
        if self.use_redis and self.redis_client:
            try:
                full_pattern = self._make_key(pattern)
                # Use SCAN to find matching keys
                cursor = b'0'
                while cursor:
                    cursor, keys = await self.redis_client.scan(
                        cursor=cursor,
                        match=full_pattern,
                        count=100
                    )
                    if keys:
                        await self.redis_client.delete(*keys)
                        count += len(keys)
            except Exception as e:
                logger.error(f"Redis pattern delete error: {e}")
        else:
            # Simple pattern matching for in-memory cache
            async with self._lock:
                keys_to_delete = [
                    k for k in self.memory_cache.keys() 
                    if pattern.replace('*', '') in k
                ]
                for key in keys_to_delete:
                    self.memory_cache.pop(key, None)
                    self.cache_timestamps.pop(key, None)
                    count += 1
        
        return count
    
    async def clear_expired(self):
        """Clear expired entries from memory cache"""
        if not self.use_redis:
            async with self._lock:
                now = datetime.now()
                expired_keys = [
                    k for k, timestamp in self.cache_timestamps.items()
                    if timestamp < now
                ]
                for key in expired_keys:
                    self.memory_cache.pop(key, None)
                    self.cache_timestamps.pop(key, None)
                
                if expired_keys:
                    logger.debug(f"Cleared {len(expired_keys)} expired cache entries")
    
    async def close(self):
        """Close the cache connection"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            self.use_redis = False
            self._initialized = False
            logger.info("Async cache connection closed")


# Global async cache instance
async_cache = AsyncCacheManager()


# Decorator for async caching
def async_cache_result(ttl_seconds: int = 300, key_prefix: str = None):
    """
    Decorator to cache async function results.
    
    Args:
        ttl_seconds: Time to live in seconds
        key_prefix: Optional prefix for cache key
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_parts = [key_prefix or func.__name__]
            
            # Add string representation of arguments
            for arg in args:
                if hasattr(arg, '__name__'):  # Skip class/function objects
                    cache_key_parts.append(arg.__name__)
                elif hasattr(arg, 'key'):  # MongoDB models
                    cache_key_parts.append(arg.key)
                else:
                    cache_key_parts.append(str(arg))
            
            # Add kwargs
            for k, v in sorted(kwargs.items()):
                cache_key_parts.append(f"{k}={v}")
            
            cache_key = ":".join(cache_key_parts)
            
            # Try to get from cache
            cached_value = await async_cache.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_value
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await async_cache.set(cache_key, result, ttl_seconds)
            logger.debug(f"Cached result for {cache_key}")
            
            return result
        
        # Add method to invalidate this function's cache
        wrapper.invalidate_cache = lambda: asyncio.create_task(
            async_cache.invalidate_pattern(f"{key_prefix or func.__name__}:*")
        )
        
        return wrapper
    return decorator


async def invalidate_model_cache(model_name: str, key: str = None):
    """
    Invalidate cache for a specific model asynchronously.
    
    Args:
        model_name: Name of the model (e.g., 'patient')
        key: Optional specific model key to invalidate
    """
    if key:
        pattern = f"{model_name}:{key}:*"
    else:
        pattern = f"{model_name}:*"
    
    count = await async_cache.invalidate_pattern(pattern)
    logger.info(f"Invalidated {count} cache entries for pattern {pattern}")