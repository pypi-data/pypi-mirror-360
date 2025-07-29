"""Essencia - A modern Python application framework."""

from essencia.core import Config, EssenciaException
from essencia.models import (
    # Async models
    User, UserCreate, UserUpdate, Session,
    # Sync models and base classes
    MongoModel, MongoId, ObjectReferenceId, StrEnum
)
from essencia.database import MongoDB, RedisClient, Database
from essencia.database.async_mongodb import AsyncMongoDB, get_async_db, create_async_db
from essencia.services import (
    # Existing services
    UserService, AuthService, SessionService,
    BaseService as LegacyBaseService, EnhancedBaseService,
    # New service framework
    BaseService, ServiceProtocol, ServiceConfig, ServiceError, ServiceResult,
    CacheMixin, AuditMixin, ValidationMixin, PaginationMixin, SearchMixin, ExportMixin,
    service_method, cached, audited, authorized, validated, transactional,
    RepositoryPattern, UnitOfWork, ServiceRegistry, ServiceFactory,
)
from essencia.ui import (
    EssenciaApp,
    # UI Controls
    ThemedTextField,
    ThemedDatePicker,
    ThemedDropdown,
    FormBuilder,
    SecureForm,
    UnifiedPagination,
    LazyLoadWidget,
    BaseDashboard,
    ThemedContainer,
    Panel,
    Section,
    TimelineItem,
    VerticalTimeline,
    HorizontalTimeline,
    LoadingIndicator,
    ThemedElevatedButton,
)
from essencia.security import (
    # Sanitization
    HTMLSanitizer,
    MarkdownSanitizer,
    sanitize_input,
    sanitize_name,
    sanitize_email,
    sanitize_phone,
    sanitize_cpf,
    # Session Management
    SessionManager,
    get_session_manager,
    create_secure_session,
    validate_current_session,
    destroy_current_session,
    # Authorization
    Role,
    Permission,
    PermissionManager,
    get_permission_manager,
    require_admin,
    require_medical_role,
    require_financial_access,
    # Rate Limiting
    RateLimiter,
    get_rate_limiter,
    rate_limit_login,
    rate_limit_api,
    # Encryption
    encrypt_cpf,
    decrypt_cpf,
    encrypt_medical_data,
    decrypt_medical_data,
)
from essencia.cache import IntelligentCache, AsyncCacheManager as AsyncCache
from essencia.utils import (
    CPFValidator,
    CNPJValidator,
    PhoneValidator,
    EmailValidator,
    DateValidator,
    MoneyValidator,
    PasswordValidator,
)
from essencia.fields import (
    EncryptedStr,
    EncryptedCPF,
    EncryptedRG,
    EncryptedMedicalData,
    DefaultDate,
    DefaultDateTime,
)
from essencia.web import (
    # App factory
    create_app,
    create_flet_app,
    FastAPIConfig,
    APISettings,
    # Dependencies
    get_db,
    get_async_db,
    get_cache,
    get_current_user,
    require_auth,
    require_role,
    # Routers
    BaseRouter,
    CRUDRouter,
    AuthRouter,
    # WebSocket
    WebSocketManager,
    ConnectionManager,
    # Security
    create_access_token,
    verify_token,
    OAuth2PasswordBearerWithCookie,
)

__version__ = "1.6.0"

__all__ = [
    # Core
    "Config",
    "EssenciaException",
    # Models - Async
    "User",
    "UserCreate",
    "UserUpdate",
    "Session",
    # Models - Sync and Base
    "MongoModel",
    "MongoId",
    "ObjectReferenceId",
    "StrEnum",
    # Database
    "MongoDB",
    "RedisClient",
    "Database",
    # Async Database
    "AsyncMongoDB",
    "get_async_db",
    "create_async_db",
    # Services - Existing
    "UserService",
    "AuthService",
    "SessionService",
    "LegacyBaseService",
    "EnhancedBaseService",
    # Services - Framework
    "BaseService",
    "ServiceProtocol",
    "ServiceConfig",
    "ServiceError",
    "ServiceResult",
    # Service Mixins
    "CacheMixin",
    "AuditMixin",
    "ValidationMixin",
    "PaginationMixin",
    "SearchMixin",
    "ExportMixin",
    # Service Decorators
    "service_method",
    "cached",
    "audited",
    "authorized",
    "validated",
    "transactional",
    # Service Patterns
    "RepositoryPattern",
    "UnitOfWork",
    "ServiceRegistry",
    "ServiceFactory",
    # UI
    "EssenciaApp",
    # UI Controls
    "ThemedTextField",
    "ThemedDatePicker",
    "ThemedDropdown",
    "FormBuilder",
    "SecureForm",
    "UnifiedPagination",
    "LazyLoadWidget",
    "BaseDashboard",
    "ThemedContainer",
    "Panel",
    "Section",
    "TimelineItem",
    "VerticalTimeline",
    "HorizontalTimeline",
    "LoadingIndicator",
    "ThemedElevatedButton",
    # Cache
    "IntelligentCache",
    "AsyncCache",
    # Security - Sanitization
    "HTMLSanitizer",
    "MarkdownSanitizer",
    "sanitize_input",
    "sanitize_name",
    "sanitize_email",
    "sanitize_phone",
    "sanitize_cpf",
    # Security - Session Management
    "SessionManager",
    "get_session_manager",
    "create_secure_session",
    "validate_current_session",
    "destroy_current_session",
    # Security - Authorization
    "Role",
    "Permission",
    "PermissionManager",
    "get_permission_manager",
    "require_admin",
    "require_medical_role",
    "require_financial_access",
    # Security - Rate Limiting
    "RateLimiter",
    "get_rate_limiter",
    "rate_limit_login",
    "rate_limit_api",
    # Security - Encryption
    "encrypt_cpf",
    "decrypt_cpf",
    "encrypt_medical_data",
    "decrypt_medical_data",
    # Utils - Validators
    "CPFValidator",
    "CNPJValidator",
    "PhoneValidator",
    "EmailValidator",
    "DateValidator",
    "MoneyValidator",
    "PasswordValidator",
    # Fields
    "EncryptedStr",
    "EncryptedCPF",
    "EncryptedRG",
    "EncryptedMedicalData",
    "DefaultDate",
    "DefaultDateTime",
    # Web - App Factory
    "create_app",
    "create_flet_app",
    "FastAPIConfig",
    "APISettings",
    # Web - Dependencies
    "get_db",
    "get_async_db",
    "get_cache",
    "get_current_user",
    "require_auth",
    "require_role",
    # Web - Routers
    "BaseRouter",
    "CRUDRouter",
    "AuthRouter",
    # Web - WebSocket
    "WebSocketManager",
    "ConnectionManager",
    # Web - Security
    "create_access_token",
    "verify_token",
    "OAuth2PasswordBearerWithCookie",
]
