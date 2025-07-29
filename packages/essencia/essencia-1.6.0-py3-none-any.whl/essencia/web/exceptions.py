"""
Exception handling for FastAPI applications.
"""

from typing import Any, Dict, Optional, Callable, List
import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from ..exceptions import (
    EssenciaException,
    ValidationException as EssenciaValidationException,
    AuthenticationException as EssenciaAuthException,
    AuthorizationException as EssenciaAuthzException,
    DatabaseException,
    CacheException,
)


logger = logging.getLogger(__name__)


class HTTPException(StarletteHTTPException):
    """Enhanced HTTP exception with extra details."""
    
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
        error_code: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code, detail, headers)
        self.error_code = error_code
        self.extra = extra or {}


class ValidationException(HTTPException):
    """Validation error exception."""
    
    def __init__(self, detail: Any, error_code: str = "VALIDATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code=error_code
        )


class AuthenticationException(HTTPException):
    """Authentication error exception."""
    
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTHENTICATION_ERROR",
            headers={"WWW-Authenticate": "Bearer"}
        )


class PermissionException(HTTPException):
    """Permission denied exception."""
    
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="PERMISSION_DENIED"
        )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTPException instances.
    
    Args:
        request: FastAPI request
        exc: HTTPException instance
        
    Returns:
        JSON response with error details
    """
    content = {
        "error": True,
        "message": exc.detail,
        "status_code": exc.status_code,
    }
    
    if exc.error_code:
        content["error_code"] = exc.error_code
        
    if exc.extra:
        content["extra"] = exc.extra
    
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=exc.headers
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    Args:
        request: FastAPI request
        exc: RequestValidationError instance
        
    Returns:
        JSON response with validation errors
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "errors": errors
        }
    )


async def essencia_exception_handler(
    request: Request,
    exc: EssenciaException
) -> JSONResponse:
    """
    Handle Essencia framework exceptions.
    
    Args:
        request: FastAPI request
        exc: EssenciaException instance
        
    Returns:
        JSON response with error details
    """
    # Map Essencia exceptions to HTTP status codes
    status_code_map = {
        EssenciaValidationException: status.HTTP_422_UNPROCESSABLE_ENTITY,
        EssenciaAuthException: status.HTTP_401_UNAUTHORIZED,
        EssenciaAuthzException: status.HTTP_403_FORBIDDEN,
        DatabaseException: status.HTTP_500_INTERNAL_SERVER_ERROR,
        CacheException: status.HTTP_503_SERVICE_UNAVAILABLE,
    }
    
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    for exc_type, code in status_code_map.items():
        if isinstance(exc, exc_type):
            status_code = code
            break
    
    # Log the error
    logger.error(f"Essencia exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": True,
            "message": str(exc),
            "error_code": exc.__class__.__name__.upper(),
            "type": "essencia_error"
        }
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Handle generic exceptions.
    
    Args:
        request: FastAPI request
        exc: Exception instance
        
    Returns:
        JSON response with error details
    """
    # Log the error
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    # Don't expose internal errors in production
    message = "Internal server error"
    if hasattr(request.app.state, "config") and request.app.state.config:
        if getattr(request.app.state.config.api_settings, "debug", False):
            message = str(exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": message,
            "error_code": "INTERNAL_ERROR",
            "type": "internal_error"
        }
    )


def setup_exception_handlers(
    app: FastAPI,
    custom_handlers: Optional[Dict[int, Callable]] = None
) -> None:
    """
    Setup exception handlers for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        custom_handlers: Additional custom exception handlers
    """
    # Add standard exception handlers
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(EssenciaException, essencia_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
    
    # Add custom handlers
    if custom_handlers:
        for exc_type, handler in custom_handlers.items():
            app.add_exception_handler(exc_type, handler)


# Error response models for OpenAPI documentation
class ErrorResponse:
    """Standard error response model."""
    
    def __init__(
        self,
        error: bool = True,
        message: str = "",
        error_code: Optional[str] = None,
        status_code: Optional[int] = None,
        extra: Optional[Dict[str, Any]] = None
    ):
        self.error = error
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.extra = extra


class ValidationErrorResponse(ErrorResponse):
    """Validation error response model."""
    
    def __init__(self, errors: List[Dict[str, str]], **kwargs):
        super().__init__(
            message="Validation error",
            error_code="VALIDATION_ERROR",
            **kwargs
        )
        self.errors = errors