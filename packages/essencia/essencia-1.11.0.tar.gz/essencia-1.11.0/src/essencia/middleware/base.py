"""
Base middleware classes and protocols.
"""

from typing import Any, Dict, List, Optional, Callable, TypeVar, Protocol, runtime_checkable
from dataclasses import dataclass, field
from datetime import datetime
from abc import ABC, abstractmethod
import asyncio
import logging
from enum import Enum

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RequestMethod(Enum):
    """HTTP request methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class Request:
    """Represents an incoming request."""
    method: RequestMethod = RequestMethod.GET
    path: str = "/"
    headers: Dict[str, str] = field(default_factory=dict)
    query_params: Dict[str, Any] = field(default_factory=dict)
    body: Optional[Any] = None
    user: Optional[Dict[str, Any]] = None
    session: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_authenticated(self) -> bool:
        """Check if request has authenticated user."""
        return self.user is not None
        
    def get_header(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get header value (case-insensitive)."""
        return self.headers.get(name.lower(), default)
        
    def set_header(self, name: str, value: str) -> None:
        """Set header value."""
        self.headers[name.lower()] = value


@dataclass
class Response:
    """Represents an outgoing response."""
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def set_header(self, name: str, value: str) -> None:
        """Set response header."""
        self.headers[name] = value
        
    def set_status(self, code: int) -> None:
        """Set response status code."""
        self.status_code = code
        
    @property
    def is_success(self) -> bool:
        """Check if response indicates success."""
        return 200 <= self.status_code < 300
        
    @property
    def is_error(self) -> bool:
        """Check if response indicates error."""
        return self.status_code >= 400


@dataclass
class MiddlewareConfig:
    """Configuration for middleware."""
    enabled: bool = True
    priority: int = 0  # Lower number = higher priority
    async_mode: bool = True
    timeout: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class Middleware(Protocol):
    """Protocol for middleware implementations."""
    
    async def process_request(self, request: Request) -> Optional[Response]:
        """
        Process incoming request.
        
        Args:
            request: Incoming request
            
        Returns:
            Response to short-circuit processing, or None to continue
        """
        ...
        
    async def process_response(self, request: Request, response: Response) -> Response:
        """
        Process outgoing response.
        
        Args:
            request: Original request
            response: Response to process
            
        Returns:
            Modified response
        """
        ...


class BaseMiddleware(ABC):
    """
    Base class for middleware implementations.
    """
    
    def __init__(self, config: Optional[MiddlewareConfig] = None):
        """
        Initialize middleware.
        
        Args:
            config: Middleware configuration
        """
        self.config = config or MiddlewareConfig()
        self.logger = logger
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize middleware resources."""
        if self._initialized:
            return
        self._initialized = True
        self.logger.info(f"Initialized {self.__class__.__name__}")
        
    async def cleanup(self) -> None:
        """Cleanup middleware resources."""
        self._initialized = False
        self.logger.info(f"Cleaned up {self.__class__.__name__}")
        
    @abstractmethod
    async def process_request(self, request: Request) -> Optional[Response]:
        """Process incoming request."""
        pass
        
    async def process_response(self, request: Request, response: Response) -> Response:
        """Process outgoing response (default: no-op)."""
        return response
        
    def should_process(self, request: Request) -> bool:
        """Check if middleware should process this request."""
        return self.config.enabled


class MiddlewareChain:
    """
    Chain of middleware to process requests/responses.
    """
    
    def __init__(self):
        """Initialize middleware chain."""
        self.middlewares: List[tuple[int, Middleware]] = []
        self.logger = logger
        
    def add(self, middleware: Middleware, priority: int = 0) -> None:
        """
        Add middleware to chain.
        
        Args:
            middleware: Middleware instance
            priority: Processing priority (lower = earlier)
        """
        self.middlewares.append((priority, middleware))
        # Sort by priority
        self.middlewares.sort(key=lambda x: x[0])
        self.logger.debug(f"Added middleware {middleware.__class__.__name__} with priority {priority}")
        
    def remove(self, middleware_class: type) -> None:
        """Remove middleware by class."""
        self.middlewares = [
            (p, m) for p, m in self.middlewares
            if not isinstance(m, middleware_class)
        ]
        
    async def initialize_all(self) -> None:
        """Initialize all middleware."""
        for _, middleware in self.middlewares:
            if hasattr(middleware, 'initialize'):
                await middleware.initialize()
                
    async def cleanup_all(self) -> None:
        """Cleanup all middleware."""
        for _, middleware in reversed(self.middlewares):
            if hasattr(middleware, 'cleanup'):
                await middleware.cleanup()
                
    async def process_request(self, request: Request) -> Optional[Response]:
        """
        Process request through middleware chain.
        
        Args:
            request: Incoming request
            
        Returns:
            Response if processing should stop, None otherwise
        """
        for _, middleware in self.middlewares:
            try:
                # Check if middleware should process
                if hasattr(middleware, 'should_process') and not middleware.should_process(request):
                    continue
                    
                # Process request
                response = await middleware.process_request(request)
                if response is not None:
                    # Short-circuit: middleware returned a response
                    self.logger.debug(
                        f"Middleware {middleware.__class__.__name__} short-circuited request processing"
                    )
                    return response
                    
            except Exception as e:
                self.logger.error(
                    f"Error in middleware {middleware.__class__.__name__} during request processing: {e}"
                )
                # Continue processing despite error
                
        return None
        
    async def process_response(self, request: Request, response: Response) -> Response:
        """
        Process response through middleware chain (in reverse order).
        
        Args:
            request: Original request
            response: Response to process
            
        Returns:
            Processed response
        """
        for _, middleware in reversed(self.middlewares):
            try:
                # Check if middleware should process
                if hasattr(middleware, 'should_process') and not middleware.should_process(request):
                    continue
                    
                # Process response
                response = await middleware.process_response(request, response)
                
            except Exception as e:
                self.logger.error(
                    f"Error in middleware {middleware.__class__.__name__} during response processing: {e}"
                )
                # Continue processing despite error
                
        return response
        
    async def execute(
        self,
        request: Request,
        handler: Callable[[Request], Response]
    ) -> Response:
        """
        Execute full middleware chain with handler.
        
        Args:
            request: Incoming request
            handler: Request handler function
            
        Returns:
            Final response
        """
        # Process request through middleware
        response = await self.process_request(request)
        
        if response is None:
            # No middleware returned a response, call handler
            try:
                if asyncio.iscoroutinefunction(handler):
                    response = await handler(request)
                else:
                    response = handler(request)
            except Exception as e:
                self.logger.error(f"Error in request handler: {e}")
                response = Response(
                    status_code=500,
                    body={"error": "Internal server error"}
                )
                
        # Process response through middleware
        response = await self.process_response(request, response)
        
        return response


class CompositeMiddleware(BaseMiddleware):
    """
    Middleware that combines multiple middleware instances.
    """
    
    def __init__(self, middlewares: List[Middleware], config: Optional[MiddlewareConfig] = None):
        """
        Initialize composite middleware.
        
        Args:
            middlewares: List of middleware to combine
            config: Configuration
        """
        super().__init__(config)
        self.middlewares = middlewares
        
    async def initialize(self) -> None:
        """Initialize all child middleware."""
        await super().initialize()
        for middleware in self.middlewares:
            if hasattr(middleware, 'initialize'):
                await middleware.initialize()
                
    async def cleanup(self) -> None:
        """Cleanup all child middleware."""
        for middleware in reversed(self.middlewares):
            if hasattr(middleware, 'cleanup'):
                await middleware.cleanup()
        await super().cleanup()
        
    async def process_request(self, request: Request) -> Optional[Response]:
        """Process request through all middleware."""
        for middleware in self.middlewares:
            response = await middleware.process_request(request)
            if response is not None:
                return response
        return None
        
    async def process_response(self, request: Request, response: Response) -> Response:
        """Process response through all middleware in reverse."""
        for middleware in reversed(self.middlewares):
            response = await middleware.process_response(request, response)
        return response