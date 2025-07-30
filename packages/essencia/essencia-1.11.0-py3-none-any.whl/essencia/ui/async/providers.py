"""
Async data providers for UI components.

Provides abstract base classes and implementations for
asynchronous data loading patterns.
"""

import asyncio
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta

import flet as ft

T = TypeVar('T')


@dataclass
class PaginationMetadata:
    """Metadata for paginated results."""
    page: int
    page_size: int
    total: int
    pages: int
    has_next: bool
    has_prev: bool


@dataclass
class PaginatedResult(Generic[T]):
    """Container for paginated results."""
    results: List[T]
    metadata: PaginationMetadata


class AsyncDataProvider(ABC, Generic[T]):
    """
    Abstract base class for async data providers.
    
    Example:
        ```python
        class UserProvider(AsyncDataProvider[User]):
            async def load(self, **kwargs) -> List[User]:
                return await api.get_users(**kwargs)
                
            async def get(self, id: str) -> Optional[User]:
                return await api.get_user(id)
                
            async def save(self, item: User) -> User:
                if item.id:
                    return await api.update_user(item)
                else:
                    return await api.create_user(item)
        ```
    """
    
    def __init__(self, cache_enabled: bool = True, cache_ttl: int = 300):
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
    
    @abstractmethod
    async def load(self, **kwargs) -> List[T]:
        """Load multiple items."""
        pass
    
    @abstractmethod
    async def get(self, id: Any) -> Optional[T]:
        """Get single item by ID."""
        pass
    
    @abstractmethod
    async def save(self, item: T) -> T:
        """Save item (create or update)."""
        pass
    
    async def delete(self, id: Any) -> bool:
        """Delete item by ID."""
        raise NotImplementedError("Delete not implemented")
    
    async def refresh(self):
        """Clear cache and reload data."""
        self._cache.clear()
        self._cache_timestamps.clear()
    
    def _get_cache_key(self, method: str, **kwargs) -> str:
        """Generate cache key from method and kwargs."""
        import json
        params = json.dumps(kwargs, sort_keys=True)
        return f"{method}:{params}"
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cache entry is still valid."""
        if not self.cache_enabled or key not in self._cache_timestamps:
            return False
            
        age = datetime.now() - self._cache_timestamps[key]
        return age.total_seconds() < self.cache_ttl
    
    async def _cached_call(self, method: str, func: Callable, **kwargs) -> Any:
        """Execute function with caching."""
        if not self.cache_enabled:
            return await func(**kwargs)
            
        cache_key = self._get_cache_key(method, **kwargs)
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
            
        result = await func(**kwargs)
        self._cache[cache_key] = result
        self._cache_timestamps[cache_key] = datetime.now()
        
        return result


class AsyncPaginationProvider(AsyncDataProvider[T]):
    """
    Data provider with built-in pagination support.
    
    Example:
        ```python
        class UserPaginationProvider(AsyncPaginationProvider[User]):
            async def load_page(
                self, 
                page: int, 
                page_size: int,
                **kwargs
            ) -> PaginatedResult[User]:
                response = await api.get_users(
                    offset=(page - 1) * page_size,
                    limit=page_size,
                    **kwargs
                )
                
                return PaginatedResult(
                    results=response.users,
                    metadata=PaginationMetadata(
                        page=page,
                        page_size=page_size,
                        total=response.total,
                        pages=math.ceil(response.total / page_size),
                        has_next=page < math.ceil(response.total / page_size),
                        has_prev=page > 1
                    )
                )
        ```
    """
    
    def __init__(self, default_page_size: int = 20, **kwargs):
        super().__init__(**kwargs)
        self.default_page_size = default_page_size
    
    @abstractmethod
    async def load_page(
        self,
        page: int = 1,
        page_size: Optional[int] = None,
        **kwargs
    ) -> PaginatedResult[T]:
        """Load a specific page of results."""
        pass
    
    async def load(self, **kwargs) -> List[T]:
        """Load all items (first page by default)."""
        result = await self.load_page(page=1, **kwargs)
        return result.results
    
    async def load_all(self, **kwargs) -> List[T]:
        """Load all pages of results."""
        all_results = []
        page = 1
        
        while True:
            result = await self.load_page(page=page, **kwargs)
            all_results.extend(result.results)
            
            if not result.metadata.has_next:
                break
                
            page += 1
            
        return all_results


class AsyncSearchProvider(AsyncPaginationProvider[T]):
    """
    Data provider with search capabilities.
    
    Example:
        ```python
        class UserSearchProvider(AsyncSearchProvider[User]):
            async def search(
                self,
                query: str,
                page: int = 1,
                page_size: Optional[int] = None,
                **kwargs
            ) -> PaginatedResult[User]:
                return await api.search_users(
                    q=query,
                    offset=(page - 1) * (page_size or self.default_page_size),
                    limit=page_size or self.default_page_size,
                    **kwargs
                )
        ```
    """
    
    @abstractmethod
    async def search(
        self,
        query: str,
        page: int = 1,
        page_size: Optional[int] = None,
        **kwargs
    ) -> PaginatedResult[T]:
        """Search for items."""
        pass
    
    async def load_page(
        self,
        page: int = 1,
        page_size: Optional[int] = None,
        query: str = "",
        **kwargs
    ) -> PaginatedResult[T]:
        """Load page with optional search."""
        if query:
            return await self.search(
                query=query,
                page=page,
                page_size=page_size,
                **kwargs
            )
        else:
            # Default implementation - override if different behavior needed
            return await self.search(
                query="",
                page=page,
                page_size=page_size,
                **kwargs
            )


class MockDataProvider(AsyncDataProvider[Dict[str, Any]]):
    """
    Mock data provider for testing and development.
    
    Example:
        ```python
        provider = MockDataProvider(
            data=[
                {"id": 1, "name": "Item 1"},
                {"id": 2, "name": "Item 2"}
            ],
            delay=0.5  # Simulate network delay
        )
        ```
    """
    
    def __init__(self, data: List[Dict[str, Any]], delay: float = 0):
        super().__init__()
        self.data = data
        self.delay = delay
        self._id_counter = max((item.get('id', 0) for item in data), default=0) + 1
    
    async def _simulate_delay(self):
        """Simulate network delay."""
        if self.delay > 0:
            await asyncio.sleep(self.delay)
    
    async def load(self, **kwargs) -> List[Dict[str, Any]]:
        """Load all items."""
        await self._simulate_delay()
        return self.data.copy()
    
    async def get(self, id: Any) -> Optional[Dict[str, Any]]:
        """Get item by ID."""
        await self._simulate_delay()
        
        for item in self.data:
            if item.get('id') == id:
                return item.copy()
                
        return None
    
    async def save(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Save item."""
        await self._simulate_delay()
        
        if 'id' in item and item['id']:
            # Update existing
            for i, existing in enumerate(self.data):
                if existing.get('id') == item['id']:
                    self.data[i] = item.copy()
                    return item
        else:
            # Create new
            item = item.copy()
            item['id'] = self._id_counter
            self._id_counter += 1
            self.data.append(item)
            
        return item
    
    async def delete(self, id: Any) -> bool:
        """Delete item by ID."""
        await self._simulate_delay()
        
        for i, item in enumerate(self.data):
            if item.get('id') == id:
                del self.data[i]
                return True
                
        return False


class CompositeDataProvider(AsyncDataProvider[T]):
    """
    Combines multiple data providers into one.
    
    Useful for aggregating data from different sources.
    
    Example:
        ```python
        local_provider = LocalUserProvider()
        remote_provider = RemoteUserProvider()
        
        provider = CompositeDataProvider(
            providers=[local_provider, remote_provider],
            merge_strategy="union"  # or "local_first", "remote_first"
        )
        ```
    """
    
    def __init__(
        self,
        providers: List[AsyncDataProvider[T]],
        merge_strategy: str = "union"
    ):
        super().__init__()
        self.providers = providers
        self.merge_strategy = merge_strategy
    
    async def load(self, **kwargs) -> List[T]:
        """Load from all providers and merge results."""
        # Load from all providers concurrently
        results = await asyncio.gather(
            *[provider.load(**kwargs) for provider in self.providers],
            return_exceptions=True
        )
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if not isinstance(result, Exception):
                valid_results.extend(result)
        
        # Apply merge strategy
        if self.merge_strategy == "union":
            # Return all results
            return valid_results
        elif self.merge_strategy == "local_first":
            # Return first non-empty result
            for result in results:
                if not isinstance(result, Exception) and result:
                    return result
            return []
        elif self.merge_strategy == "remote_first":
            # Return last non-empty result
            for result in reversed(results):
                if not isinstance(result, Exception) and result:
                    return result
            return []
        
        return valid_results
    
    async def get(self, id: Any) -> Optional[T]:
        """Get from first provider that has the item."""
        for provider in self.providers:
            try:
                item = await provider.get(id)
                if item:
                    return item
            except Exception:
                continue
                
        return None
    
    async def save(self, item: T) -> T:
        """Save to all providers."""
        # Save to all providers concurrently
        results = await asyncio.gather(
            *[provider.save(item) for provider in self.providers],
            return_exceptions=True
        )
        
        # Return first successful result
        for result in results:
            if not isinstance(result, Exception):
                return result
                
        # If all failed, raise the first exception
        for result in results:
            if isinstance(result, Exception):
                raise result
                
        raise Exception("All providers failed to save")