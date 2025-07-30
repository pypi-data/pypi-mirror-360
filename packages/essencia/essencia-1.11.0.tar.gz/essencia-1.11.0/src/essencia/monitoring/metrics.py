"""
Prometheus metrics collection for Essencia applications.
"""
import time
import functools
from typing import Dict, Any, Optional, Callable, List
from contextlib import contextmanager
from prometheus_client import (
    Counter as PrometheusCounter,
    Gauge as PrometheusGauge,
    Histogram as PrometheusHistogram,
    Summary as PrometheusSummary,
    CollectorRegistry,
    generate_latest,
    push_to_gateway,
    CONTENT_TYPE_LATEST
)


class MetricsCollector:
    """Central metrics collector for the application."""
    
    def __init__(self, app_name: str = "essencia", registry: Optional[CollectorRegistry] = None):
        self.app_name = app_name
        self.registry = registry or CollectorRegistry()
        self._metrics: Dict[str, Any] = {}
        
        # Initialize default metrics
        self._init_default_metrics()
    
    def _init_default_metrics(self):
        """Initialize default application metrics."""
        # Request metrics
        self.request_count = self.counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"]
        )
        
        self.request_duration = self.histogram(
            "http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["method", "endpoint"]
        )
        
        # Database metrics
        self.db_query_count = self.counter(
            "database_queries_total",
            "Total database queries",
            ["operation", "collection", "status"]
        )
        
        self.db_query_duration = self.histogram(
            "database_query_duration_seconds",
            "Database query duration in seconds",
            ["operation", "collection"]
        )
        
        # Cache metrics
        self.cache_hits = self.counter(
            "cache_hits_total",
            "Total cache hits",
            ["cache_name"]
        )
        
        self.cache_misses = self.counter(
            "cache_misses_total",
            "Total cache misses",
            ["cache_name"]
        )
        
        # Business metrics
        self.active_users = self.gauge(
            "active_users",
            "Number of active users"
        )
        
        self.appointments_created = self.counter(
            "appointments_created_total",
            "Total appointments created",
            ["appointment_type"]
        )
        
        self.prescriptions_issued = self.counter(
            "prescriptions_issued_total",
            "Total prescriptions issued",
            ["medication_type"]
        )
        
        # System metrics
        self.error_count = self.counter(
            "errors_total",
            "Total errors",
            ["error_type", "component"]
        )
        
        self.queue_size = self.gauge(
            "queue_size",
            "Current queue size",
            ["queue_name"]
        )
    
    def counter(self, name: str, description: str, labels: Optional[List[str]] = None) -> PrometheusCounter:
        """Create or get a counter metric."""
        metric_name = f"{self.app_name}_{name}"
        if metric_name not in self._metrics:
            self._metrics[metric_name] = PrometheusCounter(
                metric_name,
                description,
                labels or [],
                registry=self.registry
            )
        return self._metrics[metric_name]
    
    def gauge(self, name: str, description: str, labels: Optional[List[str]] = None) -> PrometheusGauge:
        """Create or get a gauge metric."""
        metric_name = f"{self.app_name}_{name}"
        if metric_name not in self._metrics:
            self._metrics[metric_name] = PrometheusGauge(
                metric_name,
                description,
                labels or [],
                registry=self.registry
            )
        return self._metrics[metric_name]
    
    def histogram(self, name: str, description: str, labels: Optional[List[str]] = None,
                  buckets: Optional[List[float]] = None) -> PrometheusHistogram:
        """Create or get a histogram metric."""
        metric_name = f"{self.app_name}_{name}"
        if metric_name not in self._metrics:
            self._metrics[metric_name] = PrometheusHistogram(
                metric_name,
                description,
                labels or [],
                buckets=buckets or PrometheusHistogram.DEFAULT_BUCKETS,
                registry=self.registry
            )
        return self._metrics[metric_name]
    
    def summary(self, name: str, description: str, labels: Optional[List[str]] = None) -> PrometheusSummary:
        """Create or get a summary metric."""
        metric_name = f"{self.app_name}_{name}"
        if metric_name not in self._metrics:
            self._metrics[metric_name] = PrometheusSummary(
                metric_name,
                description,
                labels or [],
                registry=self.registry
            )
        return self._metrics[metric_name]
    
    def export(self) -> bytes:
        """Export metrics in Prometheus format."""
        return generate_latest(self.registry)
    
    def push_to_gateway(self, gateway_url: str, job: str = "essencia"):
        """Push metrics to Prometheus Pushgateway."""
        push_to_gateway(gateway_url, job=job, registry=self.registry)


# Global metrics collector instance
_metrics_collector = MetricsCollector()


# Convenience functions
def Counter(name: str, description: str, labels: Optional[List[str]] = None) -> PrometheusCounter:
    """Create a counter metric."""
    return _metrics_collector.counter(name, description, labels)


def Gauge(name: str, description: str, labels: Optional[List[str]] = None) -> PrometheusGauge:
    """Create a gauge metric."""
    return _metrics_collector.gauge(name, description, labels)


def Histogram(name: str, description: str, labels: Optional[List[str]] = None,
              buckets: Optional[List[float]] = None) -> PrometheusHistogram:
    """Create a histogram metric."""
    return _metrics_collector.histogram(name, description, labels, buckets)


def Summary(name: str, description: str, labels: Optional[List[str]] = None) -> PrometheusSummary:
    """Create a summary metric."""
    return _metrics_collector.summary(name, description, labels)


# Decorators and context managers
@contextmanager
def track_request(method: str, endpoint: str):
    """Track HTTP request metrics."""
    start_time = time.time()
    status = "success"
    
    try:
        yield
    except Exception as e:
        status = "error"
        _metrics_collector.error_count.labels(
            error_type=type(e).__name__,
            component="http"
        ).inc()
        raise
    finally:
        duration = time.time() - start_time
        _metrics_collector.request_count.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        _metrics_collector.request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)


@contextmanager
def track_database_operation(operation: str, collection: str):
    """Track database operation metrics."""
    start_time = time.time()
    status = "success"
    
    try:
        yield
    except Exception as e:
        status = "error"
        _metrics_collector.error_count.labels(
            error_type=type(e).__name__,
            component="database"
        ).inc()
        raise
    finally:
        duration = time.time() - start_time
        _metrics_collector.db_query_count.labels(
            operation=operation,
            collection=collection,
            status=status
        ).inc()
        _metrics_collector.db_query_duration.labels(
            operation=operation,
            collection=collection
        ).observe(duration)


@contextmanager
def track_cache_operation(cache_name: str, hit: bool):
    """Track cache operation metrics."""
    if hit:
        _metrics_collector.cache_hits.labels(cache_name=cache_name).inc()
    else:
        _metrics_collector.cache_misses.labels(cache_name=cache_name).inc()
    yield


def track_business_metric(metric_type: str, labels: Optional[Dict[str, str]] = None):
    """Track business-specific metrics."""
    if metric_type == "appointment_created":
        _metrics_collector.appointments_created.labels(
            appointment_type=labels.get("type", "general") if labels else "general"
        ).inc()
    elif metric_type == "prescription_issued":
        _metrics_collector.prescriptions_issued.labels(
            medication_type=labels.get("type", "general") if labels else "general"
        ).inc()


# FastAPI integration
def setup_metrics_endpoint(app):
    """Setup Prometheus metrics endpoint for FastAPI."""
    from fastapi import Response
    
    @app.get("/metrics")
    async def get_metrics():
        metrics = _metrics_collector.export()
        return Response(
            content=metrics,
            media_type=CONTENT_TYPE_LATEST
        )


# Decorator for tracking function execution
def track_execution_time(metric_name: str, labels: Optional[Dict[str, str]] = None):
    """Decorator to track function execution time."""
    def decorator(func: Callable) -> Callable:
        histogram = _metrics_collector.histogram(
            f"{metric_name}_duration_seconds",
            f"Execution time for {metric_name}",
            list(labels.keys()) if labels else []
        )
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if labels:
                    histogram.labels(**labels).observe(duration)
                else:
                    histogram.observe(duration)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                if labels:
                    histogram.labels(**labels).observe(duration)
                else:
                    histogram.observe(duration)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


import asyncio