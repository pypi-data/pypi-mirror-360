"""
FastAPI web framework integration for Essencia.

This module provides FastAPI-based web application support with:
- Application factory pattern
- Middleware integration
- Dependency injection
- WebSocket support
- Security integration
- Error handling
"""

from .app import (
    create_app,
    FastAPIConfig,
    APISettings,
)
from .dependencies import (
    get_db,
    get_async_db,
    get_cache,
    get_current_user,
    require_auth,
    require_role,
)
from .exceptions import (
    HTTPException,
    ValidationException,
    AuthenticationException,
    PermissionException,
    setup_exception_handlers,
)
from .middleware import (
    setup_middleware,
    LoggingMiddleware,
    SecurityMiddleware,
    CORSMiddleware,
)
from .routers import (
    BaseRouter,
    CRUDRouter,
    AuthRouter,
)
from .websocket import (
    WebSocketManager,
    ConnectionManager,
)
from .security import (
    create_access_token,
    verify_token,
    OAuth2PasswordBearerWithCookie,
)

__all__ = [
    # App factory
    'create_app',
    'FastAPIConfig',
    'APISettings',
    # Dependencies
    'get_db',
    'get_async_db',
    'get_cache',
    'get_current_user',
    'require_auth',
    'require_role',
    # Exceptions
    'HTTPException',
    'ValidationException',
    'AuthenticationException',
    'PermissionException',
    'setup_exception_handlers',
    # Middleware
    'setup_middleware',
    'LoggingMiddleware',
    'SecurityMiddleware',
    'CORSMiddleware',
    # Routers
    'BaseRouter',
    'CRUDRouter',
    'AuthRouter',
    # WebSocket
    'WebSocketManager',
    'ConnectionManager',
    # Security
    'create_access_token',
    'verify_token',
    'OAuth2PasswordBearerWithCookie',
]