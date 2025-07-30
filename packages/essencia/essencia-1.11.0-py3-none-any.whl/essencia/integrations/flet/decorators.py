"""
Flet-specific decorators for common security patterns.

Provides easy-to-use decorators that integrate Essencia's security
features with Flet applications.
"""

import logging
from typing import Optional, Dict, Any, Callable, Union
from functools import wraps
import asyncio

try:
    import flet as ft
except ImportError:
    raise ImportError("Flet is required for this module. Install with: pip install flet")

from .middleware import (
    FletRateLimiter,
    FletAuditLogger,
    FletSessionManager,
    FletAuthorizationMiddleware
)

logger = logging.getLogger(__name__)


def with_page_context(func: Callable) -> Callable:
    """
    Decorator that ensures a Flet page context is available.
    Extracts page from the first argument if it's a Flet control.
    """
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        page = _extract_page(args)
        if page:
            kwargs['_page'] = page
        return await func(*args, **kwargs)
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        page = _extract_page(args)
        if page:
            kwargs['_page'] = page
        return func(*args, **kwargs)
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


def _extract_page(args) -> Optional[ft.Page]:
    """Extract Flet page from arguments."""
    if args:
        # Direct page argument
        if isinstance(args[0], ft.Page):
            return args[0]
        
        # Control with page property
        if hasattr(args[0], 'page') and isinstance(args[0].page, ft.Page):
            return args[0].page
        
        # Event with page property
        if hasattr(args[0], 'page') and isinstance(args[0].page, ft.Page):
            return args[0].page
        
        # Check for control in event
        if hasattr(args[0], 'control') and hasattr(args[0].control, 'page'):
            return args[0].control.page
    
    return None


def flet_rate_limit(
    action: str = 'default',
    limit: int = 10,
    window: int = 60,
    message: Optional[str] = None
):
    """
    Rate limiting decorator for Flet event handlers.
    
    Args:
        action: Action identifier for rate limiting
        limit: Maximum allowed requests
        window: Time window in seconds
        message: Custom rate limit message
    """
    def decorator(func):
        @wraps(func)
        @with_page_context
        async def async_wrapper(*args, _page: Optional[ft.Page] = None, **kwargs):
            if not _page:
                logger.warning("No page context available for rate limiting")
                return await func(*args, **kwargs)
            
            # Get or create rate limiter
            if not hasattr(_page, '_security'):
                _page._security = {}
            if 'rate_limiter' not in _page._security:
                _page._security['rate_limiter'] = FletRateLimiter()
            
            rate_limiter = _page._security['rate_limiter']
            
            # Check rate limit
            if not rate_limiter.check_rate_limit(_page, action, limit, window):
                if message and hasattr(_page, 'snack_bar'):
                    _page.snack_bar = ft.SnackBar(
                        content=ft.Text(message),
                        bgcolor=ft.colors.ERROR
                    )
                    _page.snack_bar.open = True
                    _page.update()
                return
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        @with_page_context
        def sync_wrapper(*args, _page: Optional[ft.Page] = None, **kwargs):
            if not _page:
                logger.warning("No page context available for rate limiting")
                return func(*args, **kwargs)
            
            # Get or create rate limiter
            if not hasattr(_page, '_security'):
                _page._security = {}
            if 'rate_limiter' not in _page._security:
                _page._security['rate_limiter'] = FletRateLimiter()
            
            rate_limiter = _page._security['rate_limiter']
            
            # Check rate limit
            if not rate_limiter.check_rate_limit(_page, action, limit, window):
                if message and hasattr(_page, 'snack_bar'):
                    _page.snack_bar = ft.SnackBar(
                        content=ft.Text(message),
                        bgcolor=ft.colors.ERROR
                    )
                    _page.snack_bar.open = True
                    _page.update()
                return
            
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def flet_audit(
    action: str,
    resource: Optional[str] = None,
    include_args: bool = False
):
    """
    Audit logging decorator for Flet event handlers.
    
    Args:
        action: Action being performed
        resource: Resource being accessed
        include_args: Whether to include function arguments in audit log
    """
    def decorator(func):
        @wraps(func)
        @with_page_context
        async def async_wrapper(*args, _page: Optional[ft.Page] = None, **kwargs):
            if not _page:
                logger.warning("No page context available for audit logging")
                return await func(*args, **kwargs)
            
            # Get or create audit logger
            if not hasattr(_page, '_security'):
                _page._security = {}
            if 'audit_logger' not in _page._security:
                _page._security['audit_logger'] = FletAuditLogger()
            
            audit_logger = _page._security['audit_logger']
            
            # Prepare audit details
            details = {}
            if include_args:
                details['args'] = str(args)[:200]  # Limit size
                details['kwargs'] = str(kwargs)[:200]
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # Log success
                audit_logger.log_action(
                    _page, action, resource, 'SUCCESS', details
                )
                
                return result
                
            except Exception as e:
                # Log failure
                details['error'] = str(e)
                audit_logger.log_action(
                    _page, action, resource, 'FAILURE', details
                )
                raise
        
        @wraps(func)
        @with_page_context
        def sync_wrapper(*args, _page: Optional[ft.Page] = None, **kwargs):
            if not _page:
                logger.warning("No page context available for audit logging")
                return func(*args, **kwargs)
            
            # Get or create audit logger
            if not hasattr(_page, '_security'):
                _page._security = {}
            if 'audit_logger' not in _page._security:
                _page._security['audit_logger'] = FletAuditLogger()
            
            audit_logger = _page._security['audit_logger']
            
            # Prepare audit details
            details = {}
            if include_args:
                details['args'] = str(args)[:200]  # Limit size
                details['kwargs'] = str(kwargs)[:200]
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Log success
                audit_logger.log_action(
                    _page, action, resource, 'SUCCESS', details
                )
                
                return result
                
            except Exception as e:
                # Log failure
                details['error'] = str(e)
                audit_logger.log_action(
                    _page, action, resource, 'FAILURE', details
                )
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def flet_authorized(
    permission: Optional[str] = None,
    role: Optional[str] = None,
    redirect_to: str = '/unauthorized'
):
    """
    Authorization decorator for Flet event handlers.
    
    Args:
        permission: Required permission
        role: Required role (alternative to permission)
        redirect_to: Route to redirect unauthorized users
    """
    def decorator(func):
        @wraps(func)
        @with_page_context
        async def async_wrapper(*args, _page: Optional[ft.Page] = None, **kwargs):
            if not _page:
                logger.warning("No page context available for authorization")
                return await func(*args, **kwargs)
            
            # Get or create authorization middleware
            if not hasattr(_page, '_security'):
                _page._security = {}
            if 'auth_middleware' not in _page._security:
                _page._security['auth_middleware'] = FletAuthorizationMiddleware()
            
            auth_middleware = _page._security['auth_middleware']
            
            # Check authorization
            authorized = True
            
            if permission:
                authorized = auth_middleware.check_permission(_page, permission)
            elif role and hasattr(_page, 'session'):
                user_role = _page.session.get('user_role')
                authorized = user_role == role
            
            if not authorized:
                if hasattr(_page, 'go'):
                    _page.go(redirect_to)
                else:
                    await auth_middleware._show_unauthorized_message(_page)
                return
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        @with_page_context
        def sync_wrapper(*args, _page: Optional[ft.Page] = None, **kwargs):
            if not _page:
                logger.warning("No page context available for authorization")
                return func(*args, **kwargs)
            
            # Get or create authorization middleware
            if not hasattr(_page, '_security'):
                _page._security = {}
            if 'auth_middleware' not in _page._security:
                _page._security['auth_middleware'] = FletAuthorizationMiddleware()
            
            auth_middleware = _page._security['auth_middleware']
            
            # Check authorization
            authorized = True
            
            if permission:
                authorized = auth_middleware.check_permission(_page, permission)
            elif role and hasattr(_page, 'session'):
                user_role = _page.session.get('user_role')
                authorized = user_role == role
            
            if not authorized:
                if hasattr(_page, 'go'):
                    _page.go(redirect_to)
                else:
                    auth_middleware._show_unauthorized_message_sync(_page)
                return
            
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def flet_session_required(redirect_to: str = '/login'):
    """
    Decorator that requires a valid session.
    
    Args:
        redirect_to: Route to redirect unauthenticated users
    """
    def decorator(func):
        @wraps(func)
        @with_page_context
        async def async_wrapper(*args, _page: Optional[ft.Page] = None, **kwargs):
            if not _page:
                logger.warning("No page context available for session validation")
                return await func(*args, **kwargs)
            
            # Get or create session manager
            if not hasattr(_page, '_security'):
                _page._security = {}
            if 'session_manager' not in _page._security:
                _page._security['session_manager'] = FletSessionManager()
            
            session_manager = _page._security['session_manager']
            
            # Validate session
            if not session_manager.validate_session(_page):
                if hasattr(_page, 'go'):
                    _page.go(redirect_to)
                else:
                    if hasattr(_page, 'snack_bar'):
                        _page.snack_bar = ft.SnackBar(
                            content=ft.Text("Sessão expirada. Por favor, faça login novamente."),
                            bgcolor=ft.colors.WARNING
                        )
                        _page.snack_bar.open = True
                        _page.update()
                return
            
            return await func(*args, **kwargs)
        
        @wraps(func)
        @with_page_context
        def sync_wrapper(*args, _page: Optional[ft.Page] = None, **kwargs):
            if not _page:
                logger.warning("No page context available for session validation")
                return func(*args, **kwargs)
            
            # Get or create session manager
            if not hasattr(_page, '_security'):
                _page._security = {}
            if 'session_manager' not in _page._security:
                _page._security['session_manager'] = FletSessionManager()
            
            session_manager = _page._security['session_manager']
            
            # Validate session
            if not session_manager.validate_session(_page):
                if hasattr(_page, 'go'):
                    _page.go(redirect_to)
                else:
                    if hasattr(_page, 'snack_bar'):
                        _page.snack_bar = ft.SnackBar(
                            content=ft.Text("Sessão expirada. Por favor, faça login novamente."),
                            bgcolor=ft.colors.WARNING
                        )
                        _page.snack_bar.open = True
                        _page.update()
                return
            
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


# Convenience decorators for common scenarios

def audit_login(func):
    """Audit decorator specifically for login actions."""
    return flet_audit('LOGIN', 'auth')(func)


def audit_logout(func):
    """Audit decorator specifically for logout actions."""
    return flet_audit('LOGOUT', 'auth')(func)


def audit_data_access(resource: str):
    """Audit decorator for data access operations."""
    return flet_audit('DATA_ACCESS', resource)


def audit_data_modification(resource: str):
    """Audit decorator for data modification operations."""
    return flet_audit('DATA_MODIFICATION', resource)


def rate_limit_login(func):
    """Rate limit decorator for login attempts."""
    return flet_rate_limit('login', limit=5, window=300)(func)  # 5 attempts per 5 minutes


def rate_limit_api(func):
    """Rate limit decorator for API calls."""
    return flet_rate_limit('api', limit=100, window=60)(func)  # 100 requests per minute


def rate_limit_form(func):
    """Rate limit decorator for form submissions."""
    return flet_rate_limit('form', limit=10, window=60)(func)  # 10 submissions per minute