"""
Common service patterns and architectural components.
"""

from typing import Dict, Any, List, Optional, Type, TypeVar, Generic, Protocol
from abc import ABC, abstractmethod
import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime

from .base import BaseService, ServiceConfig, ServiceError

T = TypeVar('T')
TModel = TypeVar('TModel')


class RepositoryProtocol(Protocol[TModel]):
    """Protocol for repository implementations."""
    
    async def find_by_id(self, id: str) -> Optional[TModel]:
        """Find entity by ID."""
        ...
        
    async def find_all(self, filter: Optional[Dict[str, Any]] = None) -> List[TModel]:
        """Find all entities matching filter."""
        ...
        
    async def create(self, entity: TModel) -> TModel:
        """Create new entity."""
        ...
        
    async def update(self, id: str, entity: TModel) -> Optional[TModel]:
        """Update existing entity."""
        ...
        
    async def delete(self, id: str) -> bool:
        """Delete entity by ID."""
        ...


class RepositoryPattern(Generic[TModel], ABC):
    """
    Generic repository pattern implementation.
    
    Provides standard CRUD operations for any model type.
    """
    
    def __init__(self, model_class: Type[TModel], collection_name: str, db: Any):
        """
        Initialize repository.
        
        Args:
            model_class: Model class for type checking
            collection_name: Database collection name
            db: Database instance
        """
        self.model_class = model_class
        self.collection_name = collection_name
        self.db = db
        self._collection = None
        
    @property
    def collection(self):
        """Get database collection."""
        if self._collection is None:
            self._collection = self.db[self.collection_name]
        return self._collection
        
    async def find_by_id(self, id: str) -> Optional[TModel]:
        """Find entity by ID."""
        doc = await self.collection.find_one({"_id": id})
        if doc:
            return self.model_class(**doc)
        return None
        
    async def find_one(self, filter: Dict[str, Any]) -> Optional[TModel]:
        """Find single entity matching filter."""
        doc = await self.collection.find_one(filter)
        if doc:
            return self.model_class(**doc)
        return None
        
    async def find_all(
        self,
        filter: Optional[Dict[str, Any]] = None,
        sort: Optional[List[tuple]] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None
    ) -> List[TModel]:
        """Find all entities matching filter."""
        query = self.collection.find(filter or {})
        
        if sort:
            query = query.sort(sort)
        if skip:
            query = query.skip(skip)
        if limit:
            query = query.limit(limit)
            
        docs = await query.to_list(length=limit)
        return [self.model_class(**doc) for doc in docs]
        
    async def count(self, filter: Optional[Dict[str, Any]] = None) -> int:
        """Count entities matching filter."""
        return await self.collection.count_documents(filter or {})
        
    async def create(self, entity: TModel) -> TModel:
        """Create new entity."""
        # Convert to dict
        if hasattr(entity, 'model_dump'):
            doc = entity.model_dump()
        elif hasattr(entity, 'to_dict'):
            doc = entity.to_dict()
        else:
            doc = entity.__dict__
            
        # Insert
        result = await self.collection.insert_one(doc)
        doc['_id'] = result.inserted_id
        
        # Return updated entity
        return self.model_class(**doc)
        
    async def update(self, id: str, entity: TModel, partial: bool = False) -> Optional[TModel]:
        """Update existing entity."""
        # Convert to dict
        if hasattr(entity, 'model_dump'):
            doc = entity.model_dump(exclude_unset=partial)
        elif hasattr(entity, 'to_dict'):
            doc = entity.to_dict()
        else:
            doc = entity.__dict__
            
        # Remove ID from update
        doc.pop('_id', None)
        doc.pop('id', None)
        
        # Update
        if partial:
            result = await self.collection.update_one(
                {"_id": id},
                {"$set": doc}
            )
        else:
            result = await self.collection.replace_one(
                {"_id": id},
                doc
            )
            
        if result.modified_count > 0:
            return await self.find_by_id(id)
        return None
        
    async def delete(self, id: str) -> bool:
        """Delete entity by ID."""
        result = await self.collection.delete_one({"_id": id})
        return result.deleted_count > 0
        
    async def delete_many(self, filter: Dict[str, Any]) -> int:
        """Delete multiple entities."""
        result = await self.collection.delete_many(filter)
        return result.deleted_count
        
    async def exists(self, filter: Dict[str, Any]) -> bool:
        """Check if entity exists."""
        count = await self.collection.count_documents(filter, limit=1)
        return count > 0
        
    async def bulk_create(self, entities: List[TModel]) -> List[TModel]:
        """Create multiple entities."""
        # Convert to documents
        docs = []
        for entity in entities:
            if hasattr(entity, 'model_dump'):
                doc = entity.model_dump()
            elif hasattr(entity, 'to_dict'):
                doc = entity.to_dict()
            else:
                doc = entity.__dict__
            docs.append(doc)
            
        # Bulk insert
        result = await self.collection.insert_many(docs)
        
        # Update IDs and return
        for i, doc in enumerate(docs):
            doc['_id'] = result.inserted_ids[i]
            
        return [self.model_class(**doc) for doc in docs]
        
    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run aggregation pipeline."""
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)


@dataclass
class Transaction:
    """Represents a unit of work transaction."""
    id: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    operations: List[Dict[str, Any]] = field(default_factory=list)
    committed: bool = False
    rolled_back: bool = False
    
    def add_operation(self, operation: str, collection: str, data: Any):
        """Add operation to transaction."""
        self.operations.append({
            'operation': operation,
            'collection': collection,
            'data': data,
            'timestamp': datetime.utcnow()
        })


class UnitOfWork:
    """
    Unit of Work pattern for managing transactions across repositories.
    
    Ensures all operations within a unit succeed or fail together.
    """
    
    def __init__(self, db: Any):
        """
        Initialize unit of work.
        
        Args:
            db: Database instance
        """
        self.db = db
        self._repositories: Dict[str, RepositoryPattern] = {}
        self._transaction: Optional[Transaction] = None
        self._session = None
        
    def register_repository(self, name: str, repository: RepositoryPattern):
        """Register a repository with the unit of work."""
        self._repositories[name] = repository
        
    def get_repository(self, name: str) -> Optional[RepositoryPattern]:
        """Get registered repository by name."""
        return self._repositories.get(name)
        
    @asynccontextmanager
    async def transaction(self):
        """Start a new transaction context."""
        import uuid
        
        # Start transaction
        self._transaction = Transaction(id=str(uuid.uuid4()))
        
        # Start database session if supported
        if hasattr(self.db, 'start_session'):
            self._session = await self.db.start_session()
            self._session.start_transaction()
            
        try:
            yield self
            await self.commit()
        except Exception as e:
            await self.rollback()
            raise
        finally:
            if self._session:
                await self._session.end_session()
            self._transaction = None
            self._session = None
            
    async def commit(self):
        """Commit the current transaction."""
        if not self._transaction:
            raise ServiceError("No active transaction", code="NO_TRANSACTION")
            
        if self._transaction.committed:
            raise ServiceError("Transaction already committed", code="ALREADY_COMMITTED")
            
        if self._session:
            await self._session.commit_transaction()
            
        self._transaction.committed = True
        
    async def rollback(self):
        """Rollback the current transaction."""
        if not self._transaction:
            raise ServiceError("No active transaction", code="NO_TRANSACTION")
            
        if self._transaction.rolled_back:
            raise ServiceError("Transaction already rolled back", code="ALREADY_ROLLED_BACK")
            
        if self._session:
            await self._session.abort_transaction()
            
        self._transaction.rolled_back = True
        
    def add_operation(self, operation: str, collection: str, data: Any):
        """Add operation to current transaction."""
        if self._transaction:
            self._transaction.add_operation(operation, collection, data)


class ServiceRegistry:
    """
    Service registry for managing service instances.
    
    Provides centralized service discovery and lifecycle management.
    """
    
    def __init__(self):
        """Initialize service registry."""
        self._services: Dict[str, BaseService] = {}
        self._service_classes: Dict[str, Type[BaseService]] = {}
        self._configs: Dict[str, ServiceConfig] = {}
        self._lock = asyncio.Lock()
        
    def register_class(self, name: str, service_class: Type[BaseService], config: Optional[ServiceConfig] = None):
        """
        Register a service class.
        
        Args:
            name: Service name
            service_class: Service class
            config: Service configuration
        """
        self._service_classes[name] = service_class
        if config:
            self._configs[name] = config
            
    async def get_service(self, name: str) -> BaseService:
        """
        Get or create service instance.
        
        Args:
            name: Service name
            
        Returns:
            Service instance
        """
        async with self._lock:
            # Return existing instance
            if name in self._services:
                return self._services[name]
                
            # Create new instance
            if name not in self._service_classes:
                raise ServiceError(f"Service not registered: {name}", code="SERVICE_NOT_FOUND")
                
            service_class = self._service_classes[name]
            config = self._configs.get(name)
            
            # Create and initialize service
            service = service_class(config=config)
            await service.initialize()
            
            # Store instance
            self._services[name] = service
            
            return service
            
    async def stop_service(self, name: str):
        """Stop and remove service instance."""
        async with self._lock:
            if name in self._services:
                service = self._services[name]
                await service.cleanup()
                del self._services[name]
                
    async def stop_all(self):
        """Stop all registered services."""
        async with self._lock:
            # Cleanup all services
            for service in self._services.values():
                try:
                    await service.cleanup()
                except Exception as e:
                    logger.error(f"Error stopping service: {e}")
                    
            # Clear registry
            self._services.clear()
            
    def list_services(self) -> List[str]:
        """List all registered service names."""
        return list(self._service_classes.keys())
        
    def get_service_status(self, name: str) -> Dict[str, Any]:
        """Get service status information."""
        return {
            'name': name,
            'registered': name in self._service_classes,
            'instantiated': name in self._services,
            'class': self._service_classes.get(name).__name__ if name in self._service_classes else None,
            'config': self._configs.get(name)
        }


class ServiceFactory:
    """
    Factory for creating service instances with dependency injection.
    """
    
    def __init__(self, registry: Optional[ServiceRegistry] = None):
        """
        Initialize service factory.
        
        Args:
            registry: Service registry to use
        """
        self.registry = registry or ServiceRegistry()
        self._dependencies: Dict[str, List[str]] = {}
        
    def register(
        self,
        name: str,
        service_class: Type[BaseService],
        config: Optional[ServiceConfig] = None,
        dependencies: Optional[List[str]] = None
    ):
        """
        Register a service with dependencies.
        
        Args:
            name: Service name
            service_class: Service class
            config: Service configuration
            dependencies: List of dependent service names
        """
        self.registry.register_class(name, service_class, config)
        if dependencies:
            self._dependencies[name] = dependencies
            
    async def create(self, name: str, **kwargs) -> BaseService:
        """
        Create service instance with dependencies injected.
        
        Args:
            name: Service name
            **kwargs: Additional arguments for service
            
        Returns:
            Service instance with dependencies
        """
        # Get dependencies first
        deps = {}
        if name in self._dependencies:
            for dep_name in self._dependencies[name]:
                deps[dep_name] = await self.registry.get_service(dep_name)
                
        # Create service with dependencies
        service_class = self.registry._service_classes[name]
        config = self.registry._configs.get(name)
        
        # Inject dependencies
        service = service_class(config=config, **deps, **kwargs)
        await service.initialize()
        
        return service
        
    def create_batch(self, services: List[Dict[str, Any]]) -> Dict[str, asyncio.Task]:
        """
        Create multiple services concurrently.
        
        Args:
            services: List of service configurations
            
        Returns:
            Dict of service names to creation tasks
        """
        tasks = {}
        for service_config in services:
            name = service_config['name']
            kwargs = service_config.get('kwargs', {})
            tasks[name] = asyncio.create_task(self.create(name, **kwargs))
            
        return tasks