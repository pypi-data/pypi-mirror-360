"""
Error handling middleware for robust applications.
"""

import traceback
import re
from typing import Dict, Optional, Any, List, Type, Callable
from datetime import datetime

from .base import BaseMiddleware, Request, Response, MiddlewareConfig
from ..security import HTMLSanitizer


class ErrorHandlerMiddleware(BaseMiddleware):
    """
    Middleware for comprehensive error handling.
    """
    
    def __init__(
        self,
        debug: bool = False,
        error_handlers: Optional[Dict[Type[Exception], Callable]] = None,
        default_error_message: str = "An error occurred",
        include_stack_trace: bool = False,
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.debug = debug
        self.error_handlers = error_handlers or {}
        self.default_error_message = default_error_message
        self.include_stack_trace = include_stack_trace or debug
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Wrap request processing in error handling."""
        # Store original process method
        request.metadata['error_handler'] = self
        return None
        
    def handle_error(self, error: Exception, request: Request) -> Response:
        """Handle an error and return appropriate response."""
        # Check for specific handler
        for error_type, handler in self.error_handlers.items():
            if isinstance(error, error_type):
                return handler(error, request)
                
        # Default error handling
        error_id = f"ERR-{datetime.utcnow().timestamp()}"
        
        # Log the error
        self.logger.error(
            f"Error {error_id} processing request",
            exc_info=True,
            extra={
                'error_id': error_id,
                'path': request.path,
                'method': request.method.value,
                'user_id': request.user.get('id') if request.user else None
            }
        )
        
        # Build error response
        if self.debug:
            body = {
                'error': str(error),
                'error_type': type(error).__name__,
                'error_id': error_id,
                'path': request.path,
                'method': request.method.value
            }
            
            if self.include_stack_trace:
                body['stack_trace'] = traceback.format_exc().split('\n')
        else:
            body = {
                'error': self.default_error_message,
                'error_id': error_id
            }
            
        # Determine status code
        status_code = getattr(error, 'status_code', 500)
        
        return Response(
            status_code=status_code,
            body=body,
            headers={'X-Error-ID': error_id}
        )


class ValidationMiddleware(BaseMiddleware):
    """
    Middleware for input validation.
    """
    
    def __init__(
        self,
        max_body_size: int = 1024 * 1024,  # 1MB
        allowed_content_types: Optional[List[str]] = None,
        validate_json: bool = True,
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.max_body_size = max_body_size
        self.allowed_content_types = allowed_content_types or [
            'application/json',
            'application/x-www-form-urlencoded',
            'multipart/form-data',
            'text/plain'
        ]
        self.validate_json = validate_json
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Validate request input."""
        # Check content type
        content_type = request.get_header('Content-Type', '')
        if content_type:
            mime_type = content_type.split(';')[0].strip()
            if mime_type not in self.allowed_content_types:
                return Response(
                    status_code=415,
                    body={'error': f'Unsupported content type: {mime_type}'}
                )
                
        # Check body size
        if request.body:
            if isinstance(request.body, str):
                size = len(request.body.encode('utf-8'))
            elif isinstance(request.body, bytes):
                size = len(request.body)
            else:
                # Estimate size for other types
                size = len(str(request.body))
                
            if size > self.max_body_size:
                return Response(
                    status_code=413,
                    body={'error': 'Request body too large'}
                )
                
        # Validate JSON if applicable
        if self.validate_json and 'application/json' in content_type:
            if not isinstance(request.body, (dict, list)):
                return Response(
                    status_code=400,
                    body={'error': 'Invalid JSON in request body'}
                )
                
        return None


class SanitizationMiddleware(BaseMiddleware):
    """
    Middleware for input sanitization.
    """
    
    def __init__(
        self,
        sanitize_html: bool = True,
        sanitize_sql: bool = True,
        strip_null_bytes: bool = True,
        max_field_length: int = 10000,
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.sanitize_html = sanitize_html
        self.sanitize_sql = sanitize_sql
        self.strip_null_bytes = strip_null_bytes
        self.max_field_length = max_field_length
        self.html_sanitizer = HTMLSanitizer() if sanitize_html else None
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Sanitize request input."""
        # Sanitize query params
        if request.query_params:
            request.query_params = self._sanitize_dict(request.query_params)
            
        # Sanitize body
        if request.body:
            if isinstance(request.body, dict):
                request.body = self._sanitize_dict(request.body)
            elif isinstance(request.body, list):
                request.body = self._sanitize_list(request.body)
            elif isinstance(request.body, str):
                request.body = self._sanitize_string(request.body)
                
        return None
        
    def _sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize dictionary values."""
        sanitized = {}
        for key, value in data.items():
            # Sanitize key
            key = self._sanitize_string(key)
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[key] = self._sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = self._sanitize_list(value)
            else:
                sanitized[key] = value
                
        return sanitized
        
    def _sanitize_list(self, data: List[Any]) -> List[Any]:
        """Sanitize list values."""
        sanitized = []
        for item in data:
            if isinstance(item, str):
                sanitized.append(self._sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(self._sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(self._sanitize_list(item))
            else:
                sanitized.append(item)
        return sanitized
        
    def _sanitize_string(self, value: str) -> str:
        """Sanitize string value."""
        if not value:
            return value
            
        # Length check
        if len(value) > self.max_field_length:
            value = value[:self.max_field_length]
            
        # Strip null bytes
        if self.strip_null_bytes:
            value = value.replace('\x00', '')
            
        # HTML sanitization
        if self.sanitize_html and self.html_sanitizer:
            value = self.html_sanitizer.sanitize(value)
            
        # SQL injection prevention (basic)
        if self.sanitize_sql:
            # Remove common SQL injection patterns
            sql_patterns = [
                r'(\b(union|select|insert|update|delete|drop|create)\b)',
                r'(--|#|/\*|\*/)',
                r'(\bor\b.*=.*)',
                r'(\band\b.*=.*)'
            ]
            for pattern in sql_patterns:
                value = re.sub(pattern, '', value, flags=re.IGNORECASE)
                
        return value.strip()


class ExceptionMapperMiddleware(BaseMiddleware):
    """
    Middleware for mapping exceptions to HTTP responses.
    """
    
    def __init__(
        self,
        exception_mappings: Optional[Dict[Type[Exception], int]] = None,
        include_message: bool = True,
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.exception_mappings = exception_mappings or {
            ValueError: 400,
            KeyError: 400,
            TypeError: 400,
            PermissionError: 403,
            FileNotFoundError: 404,
            NotImplementedError: 501,
            TimeoutError: 504,
        }
        self.include_message = include_message
        
    def map_exception(self, error: Exception) -> tuple[int, str]:
        """Map exception to status code and message."""
        # Check direct mapping
        status_code = self.exception_mappings.get(type(error))
        
        if not status_code:
            # Check inheritance
            for exc_type, code in self.exception_mappings.items():
                if isinstance(error, exc_type):
                    status_code = code
                    break
                    
        if not status_code:
            # Default to 500
            status_code = 500
            
        # Get message
        if self.include_message:
            message = str(error)
        else:
            # Generic messages based on status code
            messages = {
                400: "Bad Request",
                401: "Unauthorized",
                403: "Forbidden",
                404: "Not Found",
                405: "Method Not Allowed",
                409: "Conflict",
                410: "Gone",
                422: "Unprocessable Entity",
                429: "Too Many Requests",
                500: "Internal Server Error",
                501: "Not Implemented",
                502: "Bad Gateway",
                503: "Service Unavailable",
                504: "Gateway Timeout"
            }
            message = messages.get(status_code, "Error")
            
        return status_code, message