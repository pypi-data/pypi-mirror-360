"""
Optimization middleware for performance and efficiency.
"""

import gzip
import time
import asyncio
from typing import Dict, Optional, Any, Set
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum
import hashlib
import json

from .base import BaseMiddleware, Request, Response, MiddlewareConfig


class CacheMiddleware(BaseMiddleware):
    """
    Middleware for response caching.
    """
    
    def __init__(
        self,
        cache_ttl: int = 300,  # 5 minutes
        cache_methods: Optional[Set[str]] = None,
        cache_paths: Optional[Set[str]] = None,
        vary_headers: Optional[List[str]] = None,
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.cache_ttl = cache_ttl
        self.cache_methods = cache_methods or {'GET'}
        self.cache_paths = cache_paths
        self.vary_headers = vary_headers or ['Accept', 'Accept-Language']
        self.cache: Dict[str, tuple[Response, datetime]] = {}
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Check cache for response."""
        if request.method.value not in self.cache_methods:
            return None
            
        if self.cache_paths and request.path not in self.cache_paths:
            return None
            
        # Generate cache key
        cache_key = self._generate_cache_key(request)
        
        # Check cache
        if cache_key in self.cache:
            cached_response, expires_at = self.cache[cache_key]
            if datetime.utcnow() < expires_at:
                # Cache hit
                response = Response(
                    status_code=cached_response.status_code,
                    headers=cached_response.headers.copy(),
                    body=cached_response.body
                )
                response.set_header('X-Cache', 'HIT')
                return response
            else:
                # Expired
                del self.cache[cache_key]
                
        return None
        
    async def process_response(self, request: Request, response: Response) -> Response:
        """Cache successful responses."""
        if (request.method.value in self.cache_methods and 
            response.is_success and
            (self.cache_paths is None or request.path in self.cache_paths)):
            
            # Generate cache key
            cache_key = self._generate_cache_key(request)
            
            # Store in cache
            expires_at = datetime.utcnow() + timedelta(seconds=self.cache_ttl)
            self.cache[cache_key] = (response, expires_at)
            
            # Add cache headers
            response.set_header('X-Cache', 'MISS')
            response.set_header('Cache-Control', f'public, max-age={self.cache_ttl}')
            
            # Clean old entries periodically
            if len(self.cache) > 1000:
                self._cleanup_cache()
                
        return response
        
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key from request."""
        parts = [
            request.method.value,
            request.path,
            str(sorted(request.query_params.items()))
        ]
        
        # Add vary headers
        for header in self.vary_headers:
            value = request.get_header(header, '')
            parts.append(f"{header}:{value}")
            
        # Hash for consistent key
        key_string = '|'.join(parts)
        return hashlib.md5(key_string.encode()).hexdigest()
        
    def _cleanup_cache(self) -> None:
        """Remove expired entries."""
        now = datetime.utcnow()
        expired_keys = [
            key for key, (_, expires_at) in self.cache.items()
            if expires_at < now
        ]
        for key in expired_keys:
            del self.cache[key]


class CompressionMiddleware(BaseMiddleware):
    """
    Middleware for response compression.
    """
    
    def __init__(
        self,
        min_size: int = 1024,  # Don't compress small responses
        compression_level: int = 6,
        mime_types: Optional[Set[str]] = None,
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.min_size = min_size
        self.compression_level = compression_level
        self.mime_types = mime_types or {
            'text/html', 'text/plain', 'text/css', 'text/javascript',
            'application/json', 'application/javascript', 'application/xml'
        }
        
    async def process_response(self, request: Request, response: Response) -> Response:
        """Compress response if appropriate."""
        # Check if client accepts gzip
        accept_encoding = request.get_header('Accept-Encoding', '')
        if 'gzip' not in accept_encoding:
            return response
            
        # Check response size and type
        if not self._should_compress(response):
            return response
            
        # Compress body
        if isinstance(response.body, str):
            body_bytes = response.body.encode('utf-8')
        elif isinstance(response.body, bytes):
            body_bytes = response.body
        else:
            # JSON serialize
            body_bytes = json.dumps(response.body).encode('utf-8')
            
        compressed = gzip.compress(body_bytes, compresslevel=self.compression_level)
        
        # Update response
        response.body = compressed
        response.set_header('Content-Encoding', 'gzip')
        response.set_header('Vary', 'Accept-Encoding')
        
        return response
        
    def _should_compress(self, response: Response) -> bool:
        """Check if response should be compressed."""
        # Check content type
        content_type = response.headers.get('Content-Type', '')
        mime_type = content_type.split(';')[0].strip()
        if mime_type not in self.mime_types:
            return False
            
        # Check size (rough estimate)
        if isinstance(response.body, (str, bytes)):
            size = len(response.body)
        else:
            size = len(json.dumps(response.body))
            
        return size >= self.min_size


class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware for rate limiting.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        by_user: bool = True,
        by_ip: bool = True,
        burst_size: int = 10,
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.by_user = by_user
        self.by_ip = by_ip
        self.burst_size = burst_size
        
        # Token buckets for rate limiting
        self.buckets: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'tokens': burst_size,
            'last_update': time.time()
        })
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Check rate limits."""
        # Generate rate limit key
        keys = []
        if self.by_user and request.user:
            keys.append(f"user:{request.user.get('id')}")
        if self.by_ip:
            ip = request.metadata.get('client_ip', 'unknown')
            keys.append(f"ip:{ip}")
            
        if not keys:
            return None
            
        # Check each key
        for key in keys:
            if not self._check_rate_limit(key):
                return Response(
                    status_code=429,
                    body={'error': 'Rate limit exceeded'},
                    headers={
                        'Retry-After': '60',
                        'X-RateLimit-Limit': str(self.requests_per_minute),
                        'X-RateLimit-Remaining': '0'
                    }
                )
                
        return None
        
    def _check_rate_limit(self, key: str) -> bool:
        """Check if request is within rate limit."""
        bucket = self.buckets[key]
        now = time.time()
        
        # Refill tokens based on time passed
        time_passed = now - bucket['last_update']
        tokens_to_add = time_passed * (self.requests_per_minute / 60.0)
        
        bucket['tokens'] = min(
            self.burst_size,
            bucket['tokens'] + tokens_to_add
        )
        bucket['last_update'] = now
        
        # Check if we have tokens
        if bucket['tokens'] >= 1:
            bucket['tokens'] -= 1
            return True
            
        return False


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerMiddleware(BaseMiddleware):
    """
    Middleware for circuit breaker pattern.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,  # seconds
        success_threshold: int = 3,
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        # Circuit breaker state per endpoint
        self.circuits: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'state': CircuitBreakerState.CLOSED,
            'failures': 0,
            'successes': 0,
            'last_failure': None,
            'last_state_change': datetime.utcnow()
        })
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Check circuit breaker state."""
        circuit = self.circuits[request.path]
        
        # Update state if needed
        self._update_circuit_state(circuit)
        
        if circuit['state'] == CircuitBreakerState.OPEN:
            return Response(
                status_code=503,
                body={'error': 'Service temporarily unavailable'},
                headers={'Retry-After': str(self.recovery_timeout)}
            )
            
        return None
        
    async def process_response(self, request: Request, response: Response) -> Response:
        """Update circuit breaker based on response."""
        circuit = self.circuits[request.path]
        
        if response.status_code >= 500:
            # Server error - count as failure
            self._record_failure(circuit)
        else:
            # Success
            self._record_success(circuit)
            
        return response
        
    def _update_circuit_state(self, circuit: Dict[str, Any]) -> None:
        """Update circuit state based on current conditions."""
        now = datetime.utcnow()
        
        if circuit['state'] == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if circuit['last_failure']:
                time_since_failure = (now - circuit['last_failure']).total_seconds()
                if time_since_failure >= self.recovery_timeout:
                    circuit['state'] = CircuitBreakerState.HALF_OPEN
                    circuit['last_state_change'] = now
                    self.logger.info(f"Circuit breaker entered HALF_OPEN state")
                    
    def _record_failure(self, circuit: Dict[str, Any]) -> None:
        """Record a failure."""
        circuit['failures'] += 1
        circuit['last_failure'] = datetime.utcnow()
        
        if circuit['state'] == CircuitBreakerState.HALF_OPEN:
            # Single failure in half-open returns to open
            circuit['state'] = CircuitBreakerState.OPEN
            circuit['failures'] = 0
            circuit['last_state_change'] = datetime.utcnow()
            self.logger.warning("Circuit breaker reopened due to failure in HALF_OPEN state")
            
        elif circuit['state'] == CircuitBreakerState.CLOSED:
            # Check if we've hit the threshold
            if circuit['failures'] >= self.failure_threshold:
                circuit['state'] = CircuitBreakerState.OPEN
                circuit['last_state_change'] = datetime.utcnow()
                self.logger.warning(f"Circuit breaker opened after {circuit['failures']} failures")
                
    def _record_success(self, circuit: Dict[str, Any]) -> None:
        """Record a success."""
        if circuit['state'] == CircuitBreakerState.HALF_OPEN:
            circuit['successes'] += 1
            
            # Check if we can close the circuit
            if circuit['successes'] >= self.success_threshold:
                circuit['state'] = CircuitBreakerState.CLOSED
                circuit['failures'] = 0
                circuit['successes'] = 0
                circuit['last_state_change'] = datetime.utcnow()
                self.logger.info("Circuit breaker closed after successful recovery")
                
        elif circuit['state'] == CircuitBreakerState.CLOSED:
            # Reset failure count on success
            circuit['failures'] = 0


class RetryMiddleware(BaseMiddleware):
    """
    Middleware for automatic retries.
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        exponential_backoff: bool = True,
        retry_on_status: Optional[Set[int]] = None,
        config: Optional[MiddlewareConfig] = None
    ):
        super().__init__(config)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.exponential_backoff = exponential_backoff
        self.retry_on_status = retry_on_status or {408, 429, 500, 502, 503, 504}
        
    async def process_response(self, request: Request, response: Response) -> Response:
        """Retry failed requests if appropriate."""
        if response.status_code not in self.retry_on_status:
            return response
            
        # Check if we've already retried
        retry_count = request.metadata.get('retry_count', 0)
        if retry_count >= self.max_retries:
            return response
            
        # Calculate delay
        if self.exponential_backoff:
            delay = self.retry_delay * (2 ** retry_count)
        else:
            delay = self.retry_delay
            
        self.logger.info(f"Retrying request after {delay}s (attempt {retry_count + 1}/{self.max_retries})")
        
        # Wait before retry
        await asyncio.sleep(delay)
        
        # Update retry count
        request.metadata['retry_count'] = retry_count + 1
        
        # Retry the request (would need handler reference)
        # For now, just return the response
        return response