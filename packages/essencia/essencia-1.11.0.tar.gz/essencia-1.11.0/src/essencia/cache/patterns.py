"""
Common caching patterns for Essencia applications.
"""
from typing import Any, Optional, List, Dict, Set, Callable
from datetime import datetime, timedelta
import asyncio
from contextlib import asynccontextmanager

from essencia.cache import AsyncCache
from .strategies import (
    StandardCacheStrategy,
    MultiLayerCacheStrategy,
    TaggedCacheStrategy,
    RefreshAheadCacheStrategy
)


class CacheAside:
    """Cache-aside (lazy loading) pattern."""
    
    def __init__(self, cache: AsyncCache, loader: Callable, ttl: int = 3600):
        self.cache = cache
        self.loader = loader
        self.ttl = ttl
        self.locks: Dict[str, asyncio.Lock] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value with cache-aside pattern."""
        # Try cache first
        value = await self.cache.get(key)
        if value is not None:
            return value
        
        # Prevent cache stampede with lock
        if key not in self.locks:
            self.locks[key] = asyncio.Lock()
        
        async with self.locks[key]:
            # Double-check after acquiring lock
            value = await self.cache.get(key)
            if value is not None:
                return value
            
            # Load from source
            value = await self.loader(key)
            if value is not None:
                await self.cache.set(key, value, self.ttl)
            
            return value
    
    async def invalidate(self, key: str):
        """Invalidate cache entry."""
        await self.cache.delete(key)


class CachePrefetch:
    """Prefetch pattern for predictive caching."""
    
    def __init__(
        self,
        cache: AsyncCache,
        predictor: Callable[[str], List[str]],
        loader: Callable
    ):
        self.cache = cache
        self.predictor = predictor
        self.loader = loader
        self.prefetch_tasks: Dict[str, asyncio.Task] = {}
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value and prefetch related items."""
        # Get requested value
        value = await self.cache.get(key)
        if value is None:
            value = await self.loader(key)
            if value is not None:
                await self.cache.set(key, value)
        
        # Predict and prefetch related items
        predicted_keys = await self.predictor(key)
        for pred_key in predicted_keys:
            if pred_key not in self.prefetch_tasks or self.prefetch_tasks[pred_key].done():
                self.prefetch_tasks[pred_key] = asyncio.create_task(
                    self._prefetch(pred_key)
                )
        
        return value
    
    async def _prefetch(self, key: str):
        """Prefetch item in background."""
        try:
            # Check if already cached
            if await self.cache.exists(key):
                return
            
            # Load and cache
            value = await self.loader(key)
            if value is not None:
                await self.cache.set(key, value)
        except Exception as e:
            print(f"Prefetch error for {key}: {e}")


class SessionCache:
    """Session-based caching pattern."""
    
    def __init__(self, cache: AsyncCache, session_ttl: int = 1800):
        self.cache = cache
        self.session_ttl = session_ttl
    
    async def get_session_value(
        self,
        session_id: str,
        key: str
    ) -> Optional[Any]:
        """Get value from session cache."""
        session_key = f"session:{session_id}:{key}"
        return await self.cache.get(session_key)
    
    async def set_session_value(
        self,
        session_id: str,
        key: str,
        value: Any
    ):
        """Set value in session cache."""
        session_key = f"session:{session_id}:{key}"
        await self.cache.set(session_key, value, self.session_ttl)
        
        # Track session keys for cleanup
        session_keys_key = f"session:{session_id}:keys"
        keys = await self.cache.get(session_keys_key) or []
        if key not in keys:
            keys.append(key)
            await self.cache.set(session_keys_key, keys, self.session_ttl)
    
    async def clear_session(self, session_id: str):
        """Clear all session cache entries."""
        # Get all session keys
        session_keys_key = f"session:{session_id}:keys"
        keys = await self.cache.get(session_keys_key) or []
        
        # Delete all session values
        for key in keys:
            session_key = f"session:{session_id}:{key}"
            await self.cache.delete(session_key)
        
        # Delete keys list
        await self.cache.delete(session_keys_key)


class QueryCache:
    """Database query result caching."""
    
    def __init__(
        self,
        cache: AsyncCache,
        namespace: str = "query",
        ttl: int = 300
    ):
        self.strategy = TaggedCacheStrategy(cache, namespace)
        self.ttl = ttl
    
    async def get_query_result(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """Get cached query result."""
        key = self._make_query_key(query, params)
        return await self.strategy.get(key)
    
    async def cache_query_result(
        self,
        query: str,
        params: Optional[Dict[str, Any]],
        result: Any,
        tags: Optional[List[str]] = None
    ):
        """Cache query result with tags."""
        key = self._make_query_key(query, params)
        await self.strategy.set(key, result, self.ttl, tags)
    
    async def invalidate_by_table(self, table_name: str):
        """Invalidate all queries for a table."""
        await self.strategy.invalidate_tag(f"table:{table_name}")
    
    def _make_query_key(self, query: str, params: Optional[Dict[str, Any]]) -> str:
        """Generate cache key for query."""
        import hashlib
        import json
        
        key_data = {
            "query": query,
            "params": params or {}
        }
        key_json = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_json.encode()).hexdigest()


class ComputedCache:
    """Cache for expensive computations."""
    
    def __init__(
        self,
        cache: AsyncCache,
        compute_func: Callable,
        ttl: int = 3600,
        refresh_ahead: bool = True
    ):
        if refresh_ahead:
            self.strategy = RefreshAheadCacheStrategy(
                cache,
                namespace="computed",
                loader_func=compute_func
            )
        else:
            self.strategy = StandardCacheStrategy(
                cache,
                namespace="computed",
                default_ttl=ttl
            )
        self.compute_func = compute_func
        self.ttl = ttl
    
    async def get_computed(self, key: str, *args, **kwargs) -> Any:
        """Get computed value from cache or compute it."""
        value = await self.strategy.get(key)
        if value is not None:
            return value
        
        # Compute value
        value = await self.compute_func(key, *args, **kwargs)
        if value is not None:
            await self.strategy.set(key, value, self.ttl)
        
        return value
    
    async def invalidate_computed(self, key: str):
        """Invalidate computed value."""
        await self.strategy.invalidate(key)


class CircuitBreakerCache:
    """Cache with circuit breaker pattern for resilience."""
    
    def __init__(
        self,
        cache: AsyncCache,
        fallback_cache: AsyncCache,
        failure_threshold: int = 5,
        recovery_timeout: int = 60
    ):
        self.primary_cache = cache
        self.fallback_cache = fallback_cache
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.circuit_open = False
        self.last_failure_time: Optional[datetime] = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value with circuit breaker protection."""
        # Check if circuit should be reset
        if self.circuit_open and self.last_failure_time:
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.circuit_open = False
                self.failure_count = 0
        
        # Use fallback if circuit is open
        if self.circuit_open:
            return await self.fallback_cache.get(key)
        
        try:
            # Try primary cache
            value = await self.primary_cache.get(key)
            
            # Reset failure count on success
            if self.failure_count > 0:
                self.failure_count = 0
            
            return value
            
        except Exception as e:
            # Increment failure count
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            # Open circuit if threshold reached
            if self.failure_count >= self.failure_threshold:
                self.circuit_open = True
                print(f"Circuit breaker opened: {e}")
            
            # Try fallback
            return await self.fallback_cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in both caches."""
        # Always set in fallback
        await self.fallback_cache.set(key, value, ttl)
        
        # Try primary if circuit is closed
        if not self.circuit_open:
            try:
                await self.primary_cache.set(key, value, ttl)
            except Exception:
                pass


class GeoDistributedCache:
    """Cache pattern for geo-distributed applications."""
    
    def __init__(
        self,
        local_cache: AsyncCache,
        remote_caches: Dict[str, AsyncCache],
        region: str
    ):
        self.local_cache = local_cache
        self.remote_caches = remote_caches
        self.region = region
    
    async def get(self, key: str, regions: Optional[List[str]] = None) -> Optional[Any]:
        """Get value from local or remote cache."""
        # Try local cache first
        value = await self.local_cache.get(key)
        if value is not None:
            return value
        
        # Try remote caches
        if regions:
            for region in regions:
                if region != self.region and region in self.remote_caches:
                    try:
                        value = await self.remote_caches[region].get(key)
                        if value is not None:
                            # Cache locally
                            await self.local_cache.set(key, value)
                            return value
                    except Exception:
                        continue
        
        return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        replicate_to: Optional[List[str]] = None
    ):
        """Set value in local and optionally replicate."""
        # Set locally
        await self.local_cache.set(key, value, ttl)
        
        # Replicate to other regions
        if replicate_to:
            tasks = []
            for region in replicate_to:
                if region != self.region and region in self.remote_caches:
                    task = asyncio.create_task(
                        self.remote_caches[region].set(key, value, ttl)
                    )
                    tasks.append(task)
            
            # Wait for replication (with timeout)
            if tasks:
                await asyncio.wait(tasks, timeout=5.0)


# Context managers for cache operations
@asynccontextmanager
async def cache_transaction(cache: AsyncCache, keys: List[str]):
    """Transaction-like cache operations."""
    # Store original values
    original_values = {}
    for key in keys:
        original_values[key] = await cache.get(key)
    
    try:
        yield cache
    except Exception:
        # Rollback on error
        for key, value in original_values.items():
            if value is not None:
                await cache.set(key, value)
            else:
                await cache.delete(key)
        raise


@asynccontextmanager
async def cache_lock(cache: AsyncCache, key: str, timeout: int = 30):
    """Distributed lock using cache."""
    lock_key = f"lock:{key}"
    lock_value = str(datetime.now().timestamp())
    acquired = False
    
    try:
        # Try to acquire lock
        acquired = await cache.set_if_not_exists(lock_key, lock_value, timeout)
        if not acquired:
            raise Exception(f"Could not acquire lock for {key}")
        
        yield
        
    finally:
        # Release lock if we acquired it
        if acquired:
            # Verify we still own the lock before deleting
            current_value = await cache.get(lock_key)
            if current_value == lock_value:
                await cache.delete(lock_key)