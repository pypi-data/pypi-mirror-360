"""
Essencia Services Module - Base service patterns for building robust applications.

This module provides a foundation for service-oriented architecture with:
- Database and cache abstraction
- Error handling patterns
- Authorization framework
- Audit trail integration
- Async/sync dual support
"""

# Import existing services
from .user_service import UserService
from .auth_service import AuthService
from .session_service import SessionService

# Import legacy base service (being replaced by new base)
from .base_service import BaseService as LegacyBaseService
from .service_mixins import EnhancedBaseService

# Import new service framework
from .base import (
    BaseService,
    ServiceProtocol,
    CacheStrategy,
    ServiceConfig,
    ServiceError,
    ServiceResult,
)

from .mixins import (
    CacheMixin,
    AuditMixin,
    ValidationMixin,
    PaginationMixin,
    SearchMixin,
    ExportMixin,
)

from .decorators import (
    service_method,
    cached,
    audited,
    authorized,
    validated,
    transactional,
)

from .patterns import (
    RepositoryPattern,
    UnitOfWork,
    ServiceRegistry,
    ServiceFactory,
)

__all__ = [
    # Existing services
    'UserService',
    'AuthService',
    'SessionService',
    
    # Legacy base classes (for backward compatibility)
    'LegacyBaseService',
    'EnhancedBaseService',
    
    # New base classes
    'BaseService',
    'ServiceProtocol',
    'CacheStrategy',
    'ServiceConfig',
    'ServiceError',
    'ServiceResult',
    
    # Mixins
    'CacheMixin',
    'AuditMixin',
    'ValidationMixin',
    'PaginationMixin',
    'SearchMixin',
    'ExportMixin',
    
    # Decorators
    'service_method',
    'cached',
    'audited',
    'authorized',
    'validated',
    'transactional',
    
    # Patterns
    'RepositoryPattern',
    'UnitOfWork',
    'ServiceRegistry',
    'ServiceFactory',
]