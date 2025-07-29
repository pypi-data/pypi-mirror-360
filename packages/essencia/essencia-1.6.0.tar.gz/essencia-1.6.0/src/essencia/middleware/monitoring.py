"""
Monitoring middleware for observability.
"""

import time
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict
import asyncio

from .base import BaseMiddleware, Request, Response, MiddlewareConfig

logger = logging.getLogger(__name__)


class MetricsMiddleware(BaseMiddleware):
    """
    Middleware for collecting metrics.
    """
    
    def __init__(self, config: Optional[MiddlewareConfig] = None):
        super().__init__(config)
        self.metrics = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'errors': 0,
            'status_codes': defaultdict(int)
        })
        self.request_times: Dict[str, float] = {}
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Record request start time."""
        request_id = id(request)
        self.request_times[request_id] = time.time()
        return None
        
    async def process_response(self, request: Request, response: Response) -> Response:
        """Record metrics for the request."""
        request_id = id(request)
        start_time = self.request_times.pop(request_id, None)
        
        if start_time:
            elapsed = time.time() - start_time
            path = request.path
            
            # Update metrics
            metrics = self.metrics[path]
            metrics['count'] += 1
            metrics['total_time'] += elapsed
            metrics['status_codes'][response.status_code] += 1
            
            if response.is_error:
                metrics['errors'] += 1
                
            # Add timing header
            response.set_header('X-Response-Time', f"{elapsed * 1000:.2f}ms")
            
        return response
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics."""
        result = {}
        for path, metrics in self.metrics.items():
            avg_time = metrics['total_time'] / metrics['count'] if metrics['count'] > 0 else 0
            result[path] = {
                'requests': metrics['count'],
                'average_time_ms': avg_time * 1000,
                'error_rate': metrics['errors'] / metrics['count'] if metrics['count'] > 0 else 0,
                'status_codes': dict(metrics['status_codes'])
            }
        return result


class TracingMiddleware(BaseMiddleware):
    """
    Middleware for distributed tracing.
    """
    
    def __init__(self, service_name: str = "essencia", config: Optional[MiddlewareConfig] = None):
        super().__init__(config)
        self.service_name = service_name
        self.traces: List[Dict[str, Any]] = []
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Start trace span."""
        import uuid
        
        # Get or create trace ID
        trace_id = request.get_header('X-Trace-ID') or str(uuid.uuid4())
        span_id = str(uuid.uuid4())
        
        # Store in request metadata
        request.metadata['trace_id'] = trace_id
        request.metadata['span_id'] = span_id
        request.metadata['trace_start'] = time.time()
        
        # Add to headers for propagation
        request.set_header('X-Trace-ID', trace_id)
        request.set_header('X-Span-ID', span_id)
        
        return None
        
    async def process_response(self, request: Request, response: Response) -> Response:
        """Complete trace span."""
        trace_id = request.metadata.get('trace_id')
        span_id = request.metadata.get('span_id')
        start_time = request.metadata.get('trace_start')
        
        if all([trace_id, span_id, start_time]):
            duration = time.time() - start_time
            
            # Create trace record
            trace = {
                'trace_id': trace_id,
                'span_id': span_id,
                'service': self.service_name,
                'operation': f"{request.method.value} {request.path}",
                'start_time': datetime.fromtimestamp(start_time).isoformat(),
                'duration_ms': duration * 1000,
                'status_code': response.status_code,
                'success': response.is_success,
                'user_id': request.user.get('id') if request.user else None
            }
            
            self.traces.append(trace)
            
            # Add trace headers to response
            response.set_header('X-Trace-ID', trace_id)
            response.set_header('X-Span-ID', span_id)
            
        return response
        
    def get_traces(self, trace_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get traces, optionally filtered by trace ID."""
        if trace_id:
            return [t for t in self.traces if t['trace_id'] == trace_id]
        return self.traces.copy()


class LoggingMiddleware(BaseMiddleware):
    """
    Middleware for structured logging.
    """
    
    def __init__(
        self,
        log_level: str = "INFO",
        log_body: bool = False,
        log_headers: bool = True,
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.log_level = getattr(logging, log_level.upper())
        self.log_body = log_body
        self.log_headers = log_headers
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Log incoming request."""
        log_data = {
            'event': 'request',
            'method': request.method.value,
            'path': request.path,
            'user_id': request.user.get('id') if request.user else None,
            'timestamp': request.timestamp.isoformat()
        }
        
        if self.log_headers:
            log_data['headers'] = {k: v for k, v in request.headers.items() 
                                 if not k.lower().startswith('authorization')}
            
        if self.log_body and request.body:
            # Sanitize sensitive data
            log_data['body'] = self._sanitize_body(request.body)
            
        self.logger.log(self.log_level, "Incoming request", extra=log_data)
        return None
        
    async def process_response(self, request: Request, response: Response) -> Response:
        """Log outgoing response."""
        log_data = {
            'event': 'response',
            'method': request.method.value,
            'path': request.path,
            'status_code': response.status_code,
            'success': response.is_success,
            'user_id': request.user.get('id') if request.user else None
        }
        
        if self.log_headers:
            log_data['response_headers'] = response.headers
            
        self.logger.log(self.log_level, "Outgoing response", extra=log_data)
        return response
        
    def _sanitize_body(self, body: Any) -> Any:
        """Sanitize sensitive data from body."""
        if isinstance(body, dict):
            sanitized = body.copy()
            sensitive_fields = ['password', 'token', 'secret', 'cpf', 'rg', 'credit_card']
            for field in sensitive_fields:
                if field in sanitized:
                    sanitized[field] = '***REDACTED***'
            return sanitized
        elif isinstance(body, str) and len(body) > 1000:
            return body[:1000] + '...(truncated)'
        return body


class HealthCheckMiddleware(BaseMiddleware):
    """
    Middleware for health check endpoints.
    """
    
    def __init__(
        self,
        health_path: str = "/health",
        ready_path: str = "/ready",
        checks: Optional[List[Callable]] = None,
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.health_path = health_path
        self.ready_path = ready_path
        self.checks = checks or []
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Handle health check requests."""
        if request.path == self.health_path:
            return await self._health_check()
        elif request.path == self.ready_path:
            return await self._readiness_check()
        return None
        
    async def _health_check(self) -> Response:
        """Basic health check."""
        return Response(
            status_code=200,
            body={
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'essencia'
            }
        )
        
    async def _readiness_check(self) -> Response:
        """Readiness check with dependency checks."""
        checks_passed = []
        checks_failed = []
        
        for check in self.checks:
            try:
                if asyncio.iscoroutinefunction(check):
                    result = await check()
                else:
                    result = check()
                    
                if result:
                    checks_passed.append(check.__name__)
                else:
                    checks_failed.append(check.__name__)
            except Exception as e:
                checks_failed.append(f"{check.__name__}: {str(e)}")
                
        ready = len(checks_failed) == 0
        
        return Response(
            status_code=200 if ready else 503,
            body={
                'ready': ready,
                'checks_passed': checks_passed,
                'checks_failed': checks_failed,
                'timestamp': datetime.utcnow().isoformat()
            }
        )


class PerformanceMiddleware(BaseMiddleware):
    """
    Middleware for performance monitoring and optimization.
    """
    
    def __init__(
        self,
        slow_request_threshold: float = 1.0,  # seconds
        memory_tracking: bool = True,
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.slow_request_threshold = slow_request_threshold
        self.memory_tracking = memory_tracking
        self.slow_requests: List[Dict[str, Any]] = []
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Start performance tracking."""
        request.metadata['perf_start'] = time.time()
        
        if self.memory_tracking:
            import psutil
            process = psutil.Process()
            request.metadata['memory_start'] = process.memory_info().rss
            
        return None
        
    async def process_response(self, request: Request, response: Response) -> Response:
        """Complete performance tracking."""
        start_time = request.metadata.get('perf_start')
        if start_time:
            elapsed = time.time() - start_time
            
            # Track slow requests
            if elapsed > self.slow_request_threshold:
                slow_request = {
                    'path': request.path,
                    'method': request.method.value,
                    'duration': elapsed,
                    'timestamp': datetime.utcnow().isoformat(),
                    'user_id': request.user.get('id') if request.user else None
                }
                
                if self.memory_tracking:
                    import psutil
                    process = psutil.Process()
                    memory_start = request.metadata.get('memory_start', 0)
                    memory_end = process.memory_info().rss
                    slow_request['memory_delta_mb'] = (memory_end - memory_start) / 1024 / 1024
                    
                self.slow_requests.append(slow_request)
                self.logger.warning(f"Slow request detected: {slow_request}")
                
                # Keep only recent slow requests
                if len(self.slow_requests) > 100:
                    self.slow_requests = self.slow_requests[-100:]
                    
        return response
        
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.slow_requests:
            return {'slow_requests': 0}
            
        durations = [r['duration'] for r in self.slow_requests]
        return {
            'slow_requests': len(self.slow_requests),
            'slowest_request': max(durations),
            'average_slow_duration': sum(durations) / len(durations),
            'recent_slow_requests': self.slow_requests[-10:]
        }