"""
Middleware components for FastAPI integration.
"""

import time
import logging
from typing import Callable, Optional, Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, Response
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..middleware.rate_limiter import RateLimiter
from ..security.audit import AuditLogger


logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request details and response status."""
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response: {response.status_code} for {request.method} "
            f"{request.url.path} ({duration:.3f}s)"
        )
        
        # Add custom headers
        response.headers["X-Process-Time"] = str(duration)
        
        return response


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Security-focused middleware with various protections.
    """
    
    def __init__(self, app: ASGIApp, **options):
        super().__init__(app)
        self.options = options
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # CSP header (configurable)
        if csp := self.options.get("content_security_policy"):
            response.headers["Content-Security-Policy"] = csp
        
        # HSTS header (configurable)
        if self.options.get("enable_hsts", True):
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using essencia's RateLimiter.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        calls: int = 100,
        period: int = 60,
        identifier: Optional[Callable[[Request], str]] = None
    ):
        super().__init__(app)
        self.rate_limiter = RateLimiter(max_calls=calls, time_window=period)
        self.identifier = identifier or self._default_identifier
        
    def _default_identifier(self, request: Request) -> str:
        """Default client identifier based on IP."""
        if request.client:
            return f"ip:{request.client.host}"
        return "anonymous"
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit before processing request."""
        client_id = self.identifier(request)
        
        # Check rate limit
        allowed, retry_after = await self.rate_limiter.check_rate_limit(client_id)
        
        if not allowed:
            return Response(
                content="Rate limit exceeded",
                status_code=429,
                headers={"Retry-After": str(retry_after)}
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.max_calls)
        response.headers["X-RateLimit-Window"] = str(self.rate_limiter.time_window)
        
        return response


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Audit logging middleware for tracking API access.
    """
    
    def __init__(self, app: ASGIApp, audit_logger: Optional[AuditLogger] = None):
        super().__init__(app)
        self.audit_logger = audit_logger or AuditLogger()
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log API access for audit trail."""
        start_time = time.time()
        
        # Get user info from request (if authenticated)
        user_id = None
        if hasattr(request.state, "user") and request.state.user:
            user_id = str(request.state.user.id)
        
        # Process request
        response = await call_next(request)
        
        # Log audit event
        duration = time.time() - start_time
        
        await self.audit_logger.log_event(
            event_type="API_ACCESS",
            user_id=user_id,
            resource=f"{request.method} {request.url.path}",
            details={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        return response


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Performance monitoring middleware.
    """
    
    def __init__(self, app: ASGIApp, slow_request_threshold: float = 1.0):
        super().__init__(app)
        self.slow_request_threshold = slow_request_threshold
        self.metrics: Dict[str, list] = defaultdict(list)
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Monitor request performance."""
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate metrics
        duration = time.time() - start_time
        endpoint = f"{request.method} {request.url.path}"
        
        # Store metrics
        self.metrics[endpoint].append({
            "duration": duration,
            "timestamp": datetime.utcnow(),
            "status_code": response.status_code
        })
        
        # Log slow requests
        if duration > self.slow_request_threshold:
            logger.warning(
                f"Slow request detected: {endpoint} took {duration:.3f}s"
            )
        
        return response
    
    def get_metrics(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics."""
        if endpoint:
            data = self.metrics.get(endpoint, [])
            if not data:
                return {}
            
            durations = [m["duration"] for m in data]
            return {
                "endpoint": endpoint,
                "count": len(data),
                "avg_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
            }
        
        # Return all metrics
        return {
            ep: self.get_metrics(ep) for ep in self.metrics
        }


def setup_middleware(app: FastAPI, config: Any) -> None:
    """
    Setup all middleware for the FastAPI application.
    
    Args:
        app: FastAPI application instance
        config: Application configuration
    """
    # Add custom middleware from config
    for middleware_class, options in config.middleware:
        app.add_middleware(middleware_class, **options)
    
    # Add standard middleware if enabled
    if getattr(config.api_settings, "enable_logging", True):
        app.add_middleware(LoggingMiddleware)
    
    if getattr(config.api_settings, "enable_security", True):
        app.add_middleware(SecurityMiddleware)
    
    if config.api_settings.rate_limit_enabled:
        app.add_middleware(
            RateLimitMiddleware,
            calls=config.api_settings.rate_limit_calls,
            period=config.api_settings.rate_limit_period
        )
    
    # Trusted host middleware (optional)
    if allowed_hosts := getattr(config.api_settings, "allowed_hosts", None):
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=allowed_hosts
        )