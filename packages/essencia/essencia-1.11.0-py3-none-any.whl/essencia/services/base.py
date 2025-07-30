"""
Base service patterns for building robust service layers.
"""

import logging
from typing import Optional, Dict, Any, List, TypeVar, Generic, Protocol, runtime_checkable
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

T = TypeVar('T')
TModel = TypeVar('TModel')


class CacheStrategy(Enum):
    """Cache strategies for services."""
    NO_CACHE = "no_cache"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    READ_THROUGH = "read_through"
    REFRESH_AHEAD = "refresh_ahead"


@dataclass
class ServiceConfig:
    """Configuration for services."""
    database_name: str = "essencia"
    cache_enabled: bool = True
    cache_ttl: int = 300
    cache_strategy: CacheStrategy = CacheStrategy.READ_THROUGH
    audit_enabled: bool = True
    use_async: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: float = 30.0
    batch_size: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceResult(Generic[T]):
    """Standard result wrapper for service operations."""
    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @classmethod
    def ok(cls, data: T, **metadata) -> 'ServiceResult[T]':
        """Create successful result."""
        return cls(success=True, data=data, metadata=metadata)
    
    @classmethod
    def fail(cls, error: str, **metadata) -> 'ServiceResult[T]':
        """Create failed result."""
        return cls(success=False, error=error, metadata=metadata)


class ServiceError(Exception):
    """Base exception for service layer errors."""
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


@runtime_checkable
class DatabaseProtocol(Protocol):
    """Protocol for database implementations."""
    
    def find(self, collection: str, filter: Dict[str, Any], **kwargs) -> List[Dict[str, Any]]:
        """Find documents in collection."""
        ...
    
    def find_one(self, collection: str, filter: Dict[str, Any], **kwargs) -> Optional[Dict[str, Any]]:
        """Find single document in collection."""
        ...
    
    def insert_one(self, collection: str, document: Dict[str, Any], **kwargs) -> Any:
        """Insert single document."""
        ...
    
    def update_one(self, collection: str, filter: Dict[str, Any], update: Dict[str, Any], **kwargs) -> Any:
        """Update single document."""
        ...
    
    def delete_one(self, collection: str, filter: Dict[str, Any], **kwargs) -> Any:
        """Delete single document."""
        ...


@runtime_checkable
class CacheProtocol(Protocol):
    """Protocol for cache implementations."""
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        ...
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        ...
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        ...
    
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        ...


@runtime_checkable
class ServiceProtocol(Protocol):
    """Protocol that all services should implement."""
    
    async def initialize(self) -> None:
        """Initialize service resources."""
        ...
    
    async def cleanup(self) -> None:
        """Cleanup service resources."""
        ...
    
    async def health_check(self) -> ServiceResult[Dict[str, Any]]:
        """Check service health."""
        ...


class BaseService(ABC):
    """
    Base service class with common functionality.
    
    Provides:
    - Database and cache abstraction
    - Error handling and retries
    - Logging and monitoring
    - Common validation methods
    - Async/sync dual support
    """
    
    def __init__(
        self,
        db: Optional[DatabaseProtocol] = None,
        cache: Optional[CacheProtocol] = None,
        config: Optional[ServiceConfig] = None
    ):
        """
        Initialize service with database, cache, and configuration.
        
        Args:
            db: Database instance
            cache: Cache instance
            config: Service configuration
        """
        self.config = config or ServiceConfig()
        self.db = db
        self.cache = cache if self.config.cache_enabled else None
        self.logger = logger
        self._initialized = False
        self._cleanup_handlers: List[callable] = []
        
    async def initialize(self) -> None:
        """Initialize service resources."""
        if self._initialized:
            return
            
        self.logger.info(f"Initializing {self.__class__.__name__}")
        
        # Initialize database connection if needed
        if self.db and hasattr(self.db, 'initialize'):
            await self.db.initialize()
            
        # Initialize cache connection if needed
        if self.cache and hasattr(self.cache, 'initialize'):
            await self.cache.initialize()
            
        self._initialized = True
        self.logger.info(f"{self.__class__.__name__} initialized successfully")
        
    async def cleanup(self) -> None:
        """Cleanup service resources."""
        self.logger.info(f"Cleaning up {self.__class__.__name__}")
        
        # Run cleanup handlers
        for handler in self._cleanup_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:
                self.logger.error(f"Error in cleanup handler: {e}")
                
        # Cleanup database connection
        if self.db and hasattr(self.db, 'cleanup'):
            await self.db.cleanup()
            
        # Cleanup cache connection
        if self.cache and hasattr(self.cache, 'cleanup'):
            await self.cache.cleanup()
            
        self._initialized = False
        
    def add_cleanup_handler(self, handler: callable) -> None:
        """Add a cleanup handler to be called during cleanup."""
        self._cleanup_handlers.append(handler)
        
    async def health_check(self) -> ServiceResult[Dict[str, Any]]:
        """
        Check service health.
        
        Returns:
            ServiceResult with health status
        """
        health_data = {
            'service': self.__class__.__name__,
            'status': 'healthy',
            'initialized': self._initialized,
            'timestamp': datetime.utcnow(),
            'components': {}
        }
        
        # Check database health
        if self.db:
            try:
                # Simple query to check connection
                if hasattr(self.db, 'ping'):
                    await self.db.ping()
                health_data['components']['database'] = 'healthy'
            except Exception as e:
                health_data['components']['database'] = f'unhealthy: {str(e)}'
                health_data['status'] = 'degraded'
                
        # Check cache health
        if self.cache:
            try:
                # Simple operation to check connection
                test_key = f"health_check_{self.__class__.__name__}"
                self.cache.set(test_key, "ok", ttl=10)
                if self.cache.get(test_key) == "ok":
                    health_data['components']['cache'] = 'healthy'
                else:
                    health_data['components']['cache'] = 'unhealthy: read/write failed'
                    health_data['status'] = 'degraded'
            except Exception as e:
                health_data['components']['cache'] = f'unhealthy: {str(e)}'
                health_data['status'] = 'degraded'
                
        return ServiceResult.ok(health_data)
        
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Validate that required fields are present and not empty.
        
        Args:
            data: Dictionary to validate
            required_fields: List of required field names
            
        Raises:
            ServiceError: If required fields are missing or empty
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
                
        if missing_fields:
            raise ServiceError(
                f"Required fields missing: {', '.join(missing_fields)}",
                code="VALIDATION_ERROR",
                details={"missing_fields": missing_fields}
            )
            
    def sanitize_input(self, data: Dict[str, Any], allowed_fields: List[str]) -> Dict[str, Any]:
        """
        Sanitize input by only allowing specified fields.
        
        Args:
            data: Input data dictionary
            allowed_fields: List of allowed field names
            
        Returns:
            Sanitized dictionary with only allowed fields
        """
        return {k: v for k, v in data.items() if k in allowed_fields}
        
    async def with_retry(self, func: callable, *args, **kwargs) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Last exception if all retries fail
        """
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                    self.logger.warning(
                        f"Retry {attempt + 1}/{self.config.max_retries} for {func.__name__} "
                        f"after {delay}s delay. Error: {e}"
                    )
                    await asyncio.sleep(delay)
                else:
                    self.logger.error(f"All retries failed for {func.__name__}: {e}")
                    
        raise last_error
        
    async def get_with_cache(
        self,
        cache_key: str,
        fetch_func: callable,
        ttl: Optional[int] = None,
        force_refresh: bool = False
    ) -> Any:
        """
        Get data from cache or fetch if not cached.
        
        Args:
            cache_key: Key for caching
            fetch_func: Function to call if cache miss
            ttl: Time to live in seconds (uses config default if not provided)
            force_refresh: Force fetch even if cached
            
        Returns:
            Cached or fetched data
        """
        if not self.cache or force_refresh:
            return await self._fetch_and_cache(cache_key, fetch_func, ttl)
            
        try:
            # Try to get from cache
            cached = self.cache.get(cache_key)
            if cached is not None:
                self.logger.debug(f"Cache hit for key: {cache_key}")
                return cached
                
            # Cache miss, fetch data
            return await self._fetch_and_cache(cache_key, fetch_func, ttl)
            
        except Exception as e:
            self.logger.warning(f"Cache operation failed: {e}")
            # Fall back to direct fetch
            if asyncio.iscoroutinefunction(fetch_func):
                return await fetch_func()
            else:
                return fetch_func()
                
    async def _fetch_and_cache(self, cache_key: str, fetch_func: callable, ttl: Optional[int] = None) -> Any:
        """Fetch data and cache it."""
        self.logger.debug(f"Cache miss for key: {cache_key}")
        
        # Fetch data
        if asyncio.iscoroutinefunction(fetch_func):
            data = await fetch_func()
        else:
            data = fetch_func()
            
        # Cache the result if cache is available
        if self.cache and data is not None:
            cache_ttl = ttl or self.config.cache_ttl
            try:
                self.cache.set(cache_key, data, cache_ttl)
                self.logger.debug(f"Cached key: {cache_key} with TTL: {cache_ttl}")
            except Exception as e:
                self.logger.warning(f"Failed to cache data: {e}")
                
        return data
        
    def invalidate_cache(self, pattern: str) -> None:
        """
        Invalidate cache entries matching pattern.
        
        Args:
            pattern: Pattern to match cache keys (e.g., "patient:*")
        """
        if not self.cache:
            return
            
        try:
            if hasattr(self.cache, 'delete_pattern'):
                self.cache.delete_pattern(pattern)
            else:
                # Fallback for caches without pattern support
                self.cache.delete(pattern)
            self.logger.debug(f"Invalidated cache for pattern: {pattern}")
        except Exception as e:
            self.logger.warning(f"Failed to invalidate cache: {e}")
            
    def log_operation(self, operation: str, details: Optional[Dict[str, Any]] = None) -> None:
        """Log service operation for monitoring."""
        log_entry = {
            'service': self.__class__.__name__,
            'operation': operation,
            'timestamp': datetime.utcnow(),
            'details': details or {}
        }
        self.logger.info(f"Service operation: {operation}", extra=log_entry)
        
    @abstractmethod
    async def validate_permissions(self, user: Dict[str, Any], operation: str, resource: Any = None) -> bool:
        """
        Validate user permissions for operation.
        
        Args:
            user: User information
            operation: Operation being performed
            resource: Optional resource being accessed
            
        Returns:
            True if authorized, False otherwise
        """
        pass