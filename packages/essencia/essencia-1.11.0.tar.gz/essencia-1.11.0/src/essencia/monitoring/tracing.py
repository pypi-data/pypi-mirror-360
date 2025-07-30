"""
OpenTelemetry tracing for distributed tracing support.
"""
import functools
from typing import Dict, Any, Optional, Callable, Union
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.zipkin.json import ZipkinExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.trace import Status, StatusCode
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.pymongo import PyMongoInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor


class TracingProvider:
    """OpenTelemetry tracing provider for Essencia applications."""
    
    def __init__(
        self,
        service_name: str = "essencia",
        service_version: str = "1.0.0",
        exporter_type: str = "console",
        endpoint: Optional[str] = None
    ):
        self.service_name = service_name
        self.service_version = service_version
        
        # Create resource
        resource = Resource.create({
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            "environment": "production",
            "language": "python"
        })
        
        # Setup tracer provider
        self.provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(self.provider)
        
        # Setup exporter
        self._setup_exporter(exporter_type, endpoint)
        
        # Get tracer
        self.tracer = trace.get_tracer(service_name, service_version)
        
        # Auto-instrument common libraries
        self._setup_auto_instrumentation()
    
    def _setup_exporter(self, exporter_type: str, endpoint: Optional[str]):
        """Setup trace exporter based on type."""
        if exporter_type == "console":
            exporter = ConsoleSpanExporter()
        elif exporter_type == "otlp":
            exporter = OTLPSpanExporter(
                endpoint=endpoint or "localhost:4317",
                insecure=True
            )
        elif exporter_type == "jaeger":
            exporter = JaegerExporter(
                agent_host_name=endpoint or "localhost",
                agent_port=6831
            )
        elif exporter_type == "zipkin":
            exporter = ZipkinExporter(
                endpoint=endpoint or "http://localhost:9411/api/v2/spans"
            )
        else:
            raise ValueError(f"Unknown exporter type: {exporter_type}")
        
        # Add span processor
        span_processor = BatchSpanProcessor(exporter)
        self.provider.add_span_processor(span_processor)
    
    def _setup_auto_instrumentation(self):
        """Setup automatic instrumentation for common libraries."""
        # Instrument HTTP requests
        RequestsInstrumentor().instrument()
        
        # Instrument MongoDB
        PyMongoInstrumentor().instrument()
        
        # Instrument Redis
        RedisInstrumentor().instrument()
    
    def create_span(self, name: str, kind: trace.SpanKind = trace.SpanKind.INTERNAL) -> trace.Span:
        """Create a new span."""
        return self.tracer.start_span(name, kind=kind)
    
    @contextmanager
    def span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Context manager for creating spans."""
        with self.tracer.start_as_current_span(name) as span:
            if attributes:
                span.set_attributes(attributes)
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                raise


# Global tracing provider instance
_tracing_provider: Optional[TracingProvider] = None


def init_tracing(
    service_name: str = "essencia",
    service_version: str = "1.0.0",
    exporter_type: str = "console",
    endpoint: Optional[str] = None
) -> TracingProvider:
    """Initialize global tracing provider."""
    global _tracing_provider
    _tracing_provider = TracingProvider(service_name, service_version, exporter_type, endpoint)
    return _tracing_provider


def get_tracer() -> trace.Tracer:
    """Get the current tracer."""
    if _tracing_provider:
        return _tracing_provider.tracer
    return trace.get_tracer("essencia")


@contextmanager
def create_span(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Create a new span with context manager."""
    tracer = get_tracer()
    with tracer.start_as_current_span(name) as span:
        if attributes:
            span.set_attributes(attributes)
        try:
            yield span
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            raise


def get_current_span() -> Optional[trace.Span]:
    """Get the current active span."""
    return trace.get_current_span()


def set_span_attributes(attributes: Dict[str, Any]):
    """Set attributes on the current span."""
    span = get_current_span()
    if span:
        span.set_attributes(attributes)


def record_exception(exception: Exception):
    """Record an exception in the current span."""
    span = get_current_span()
    if span:
        span.record_exception(exception)
        span.set_status(Status(StatusCode.ERROR, str(exception)))


# Decorators for tracing
def trace_async(name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None):
    """Decorator for tracing async functions."""
    def decorator(func: Callable) -> Callable:
        span_name = name or f"{func.__module__}.{func.__name__}"
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            with create_span(span_name, attributes) as span:
                # Add function arguments as span attributes
                span.set_attribute("function.args", str(args))
                span.set_attribute("function.kwargs", str(kwargs))
                
                result = await func(*args, **kwargs)
                
                # Add result info
                span.set_attribute("function.result_type", type(result).__name__)
                
                return result
        
        return wrapper
    return decorator


def trace_sync(name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None):
    """Decorator for tracing sync functions."""
    def decorator(func: Callable) -> Callable:
        span_name = name or f"{func.__module__}.{func.__name__}"
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with create_span(span_name, attributes) as span:
                # Add function arguments as span attributes
                span.set_attribute("function.args", str(args))
                span.set_attribute("function.kwargs", str(kwargs))
                
                result = func(*args, **kwargs)
                
                # Add result info
                span.set_attribute("function.result_type", type(result).__name__)
                
                return result
        
        return wrapper
    return decorator


# MongoDB tracing helpers
def trace_mongodb_operation(operation: str, collection: str, filter_query: Optional[Dict] = None):
    """Add MongoDB operation details to current span."""
    span = get_current_span()
    if span:
        span.set_attributes({
            "db.system": "mongodb",
            "db.operation": operation,
            "db.mongodb.collection": collection,
            "db.statement": str(filter_query) if filter_query else None
        })


# HTTP tracing helpers
def trace_http_request(method: str, url: str, status_code: Optional[int] = None):
    """Add HTTP request details to current span."""
    span = get_current_span()
    if span:
        attributes = {
            "http.method": method,
            "http.url": url,
            "http.scheme": url.split("://")[0] if "://" in url else "http"
        }
        if status_code:
            attributes["http.status_code"] = status_code
        span.set_attributes(attributes)


# Cache tracing helpers
def trace_cache_operation(operation: str, key: str, hit: bool):
    """Add cache operation details to current span."""
    span = get_current_span()
    if span:
        span.set_attributes({
            "cache.operation": operation,
            "cache.key": key,
            "cache.hit": hit
        })


# FastAPI integration
def setup_fastapi_tracing(app):
    """Setup OpenTelemetry tracing for FastAPI."""
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    
    FastAPIInstrumentor.instrument_app(app)


# Flask integration
def setup_flask_tracing(app):
    """Setup OpenTelemetry tracing for Flask."""
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    
    FlaskInstrumentor().instrument_app(app)