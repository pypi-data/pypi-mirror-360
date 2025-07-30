"""
Advanced caching strategies for Essencia.
"""
from typing import Any, Optional, List, Dict, Callable, Union
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import hashlib
import json
import asyncio
from functools import wraps

from essencia.cache import AsyncCache, CacheConfig


class CacheStrategy(ABC):
    """Base class for cache strategies."""
    
    def __init__(self, cache: AsyncCache, namespace: str = ""):
        self.cache = cache
        self.namespace = namespace
    
    def make_key(self, key: str) -> str:
        """Create namespaced cache key."""
        if self.namespace:
            return f"{self.namespace}:{key}"
        return key
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache."""
        pass
    
    @abstractmethod
    async def invalidate(self, key: str):
        """Invalidate cache entry."""
        pass


class StandardCacheStrategy(CacheStrategy):
    """Standard cache strategy with TTL."""
    
    def __init__(self, cache: AsyncCache, namespace: str = "", default_ttl: int = 3600):
        super().__init__(cache, namespace)
        self.default_ttl = default_ttl
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return await self.cache.get(self.make_key(key))
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache."""
        ttl = ttl or self.default_ttl
        await self.cache.set(self.make_key(key), value, ttl)
    
    async def invalidate(self, key: str):
        """Invalidate cache entry."""
        await self.cache.delete(self.make_key(key))


class MultiLayerCacheStrategy(CacheStrategy):
    """Multi-layer cache with L1 (memory) and L2 (Redis) caching."""
    
    def __init__(
        self,
        cache: AsyncCache,
        namespace: str = "",
        l1_size: int = 1000,
        l1_ttl: int = 60,
        l2_ttl: int = 3600
    ):
        super().__init__(cache, namespace)
        self.l1_cache: Dict[str, tuple[Any, datetime]] = {}
        self.l1_size = l1_size
        self.l1_ttl = l1_ttl
        self.l2_ttl = l2_ttl
        self.access_count: Dict[str, int] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache (L1 first, then L2)."""
        cache_key = self.make_key(key)
        
        # Check L1 cache
        if cache_key in self.l1_cache:
            value, expiry = self.l1_cache[cache_key]
            if datetime.now() < expiry:
                self.access_count[cache_key] = self.access_count.get(cache_key, 0) + 1
                return value
            else:
                del self.l1_cache[cache_key]
        
        # Check L2 cache
        value = await self.cache.get(cache_key)
        if value is not None:
            # Promote to L1 if frequently accessed
            access_count = self.access_count.get(cache_key, 0)
            if access_count > 3:
                await self._promote_to_l1(cache_key, value)
        
        return value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in both cache layers."""
        cache_key = self.make_key(key)
        
        # Set in L2 (Redis)
        l2_ttl = ttl or self.l2_ttl
        await self.cache.set(cache_key, value, l2_ttl)
        
        # Set in L1 if space available
        if len(self.l1_cache) < self.l1_size:
            expiry = datetime.now() + timedelta(seconds=self.l1_ttl)
            self.l1_cache[cache_key] = (value, expiry)
    
    async def invalidate(self, key: str):
        """Invalidate cache entry in both layers."""
        cache_key = self.make_key(key)
        
        # Remove from L1
        if cache_key in self.l1_cache:
            del self.l1_cache[cache_key]
        
        # Remove from L2
        await self.cache.delete(cache_key)
        
        # Reset access count
        if cache_key in self.access_count:
            del self.access_count[cache_key]
    
    async def _promote_to_l1(self, key: str, value: Any):
        """Promote frequently accessed item to L1 cache."""
        # Evict least recently used if full
        if len(self.l1_cache) >= self.l1_size:
            # Simple LRU: remove oldest entry
            oldest_key = min(self.l1_cache.keys(), 
                           key=lambda k: self.l1_cache[k][1])
            del self.l1_cache[oldest_key]
        
        expiry = datetime.now() + timedelta(seconds=self.l1_ttl)
        self.l1_cache[key] = (value, expiry)


class TaggedCacheStrategy(CacheStrategy):
    """Cache strategy with tag-based invalidation."""
    
    def __init__(self, cache: AsyncCache, namespace: str = ""):
        super().__init__(cache, namespace)
        self.tag_prefix = f"{namespace}:tag:" if namespace else "tag:"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return await self.cache.get(self.make_key(key))
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None
    ):
        """Set value in cache with tags."""
        cache_key = self.make_key(key)
        
        # Set the value
        await self.cache.set(cache_key, value, ttl)
        
        # Store tags
        if tags:
            for tag in tags:
                tag_key = f"{self.tag_prefix}{tag}"
                tagged_keys = await self.cache.get(tag_key) or []
                if cache_key not in tagged_keys:
                    tagged_keys.append(cache_key)
                await self.cache.set(tag_key, tagged_keys, ttl)
    
    async def invalidate(self, key: str):
        """Invalidate cache entry."""
        await self.cache.delete(self.make_key(key))
    
    async def invalidate_tag(self, tag: str):
        """Invalidate all cache entries with a specific tag."""
        tag_key = f"{self.tag_prefix}{tag}"
        tagged_keys = await self.cache.get(tag_key) or []
        
        # Delete all tagged keys
        for key in tagged_keys:
            await self.cache.delete(key)
        
        # Delete the tag list
        await self.cache.delete(tag_key)


class DependencyCacheStrategy(CacheStrategy):
    """Cache strategy with dependency tracking."""
    
    def __init__(self, cache: AsyncCache, namespace: str = ""):
        super().__init__(cache, namespace)
        self.dep_prefix = f"{namespace}:dep:" if namespace else "dep:"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache if dependencies are valid."""
        cache_key = self.make_key(key)
        
        # Check if any dependencies have been invalidated
        dep_key = f"{self.dep_prefix}{cache_key}"
        dependencies = await self.cache.get(dep_key) or []
        
        for dep in dependencies:
            if not await self.cache.exists(dep):
                # Dependency invalidated, invalidate this key too
                await self.invalidate(key)
                return None
        
        return await self.cache.get(cache_key)
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        depends_on: Optional[List[str]] = None
    ):
        """Set value with dependencies."""
        cache_key = self.make_key(key)
        
        # Set the value
        await self.cache.set(cache_key, value, ttl)
        
        # Store dependencies
        if depends_on:
            dep_key = f"{self.dep_prefix}{cache_key}"
            await self.cache.set(dep_key, depends_on, ttl)
    
    async def invalidate(self, key: str):
        """Invalidate cache entry and its dependencies."""
        cache_key = self.make_key(key)
        
        # Delete the value
        await self.cache.delete(cache_key)
        
        # Delete dependency tracking
        dep_key = f"{self.dep_prefix}{cache_key}"
        await self.cache.delete(dep_key)


class WriteThoughCacheStrategy(CacheStrategy):
    """Write-through cache strategy."""
    
    def __init__(
        self,
        cache: AsyncCache,
        namespace: str = "",
        backend_get: Optional[Callable] = None,
        backend_set: Optional[Callable] = None
    ):
        super().__init__(cache, namespace)
        self.backend_get = backend_get
        self.backend_set = backend_set
    
    async def get(self, key: str) -> Optional[Any]:
        """Get from cache or backend."""
        cache_key = self.make_key(key)
        
        # Try cache first
        value = await self.cache.get(cache_key)
        if value is not None:
            return value
        
        # Get from backend if available
        if self.backend_get:
            value = await self.backend_get(key)
            if value is not None:
                # Cache the value
                await self.cache.set(cache_key, value)
        
        return value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Write to both cache and backend."""
        cache_key = self.make_key(key)
        
        # Write to cache
        await self.cache.set(cache_key, value, ttl)
        
        # Write to backend if available
        if self.backend_set:
            await self.backend_set(key, value)
    
    async def invalidate(self, key: str):
        """Invalidate cache entry."""
        await self.cache.delete(self.make_key(key))


class RefreshAheadCacheStrategy(CacheStrategy):
    """Refresh-ahead cache strategy for frequently accessed data."""
    
    def __init__(
        self,
        cache: AsyncCache,
        namespace: str = "",
        refresh_threshold: float = 0.8,
        loader_func: Optional[Callable] = None
    ):
        super().__init__(cache, namespace)
        self.refresh_threshold = refresh_threshold
        self.loader_func = loader_func
        self.refresh_tasks: Dict[str, asyncio.Task] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value and refresh if near expiry."""
        cache_key = self.make_key(key)
        
        # Get value and TTL
        value = await self.cache.get(cache_key)
        if value is None:
            # Load if loader function provided
            if self.loader_func:
                value = await self.loader_func(key)
                if value is not None:
                    await self.set(key, value)
            return value
        
        # Check if refresh needed
        ttl = await self.cache.ttl(cache_key)
        original_ttl = await self.cache.get(f"{cache_key}:original_ttl") or 3600
        
        if ttl > 0 and ttl < original_ttl * (1 - self.refresh_threshold):
            # Trigger async refresh if not already running
            if cache_key not in self.refresh_tasks or self.refresh_tasks[cache_key].done():
                self.refresh_tasks[cache_key] = asyncio.create_task(
                    self._refresh_value(key, original_ttl)
                )
        
        return value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value and store original TTL."""
        cache_key = self.make_key(key)
        ttl = ttl or 3600
        
        await self.cache.set(cache_key, value, ttl)
        await self.cache.set(f"{cache_key}:original_ttl", ttl, ttl)
    
    async def invalidate(self, key: str):
        """Invalidate cache entry."""
        cache_key = self.make_key(key)
        
        # Cancel refresh task if running
        if cache_key in self.refresh_tasks:
            self.refresh_tasks[cache_key].cancel()
            del self.refresh_tasks[cache_key]
        
        await self.cache.delete(cache_key)
        await self.cache.delete(f"{cache_key}:original_ttl")
    
    async def _refresh_value(self, key: str, ttl: int):
        """Refresh value in background."""
        if self.loader_func:
            try:
                new_value = await self.loader_func(key)
                if new_value is not None:
                    await self.set(key, new_value, ttl)
            except Exception as e:
                print(f"Error refreshing cache key {key}: {e}")


# Cache decorators
def cached(
    strategy: CacheStrategy,
    key_func: Optional[Callable] = None,
    ttl: Optional[int] = None
):
    """Decorator for caching function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                cache_key = ":".join(key_parts)
            
            # Try cache
            result = await strategy.get(cache_key)
            if result is not None:
                return result
            
            # Call function
            result = await func(*args, **kwargs)
            
            # Cache result
            await strategy.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, run in event loop
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(async_wrapper(*args, **kwargs))
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator


def cache_invalidate(strategy: CacheStrategy, key_pattern: str):
    """Decorator to invalidate cache after function execution."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            
            # Invalidate cache
            await strategy.invalidate(key_pattern.format(*args, **kwargs))
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalidate cache (run async in sync context)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(
                strategy.invalidate(key_pattern.format(*args, **kwargs))
            )
            
            return result
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    
    return decorator