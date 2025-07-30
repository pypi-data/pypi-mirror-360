"""
Essencia Middleware Module - Cross-cutting concerns for applications.

Provides middleware components for:
- Request/response processing
- Monitoring and observability
- Performance optimization
- Error handling
- Logging and tracing
"""

from .base import (
    Middleware,
    MiddlewareChain,
    Request,
    Response,
    MiddlewareConfig,
)

from .monitoring import (
    MetricsMiddleware,
    TracingMiddleware,
    LoggingMiddleware,
    HealthCheckMiddleware,
    PerformanceMiddleware,
)

from .security import (
    AuthenticationMiddleware,
    AuthorizationMiddleware,
    CSRFMiddleware,
    CORSMiddleware,
    SecurityHeadersMiddleware,
)

from .optimization import (
    CacheMiddleware,
    CompressionMiddleware,
    RateLimitMiddleware,
    CircuitBreakerMiddleware,
    RetryMiddleware,
)

from .error_handling import (
    ErrorHandlerMiddleware,
    ValidationMiddleware,
    SanitizationMiddleware,
    ExceptionMapperMiddleware,
)

__all__ = [
    # Base
    'Middleware',
    'MiddlewareChain',
    'Request',
    'Response',
    'MiddlewareConfig',
    
    # Monitoring
    'MetricsMiddleware',
    'TracingMiddleware',
    'LoggingMiddleware',
    'HealthCheckMiddleware',
    'PerformanceMiddleware',
    
    # Security
    'AuthenticationMiddleware',
    'AuthorizationMiddleware',
    'CSRFMiddleware',
    'CORSMiddleware',
    'SecurityHeadersMiddleware',
    
    # Optimization
    'CacheMiddleware',
    'CompressionMiddleware',
    'RateLimitMiddleware',
    'CircuitBreakerMiddleware',
    'RetryMiddleware',
    
    # Error Handling
    'ErrorHandlerMiddleware',
    'ValidationMiddleware',
    'SanitizationMiddleware',
    'ExceptionMapperMiddleware',
]