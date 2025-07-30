"""
Base service class providing common functionality for all services.
"""

import logging
from typing import Optional, Dict, Any, List, TYPE_CHECKING
import asyncio

from essencia.core.exceptions import (
    EssenciaException,
    ValidationError,
    DatabaseConnectionError,
    ServiceError,
    NotFoundError,
    AuthorizationError
)

if TYPE_CHECKING:
    from essencia.models.base import MongoModel

logger = logging.getLogger(__name__)


class BaseService:
    """
    Base service class with common functionality.
    
    Provides:
    - Database and cache access
    - Error handling
    - Logging
    - Common validation methods
    """
    
    def __init__(self, db_name: str = "essencia", use_async: bool = True):
        """
        Initialize service with database and cache.
        
        Args:
            db_name: Database name to use
            use_async: Whether to use async operations
        """
        self.db_name = db_name
        self.use_async = use_async
        self.logger = logger
        self._initialized = False
        
        # Lazy initialization of database and cache
        self._db = None
        self._cache = None
        self._async_db = None
        self._async_cache = None
    
    @property
    def db(self):
        """Get sync database instance."""
        if self._db is None:
            from essencia.database.sync_mongodb import SyncMongoDB
            self._db = SyncMongoDB(self.db_name)
        return self._db
    
    @property
    def cache(self):
        """Get sync cache instance."""
        if self._cache is None:
            try:
                from essencia.cache import get_cache
                self._cache = get_cache()
            except ImportError:
                self.logger.warning("Cache system not available")
                self._cache = None
        return self._cache
    
    async def initialize(self):
        """Initialize async resources."""
        if self._initialized:
            return
            
        if self.use_async:
            # Initialize async database
            from essencia.database.mongodb import get_async_db
            self._async_db = await get_async_db(self.db_name)
            
            # Initialize async cache
            try:
                from essencia.cache.async_cache import async_cache
                self._async_cache = async_cache
                await self._async_cache.initialize()
            except ImportError:
                self.logger.warning("Async cache system not available")
                self._async_cache = None
        
        self._initialized = True
        
    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Validate that required fields are present and not empty.
        
        Args:
            data: Dictionary to validate
            required_fields: List of required field names
            
        Raises:
            ValueError: If required fields are missing or empty
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)
                
        if missing_fields:
            raise ValidationError(f"Campos obrigatórios faltando: {', '.join(missing_fields)}")
            
    def handle_database_error(self, operation: str, error: Exception) -> None:
        """
        Handle database errors with proper logging and re-raising.
        
        Args:
            operation: Description of the operation that failed
            error: The exception that occurred
            
        Raises:
            Exception: Always raises with user-friendly message
        """
        self.logger.error(f"Database error during {operation}: {error}")
        raise DatabaseConnectionError(f"Erro ao {operation}. Por favor, tente novamente.")
        
    def check_authorization(self, user: Dict[str, Any], required_role: Optional[str] = None,
                          resource_owner: Optional[str] = None) -> None:
        """
        Check if user is authorized for an operation.
        
        Args:
            user: User dictionary with 'role' and 'key' fields
            required_role: Required role for the operation
            resource_owner: Key of the resource owner (for ownership checks)
            
        Raises:
            PermissionError: If user is not authorized
        """
        if not user:
            raise AuthorizationError("Usuário não autenticado")
            
        # Check role if required
        if required_role and user.get('role') != required_role:
            raise AuthorizationError(f"Acesso negado. Função requerida: {required_role}")
            
        # Check ownership if resource owner specified
        if resource_owner and str(user.get('key', user.get('_id'))) != str(resource_owner):
            raise AuthorizationError("Acesso negado. Você não tem permissão para acessar este recurso.")
            
    async def get_with_cache(self, cache_key: str, fetch_func, ttl: int = 300) -> Any:
        """
        Get data from cache or fetch if not cached.
        
        Args:
            cache_key: Key for caching
            fetch_func: Function to call if cache miss
            ttl: Time to live in seconds
            
        Returns:
            Cached or fetched data
        """
        try:
            if self.use_async and self._async_cache:
                # Use async cache
                cached = await self._async_cache.get(cache_key)
                if cached is not None:
                    self.logger.debug(f"Cache hit for key: {cache_key}")
                    return cached
                    
                # Fetch if not cached
                self.logger.debug(f"Cache miss for key: {cache_key}")
                data = await fetch_func()
                
                # Cache the result
                await self._async_cache.set(cache_key, data, ttl)
                return data
            elif self.cache:
                # Use sync cache with async wrapper
                cached = self.cache.get(cache_key)
                if cached is not None:
                    self.logger.debug(f"Cache hit for key: {cache_key}")
                    return cached
                    
                # Fetch if not cached
                data = await fetch_func()
                self.cache.set(cache_key, data, ttl)
                return data
            else:
                # No cache available
                return await fetch_func()
                
        except Exception as e:
            self.logger.warning(f"Cache operation failed: {e}")
            # Fall back to direct fetch
            return await fetch_func()
            
    def invalidate_cache(self, pattern: str) -> None:
        """
        Invalidate cache entries matching pattern.
        
        Args:
            pattern: Pattern to match cache keys (e.g., "patient:*")
        """
        try:
            if self.cache and hasattr(self.cache, 'delete_pattern'):
                self.cache.delete_pattern(pattern)
                self.logger.debug(f"Invalidated cache for pattern: {pattern}")
        except Exception as e:
            self.logger.warning(f"Failed to invalidate cache: {e}")
            
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
        
    def validate_key(self, key: str) -> bool:
        """
        Validate that a key has the correct format.
        
        Args:
            key: The key to validate
            
        Returns:
            True if key is valid, False otherwise
        """
        if not key or not isinstance(key, str):
            return False
        # Keys should be non-empty strings without special characters that could cause issues
        return len(key.strip()) > 0 and not any(char in key for char in ['$', '.', '\0'])
        
    def build_key_query(self, key_or_id: str) -> Dict[str, str]:
        """
        Build a query that works with both key and _id fields for backward compatibility.
        
        Args:
            key_or_id: Key or ID to search for
            
        Returns:
            MongoDB query dictionary
        """
        if not self.validate_key(key_or_id):
            raise ValidationError(f"Invalid key format: {key_or_id}")
            
        # Try key first, fallback to _id for backward compatibility
        return {'key': key_or_id}
        
    def format_response(self, data: Any, message: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format service response in standard structure.
        
        Args:
            data: The main response data
            message: Optional success message
            metadata: Optional metadata (pagination, etc.)
            
        Returns:
            Standardized response dictionary
        """
        response = {"success": True, "data": data}
        
        if message:
            response["message"] = message
            
        if metadata:
            response["metadata"] = metadata
            
        return response
        
    def format_error_response(self, error: Exception) -> Dict[str, Any]:
        """
        Format error response in standard structure.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Standardized error response
        """
        if isinstance(error, EssenciaException):
            return {
                "success": False,
                "error": {
                    "type": error.__class__.__name__,
                    "message": str(error),
                    "code": getattr(error, 'code', 'UNKNOWN_ERROR')
                }
            }
        else:
            # Don't expose internal errors to users
            return {
                "success": False,
                "error": {
                    "type": "InternalError",
                    "message": "Ocorreu um erro interno. Por favor, tente novamente.",
                    "code": "INTERNAL_ERROR"
                }
            }
            
    async def find_by_key(self, model_class: type, key: str):
        """
        Find a model instance by its key.
        
        Args:
            model_class: The model class to search
            key: The key to search for
            
        Returns:
            Model instance or None
        """
        try:
            await self.initialize()
            
            # Validate key format
            if not self.validate_key(key):
                self.logger.warning(f"Invalid key format for {model_class.__name__}: {key}")
                return None
            
            if self.use_async and hasattr(model_class, 'afind_by_key'):
                return await model_class.afind_by_key(key)
            else:
                # Fallback to sync in executor
                return await asyncio.get_event_loop().run_in_executor(
                    None, model_class.get_by_key, key
                )
        except Exception as e:
            self.logger.error(f"Error finding {model_class.__name__} by key {key}: {e}")
            return None
            
    async def create(self, model_class: type, data: Dict[str, Any], user_key: Optional[str] = None):
        """
        Create a new model instance.
        
        Args:
            model_class: The model class to create
            data: Data for the new instance
            user_key: Optional user key for auditing
            
        Returns:
            Created model instance
        """
        try:
            await self.initialize()
            
            instance = model_class(**data)
            
            if self.use_async and hasattr(instance, 'asave'):
                await instance.asave()
            else:
                # Fallback to sync in executor
                await asyncio.get_event_loop().run_in_executor(
                    None, instance.save_self
                )
            
            if user_key:
                self.logger.info(f"Created {model_class.__name__} {instance.key} by user {user_key}")
                
            return instance
        except Exception as e:
            self.handle_database_error(f"criar {model_class.__name__}", e)
            
    async def update(self, model_class: type, instance_key: str, updates: Dict[str, Any], user_key: Optional[str] = None):
        """
        Update a model instance.
        
        Args:
            model_class: The model class
            instance_key: Instance key
            updates: Updates to apply
            user_key: Optional user key for auditing
            
        Returns:
            Updated instance
        """
        try:
            await self.initialize()
            
            # Validate key format
            if not self.validate_key(instance_key):
                raise ValidationError(f"Invalid instance key format: {instance_key}")
            
            query = self.build_key_query(instance_key)
            
            if self.use_async and hasattr(model_class, 'afind_one'):
                instance = await model_class.afind_one(query)
                if not instance:
                    raise NotFoundError(f"{model_class.__name__} not found")
                    
                await instance.aupdate({'$set': updates})
            else:
                # Fallback to sync
                loop = asyncio.get_event_loop()
                instance = await loop.run_in_executor(
                    None, model_class.get_one, query
                )
                if not instance:
                    raise NotFoundError(f"{model_class.__name__} not found")
                    
                await loop.run_in_executor(
                    None, instance.update_self, {'$set': updates}
                )
            
            if user_key:
                self.logger.info(f"Updated {model_class.__name__} {instance.key} by user {user_key}")
                
            return instance
        except (ValidationError, ServiceError, NotFoundError):
            raise
        except Exception as e:
            self.handle_database_error(f"atualizar {model_class.__name__}", e)
            
    async def find_many(self, model_class: type, query: Dict[str, Any], 
                       sort: Optional[List] = None, limit: Optional[int] = None):
        """
        Find multiple model instances.
        
        Args:
            model_class: The model class to search
            query: MongoDB query
            sort: Sort specification
            limit: Maximum results
            
        Returns:
            List of model instances
        """
        try:
            await self.initialize()
            
            if self.use_async and hasattr(model_class, 'afind'):
                # Use async find
                results = await model_class.afind(query)
                
                if sort:
                    # Apply sorting after fetch
                    results = sorted(results, key=lambda x: [getattr(x, field) for field, _ in sort])
                    
                if limit:
                    results = results[:limit]
            else:
                # Fallback to sync
                loop = asyncio.get_event_loop()
                results = await loop.run_in_executor(
                    None, model_class.find, query
                )
                
                if sort:
                    results = sorted(results, key=lambda x: [getattr(x, field) for field, _ in sort])
                    
                if limit:
                    results = results[:limit]
                
            return results
        except Exception as e:
            self.logger.error(f"Error finding {model_class.__name__}: {e}")
            return []
            
    async def delete(self, model_class: type, instance_key: str):
        """
        Delete a model instance.
        
        Args:
            model_class: The model class
            instance_key: Instance key to delete
        """
        try:
            # Validate key format
            if not self.validate_key(instance_key):
                raise ValidationError(f"Invalid instance key format: {instance_key}")
            
            query = self.build_key_query(instance_key)
            model_class.delete_one(query)
            self.logger.info(f"Deleted {model_class.__name__} {instance_key}")
        except (ValidationError, ServiceError, NotFoundError):
            raise
        except Exception as e:
            self.handle_database_error(f"deletar {model_class.__name__}", e)