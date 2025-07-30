"""
Flet-specific middleware adapters for Essencia security features.

Provides middleware that integrates Essencia's security features
with Flet's page and component model.
"""

import logging
from typing import Optional, Dict, Any, Callable, List
from functools import wraps
import asyncio

try:
    import flet as ft
except ImportError:
    raise ImportError("Flet is required for this module. Install with: pip install flet")

from essencia.security import (
    RateLimiter,
    get_rate_limiter,
    AuditLogger,
    get_audit_logger,
    SessionManager,
    get_session_manager,
    PermissionManager,
    get_permission_manager,
    WebSecurityHeaders,
    get_security_headers
)

logger = logging.getLogger(__name__)


class FletRateLimiter:
    """
    Flet-specific rate limiter that extracts user context from Flet pages.
    """
    
    def __init__(self, rate_limiter: Optional[RateLimiter] = None):
        """Initialize with an optional rate limiter instance."""
        self.rate_limiter = rate_limiter or get_rate_limiter()
    
    def check_rate_limit(self, page: ft.Page, action: str, limit: int = 10, 
                        window: int = 60) -> bool:
        """
        Check rate limit for a Flet page action.
        
        Args:
            page: Flet page instance
            action: Action identifier (e.g., 'login', 'form_submit')
            limit: Maximum allowed requests
            window: Time window in seconds
            
        Returns:
            True if action is allowed, False if rate limited
        """
        # Extract user identifier from page
        identifier = self._get_identifier(page)
        
        # Check rate limit
        result = self.rate_limiter.check_limit(
            identifier=identifier,
            action=action,
            limit=limit,
            window=window
        )
        
        if not result.allowed:
            self._show_rate_limit_message(page, result)
        
        return result.allowed
    
    def _get_identifier(self, page: ft.Page) -> str:
        """Extract identifier from Flet page."""
        # Try to get user ID from session
        if hasattr(page, 'session') and page.session.get('user_id'):
            return f"user:{page.session.get('user_id')}"
        
        # Fall back to client IP
        if hasattr(page, 'client_ip'):
            return f"ip:{page.client_ip}"
        
        # Last resort: session ID
        return f"session:{id(page)}"
    
    def _show_rate_limit_message(self, page: ft.Page, result):
        """Show rate limit message to user."""
        if hasattr(page, 'snack_bar'):
            page.snack_bar = ft.SnackBar(
                content=ft.Text(
                    f"Por favor, aguarde {result.retry_after} segundos antes de tentar novamente."
                ),
                bgcolor=ft.colors.ERROR
            )
            page.snack_bar.open = True
            page.update()


class FletAuditLogger:
    """
    Flet-specific audit logger that captures page context.
    """
    
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        """Initialize with an optional audit logger instance."""
        self.audit_logger = audit_logger or get_audit_logger()
    
    def log_action(self, page: ft.Page, action: str, resource: str = None,
                   outcome: str = 'SUCCESS', details: Dict[str, Any] = None):
        """
        Log an action with Flet page context.
        
        Args:
            page: Flet page instance
            action: Action being performed
            resource: Resource being accessed
            outcome: Action outcome (SUCCESS/FAILURE)
            details: Additional details
        """
        context = self._extract_page_context(page)
        
        # Merge with provided details
        if details:
            context.update(details)
        
        self.audit_logger.log_event(
            event_type='USER_ACTION',
            action=action,
            resource=resource,
            outcome=outcome,
            user_id=context.get('user_id'),
            details=context
        )
    
    def _extract_page_context(self, page: ft.Page) -> Dict[str, Any]:
        """Extract context information from Flet page."""
        context = {
            'route': getattr(page, 'route', '/'),
            'platform': getattr(page, 'platform', 'unknown'),
            'client_ip': getattr(page, 'client_ip', None),
            'user_agent': getattr(page, 'user_agent', None)
        }
        
        # Extract user information from session
        if hasattr(page, 'session'):
            context['user_id'] = page.session.get('user_id')
            context['user_email'] = page.session.get('user_email')
            context['user_role'] = page.session.get('user_role')
        
        return {k: v for k, v in context.items() if v is not None}


class FletSessionManager:
    """
    Flet-specific session manager that integrates with Flet's session storage.
    """
    
    def __init__(self, session_manager: Optional[SessionManager] = None):
        """Initialize with an optional session manager instance."""
        self.session_manager = session_manager or get_session_manager()
    
    def create_session(self, page: ft.Page, user_data: Dict[str, Any]) -> str:
        """
        Create a secure session for a Flet page.
        
        Args:
            page: Flet page instance
            user_data: User data to store in session
            
        Returns:
            Session ID
        """
        # Create session in backend
        session_id = self.session_manager.create_session(user_data)
        
        # Store session data in Flet page
        if not hasattr(page, 'session'):
            page.session = {}
        
        page.session.update({
            'session_id': session_id,
            'user_id': user_data.get('id'),
            'user_email': user_data.get('email'),
            'user_role': user_data.get('role'),
            'authenticated': True
        })
        
        # Set CSRF token
        csrf_token = self.session_manager.generate_csrf_token(session_id)
        page.session['csrf_token'] = csrf_token
        
        return session_id
    
    def validate_session(self, page: ft.Page) -> bool:
        """
        Validate the current session.
        
        Args:
            page: Flet page instance
            
        Returns:
            True if session is valid
        """
        if not hasattr(page, 'session') or not page.session.get('session_id'):
            return False
        
        session_id = page.session.get('session_id')
        return self.session_manager.validate_session(session_id)
    
    def destroy_session(self, page: ft.Page):
        """Destroy the current session."""
        if hasattr(page, 'session') and page.session.get('session_id'):
            session_id = page.session.get('session_id')
            self.session_manager.destroy_session(session_id)
            page.session.clear()


class FletAuthorizationMiddleware:
    """
    Flet-specific authorization middleware.
    """
    
    def __init__(self, permission_manager: Optional[PermissionManager] = None):
        """Initialize with an optional permission manager instance."""
        self.permission_manager = permission_manager or get_permission_manager()
    
    def check_permission(self, page: ft.Page, permission: str) -> bool:
        """
        Check if the current user has a permission.
        
        Args:
            page: Flet page instance
            permission: Permission to check
            
        Returns:
            True if user has permission
        """
        if not hasattr(page, 'session'):
            return False
        
        user_role = page.session.get('user_role')
        if not user_role:
            return False
        
        return self.permission_manager.has_permission(user_role, permission)
    
    def require_permission(self, permission: str):
        """
        Decorator that requires a specific permission.
        
        Args:
            permission: Required permission
        """
        def decorator(func):
            @wraps(func)
            async def async_wrapper(page: ft.Page, *args, **kwargs):
                if not self.check_permission(page, permission):
                    await self._show_unauthorized_message(page)
                    return
                return await func(page, *args, **kwargs)
            
            @wraps(func)
            def sync_wrapper(page: ft.Page, *args, **kwargs):
                if not self.check_permission(page, permission):
                    self._show_unauthorized_message_sync(page)
                    return
                return func(page, *args, **kwargs)
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
    
    async def _show_unauthorized_message(self, page: ft.Page):
        """Show unauthorized message (async)."""
        self._show_unauthorized_message_sync(page)
    
    def _show_unauthorized_message_sync(self, page: ft.Page):
        """Show unauthorized message (sync)."""
        if hasattr(page, 'snack_bar'):
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Você não tem permissão para realizar esta ação."),
                bgcolor=ft.colors.ERROR
            )
            page.snack_bar.open = True
            page.update()


def apply_security_to_page(page: ft.Page, config: Optional[Dict[str, Any]] = None):
    """
    Apply comprehensive security settings to a Flet page.
    
    Args:
        page: Flet page instance
        config: Optional security configuration
    """
    config = config or {}
    
    # Apply security headers (if supported by deployment)
    headers_manager = get_security_headers()
    headers = headers_manager.get_security_headers()
    
    # Store headers for potential server use
    if not hasattr(page, '_security_headers'):
        page._security_headers = headers
    
    # Initialize security managers on the page
    if not hasattr(page, '_security'):
        page._security = {
            'rate_limiter': FletRateLimiter(),
            'audit_logger': FletAuditLogger(),
            'session_manager': FletSessionManager(),
            'auth_middleware': FletAuthorizationMiddleware()
        }
    
    # Set secure page properties
    page.title = config.get('title', 'Secure Application')
    
    # Log page access
    page._security['audit_logger'].log_action(
        page, 'PAGE_ACCESS', page.route
    )
    
    logger.info(f"Security applied to Flet page: {page.route}")


def setup_page_security(
    require_auth: bool = True,
    required_permissions: Optional[List[str]] = None,
    rate_limit_config: Optional[Dict[str, Any]] = None
):
    """
    Decorator to setup security for a Flet page/view function.
    
    Args:
        require_auth: Whether authentication is required
        required_permissions: List of required permissions
        rate_limit_config: Rate limiting configuration
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(page: ft.Page, *args, **kwargs):
            # Apply security settings
            apply_security_to_page(page)
            
            # Check authentication
            if require_auth:
                session_mgr = page._security['session_manager']
                if not session_mgr.validate_session(page):
                    page.go('/login')
                    return
            
            # Check permissions
            if required_permissions:
                auth_middleware = page._security['auth_middleware']
                for permission in required_permissions:
                    if not auth_middleware.check_permission(page, permission):
                        await auth_middleware._show_unauthorized_message(page)
                        return
            
            # Apply rate limiting
            if rate_limit_config:
                rate_limiter = page._security['rate_limiter']
                action = rate_limit_config.get('action', 'page_access')
                limit = rate_limit_config.get('limit', 100)
                window = rate_limit_config.get('window', 60)
                
                if not rate_limiter.check_rate_limit(page, action, limit, window):
                    return
            
            # Call the original function
            return await func(page, *args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(page: ft.Page, *args, **kwargs):
            # Apply security settings
            apply_security_to_page(page)
            
            # Check authentication
            if require_auth:
                session_mgr = page._security['session_manager']
                if not session_mgr.validate_session(page):
                    page.go('/login')
                    return
            
            # Check permissions
            if required_permissions:
                auth_middleware = page._security['auth_middleware']
                for permission in required_permissions:
                    if not auth_middleware.check_permission(page, permission):
                        auth_middleware._show_unauthorized_message_sync(page)
                        return
            
            # Apply rate limiting
            if rate_limit_config:
                rate_limiter = page._security['rate_limiter']
                action = rate_limit_config.get('action', 'page_access')
                limit = rate_limit_config.get('limit', 100)
                window = rate_limit_config.get('window', 60)
                
                if not rate_limiter.check_rate_limit(page, action, limit, window):
                    return
            
            # Call the original function
            return func(page, *args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator