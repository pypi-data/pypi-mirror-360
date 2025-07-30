"""
Monitoring module for Essencia framework.

Provides comprehensive monitoring with Prometheus metrics and OpenTelemetry tracing.
"""
from .metrics import (
    MetricsCollector,
    Counter,
    Gauge,
    Histogram,
    Summary,
    track_request,
    track_database_operation,
    track_cache_operation
)
from .tracing import (
    TracingProvider,
    create_span,
    trace_async,
    trace_sync,
    get_current_span,
    set_span_attributes
)
from .health import (
    HealthCheck,
    HealthStatus,
    ComponentHealth,
    register_health_check,
    get_health_status
)

__all__ = [
    # Metrics
    "MetricsCollector",
    "Counter",
    "Gauge", 
    "Histogram",
    "Summary",
    "track_request",
    "track_database_operation",
    "track_cache_operation",
    # Tracing
    "TracingProvider",
    "create_span",
    "trace_async",
    "trace_sync",
    "get_current_span",
    "set_span_attributes",
    # Health
    "HealthCheck",
    "HealthStatus",
    "ComponentHealth",
    "register_health_check",
    "get_health_status"
]