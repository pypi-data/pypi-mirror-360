"""
Security middleware for protection and access control.
"""

import re
from typing import Dict, List, Optional, Set, Pattern
from datetime import datetime

from .base import BaseMiddleware, Request, Response, MiddlewareConfig
from ..security import (
    validate_current_session,
    get_csrf_token,
    validate_csrf,
    get_permission_manager,
    SecurityHeaders,
)


class AuthenticationMiddleware(BaseMiddleware):
    """
    Middleware for authentication.
    """
    
    def __init__(
        self,
        public_paths: Optional[List[str]] = None,
        login_path: str = "/login",
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.public_paths = set(public_paths or ['/login', '/health', '/ready'])
        self.login_path = login_path
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Check authentication."""
        # Skip auth for public paths
        if request.path in self.public_paths:
            return None
            
        # Check if user is authenticated
        if not request.is_authenticated:
            return Response(
                status_code=401,
                body={'error': 'Authentication required'},
                headers={'Location': self.login_path}
            )
            
        # Validate session if available
        if request.session and not self._validate_session(request):
            return Response(
                status_code=401,
                body={'error': 'Invalid or expired session'},
                headers={'Location': self.login_path}
            )
            
        return None
        
    def _validate_session(self, request: Request) -> bool:
        """Validate user session."""
        # This would integrate with session management
        # For now, basic check
        if 'session_id' not in request.session:
            return False
            
        # Check session expiry
        expires_at = request.session.get('expires_at')
        if expires_at and datetime.fromisoformat(expires_at) < datetime.utcnow():
            return False
            
        return True


class AuthorizationMiddleware(BaseMiddleware):
    """
    Middleware for role-based authorization.
    """
    
    def __init__(
        self,
        role_paths: Optional[Dict[str, List[str]]] = None,
        permission_paths: Optional[Dict[str, List[str]]] = None,
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.role_paths = role_paths or {}
        self.permission_paths = permission_paths or {}
        self.permission_manager = None
        
    async def initialize(self) -> None:
        """Initialize permission manager."""
        await super().initialize()
        self.permission_manager = get_permission_manager()
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Check authorization."""
        if not request.user:
            return None  # Let authentication middleware handle
            
        user_role = request.user.get('role')
        user_permissions = request.user.get('permissions', [])
        
        # Check role-based access
        for role, paths in self.role_paths.items():
            if self._matches_path(request.path, paths):
                if user_role != role:
                    return self._forbidden_response(f"Role '{role}' required")
                    
        # Check permission-based access
        for permission, paths in self.permission_paths.items():
            if self._matches_path(request.path, paths):
                if permission not in user_permissions:
                    if self.permission_manager:
                        # Check if role has permission
                        if not self.permission_manager.role_has_permission(user_role, permission):
                            return self._forbidden_response(f"Permission '{permission}' required")
                    else:
                        return self._forbidden_response(f"Permission '{permission}' required")
                        
        return None
        
    def _matches_path(self, request_path: str, patterns: List[str]) -> bool:
        """Check if request path matches any pattern."""
        for pattern in patterns:
            if pattern.endswith('*'):
                # Prefix match
                if request_path.startswith(pattern[:-1]):
                    return True
            else:
                # Exact match
                if request_path == pattern:
                    return True
        return False
        
    def _forbidden_response(self, reason: str) -> Response:
        """Create forbidden response."""
        return Response(
            status_code=403,
            body={'error': 'Forbidden', 'reason': reason}
        )


class CSRFMiddleware(BaseMiddleware):
    """
    Middleware for CSRF protection.
    """
    
    def __init__(
        self,
        safe_methods: Optional[Set[str]] = None,
        excluded_paths: Optional[List[str]] = None,
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.safe_methods = safe_methods or {'GET', 'HEAD', 'OPTIONS'}
        self.excluded_paths = set(excluded_paths or ['/api/*'])
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Validate CSRF token for unsafe methods."""
        # Skip for safe methods
        if request.method.value in self.safe_methods:
            return None
            
        # Skip for excluded paths
        if self._is_excluded(request.path):
            return None
            
        # Get CSRF token from request
        csrf_token = None
        
        # Check header first
        csrf_token = request.get_header('X-CSRF-Token')
        
        # Check form data
        if not csrf_token and isinstance(request.body, dict):
            csrf_token = request.body.get('csrf_token')
            
        # Validate token
        if not csrf_token or not self._validate_csrf_token(request, csrf_token):
            return Response(
                status_code=403,
                body={'error': 'Invalid CSRF token'}
            )
            
        return None
        
    async def process_response(self, request: Request, response: Response) -> Response:
        """Add CSRF token to response if needed."""
        if request.method.value == 'GET' and response.is_success:
            # Generate new token for forms
            if hasattr(request, 'page'):
                token = get_csrf_token(request.page)
                response.metadata['csrf_token'] = token
                
        return response
        
    def _is_excluded(self, path: str) -> bool:
        """Check if path is excluded from CSRF protection."""
        for pattern in self.excluded_paths:
            if pattern.endswith('*') and path.startswith(pattern[:-1]):
                return True
            elif path == pattern:
                return True
        return False
        
    def _validate_csrf_token(self, request: Request, token: str) -> bool:
        """Validate CSRF token."""
        if hasattr(request, 'page'):
            return validate_csrf(request.page, token)
        # Fallback validation
        expected = request.session.get('csrf_token') if request.session else None
        return expected and token == expected


class CORSMiddleware(BaseMiddleware):
    """
    Middleware for Cross-Origin Resource Sharing (CORS).
    """
    
    def __init__(
        self,
        allowed_origins: Optional[List[str]] = None,
        allowed_methods: Optional[List[str]] = None,
        allowed_headers: Optional[List[str]] = None,
        expose_headers: Optional[List[str]] = None,
        max_age: int = 86400,
        allow_credentials: bool = True,
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.allowed_origins = allowed_origins or ['*']
        self.allowed_methods = allowed_methods or ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
        self.allowed_headers = allowed_headers or ['Content-Type', 'Authorization', 'X-CSRF-Token']
        self.expose_headers = expose_headers or []
        self.max_age = max_age
        self.allow_credentials = allow_credentials
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Handle preflight requests."""
        if request.method.value == 'OPTIONS':
            # Handle preflight
            return Response(
                status_code=200,
                headers=self._get_cors_headers(request)
            )
        return None
        
    async def process_response(self, request: Request, response: Response) -> Response:
        """Add CORS headers to response."""
        cors_headers = self._get_cors_headers(request)
        for header, value in cors_headers.items():
            response.set_header(header, value)
        return response
        
    def _get_cors_headers(self, request: Request) -> Dict[str, str]:
        """Get CORS headers based on request."""
        headers = {}
        
        # Origin
        origin = request.get_header('Origin')
        if origin:
            if '*' in self.allowed_origins:
                headers['Access-Control-Allow-Origin'] = origin
            elif origin in self.allowed_origins:
                headers['Access-Control-Allow-Origin'] = origin
            else:
                # Origin not allowed
                return {}
                
        # Methods
        headers['Access-Control-Allow-Methods'] = ', '.join(self.allowed_methods)
        
        # Headers
        headers['Access-Control-Allow-Headers'] = ', '.join(self.allowed_headers)
        
        # Expose headers
        if self.expose_headers:
            headers['Access-Control-Expose-Headers'] = ', '.join(self.expose_headers)
            
        # Max age
        headers['Access-Control-Max-Age'] = str(self.max_age)
        
        # Credentials
        if self.allow_credentials:
            headers['Access-Control-Allow-Credentials'] = 'true'
            
        return headers


class SecurityHeadersMiddleware(BaseMiddleware):
    """
    Middleware for security headers.
    """
    
    def __init__(
        self,
        use_medical_headers: bool = False,
        custom_headers: Optional[Dict[str, str]] = None,
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.use_medical_headers = use_medical_headers
        self.custom_headers = custom_headers or {}
        
    async def process_response(self, request: Request, response: Response) -> Response:
        """Add security headers to response."""
        # Get appropriate headers
        if self.use_medical_headers:
            headers = SecurityHeaders.get_medical_headers()
        else:
            headers = SecurityHeaders.get_default_headers()
            
        # Add custom headers
        headers.update(self.custom_headers)
        
        # Apply headers
        for header, value in headers.items():
            response.set_header(header, value)
            
        return response