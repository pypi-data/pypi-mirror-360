"""
Comprehensive rate limiting system for DDoS protection and API abuse prevention.

Provides multiple rate limiting strategies:
- Fixed window rate limiting
- Sliding window rate limiting
- Token bucket algorithm
- User-based and IP-based limiting
- Distributed rate limiting with Redis
"""

import time
import logging
import hashlib
from typing import Dict, Optional, Union, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from functools import wraps
from collections import defaultdict, deque
import asyncio

# Import for Redis if available
# Temporarily disabled for PyInstaller compatibility
# try:
#     import aioredis
#     REDIS_AVAILABLE = True
# except ImportError:
REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)
logger.warning("aioredis disabled for PyInstaller compatibility")


class RateLimitError(Exception):
    """Rate limit exceeded error."""
    def __init__(self, message: str, retry_after: Optional[int] = None, endpoint: Optional[str] = None):
        super().__init__(message)
        self.retry_after = retry_after
        self.endpoint = endpoint


class RateLimitStrategy(str, Enum):
    """Rate limiting strategies."""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimitScope(str, Enum):
    """Rate limit scope types."""
    USER = "user"
    IP = "ip"
    ENDPOINT = "endpoint"
    GLOBAL = "global"
    CUSTOM = "custom"


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests: int  # Number of requests allowed
    window: int    # Time window in seconds
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    scope: RateLimitScope = RateLimitScope.USER
    burst_multiplier: float = 1.5  # Allow burst up to this multiplier
    cooldown_period: int = 300     # Cooldown period after rate limit hit
    whitelist: Optional[List[str]] = None  # Whitelisted IPs or user IDs


@dataclass
class RateLimitResult:
    """Rate limit check result."""
    allowed: bool
    remaining: int
    reset_time: int
    retry_after: Optional[int] = None
    current_usage: int = 0


class RateLimiter:
    """
    Comprehensive rate limiting system with multiple strategies.
    
    Supports both in-memory and Redis-based distributed rate limiting.
    """
    
    def __init__(self, use_redis: bool = True, redis_url: Optional[str] = None):
        """
        Initialize rate limiter.
        
        Args:
            use_redis: Whether to use Redis for distributed rate limiting
            redis_url: Redis URL for connection
        """
        self.use_redis = use_redis and REDIS_AVAILABLE
        self.redis_url = redis_url
        self.redis_client = None
        
        # In-memory storage for when Redis is not available
        self._memory_store: Dict[str, Dict] = defaultdict(dict)
        self._token_buckets: Dict[str, Dict] = defaultdict(dict)
        
        # Predefined rate limit configurations
        self.configs = {
            "login": RateLimitConfig(
                requests=5, 
                window=300,  # 5 requests per 5 minutes
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                scope=RateLimitScope.IP,
                cooldown_period=900  # 15 minute cooldown
            ),
            "api": RateLimitConfig(
                requests=100,
                window=3600,  # 100 requests per hour
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                scope=RateLimitScope.USER
            ),
            "search": RateLimitConfig(
                requests=50,
                window=300,  # 50 searches per 5 minutes
                strategy=RateLimitStrategy.TOKEN_BUCKET,
                scope=RateLimitScope.USER
            ),
            "export": RateLimitConfig(
                requests=5,
                window=3600,  # 5 exports per hour
                strategy=RateLimitStrategy.FIXED_WINDOW,
                scope=RateLimitScope.USER,
                cooldown_period=3600
            ),
            "form_submission": RateLimitConfig(
                requests=20,
                window=60,  # 20 form submissions per minute
                strategy=RateLimitStrategy.SLIDING_WINDOW,
                scope=RateLimitScope.USER
            ),
            "password_reset": RateLimitConfig(
                requests=3,
                window=3600,  # 3 password resets per hour
                strategy=RateLimitStrategy.FIXED_WINDOW,
                scope=RateLimitScope.IP,
                cooldown_period=7200  # 2 hour cooldown
            )
        }
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._redis_initialized = False
    
    async def _init_redis(self):
        """Initialize Redis connection if needed."""
        if not self.use_redis or self._redis_initialized:
            return
        
        try:
            if self.redis_url and REDIS_AVAILABLE:
                self.redis_client = aioredis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_keepalive=True,
                    socket_connect_timeout=5
                )
                # Test connection
                await self.redis_client.ping()
                self._redis_initialized = True
                self.logger.info("Rate limiter Redis connection established")
            else:
                self.use_redis = False
        except Exception as e:
            self.logger.warning(f"Redis initialization failed: {e}, using in-memory rate limiting")
            self.use_redis = False
            self.redis_client = None
    
    def _generate_key(self, identifier: str, config: RateLimitConfig, endpoint: str = "") -> str:
        """Generate cache key for rate limiting."""
        scope_id = f"{config.scope.value}:{identifier}"
        endpoint_suffix = f":{endpoint}" if endpoint else ""
        key = f"rate_limit:{scope_id}{endpoint_suffix}:{config.strategy.value}"
        return hashlib.md5(key.encode()).hexdigest()
    
    async def check_rate_limit(
        self, 
        identifier: str, 
        config_name: str, 
        endpoint: str = "",
        custom_config: Optional[RateLimitConfig] = None
    ) -> RateLimitResult:
        """
        Check if request is within rate limits.
        
        Args:
            identifier: User ID, IP address, or custom identifier
            config_name: Name of predefined config or "custom"
            endpoint: Optional endpoint name for endpoint-specific limiting
            custom_config: Custom configuration if config_name is "custom"
            
        Returns:
            RateLimitResult with rate limit status
        """
        config = custom_config if config_name == "custom" else self.configs.get(config_name)
        if not config:
            raise ValueError(f"Unknown rate limit config: {config_name}")
        
        # Check whitelist
        if config.whitelist and identifier in config.whitelist:
            return RateLimitResult(
                allowed=True,
                remaining=config.requests,
                reset_time=int(time.time()) + config.window
            )
        
        key = self._generate_key(identifier, config, endpoint)
        current_time = time.time()
        
        # Initialize Redis if needed
        await self._init_redis()
        
        if config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return await self._check_sliding_window(key, config, current_time)
        elif config.strategy == RateLimitStrategy.FIXED_WINDOW:
            return await self._check_fixed_window(key, config, current_time)
        elif config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return await self._check_token_bucket(key, config, current_time)
        else:
            raise ValueError(f"Unsupported rate limit strategy: {config.strategy}")
    
    async def _check_sliding_window(self, key: str, config: RateLimitConfig, current_time: float) -> RateLimitResult:
        """Implement sliding window rate limiting."""
        window_start = current_time - config.window
        
        if self.use_redis and self.redis_client:
            # Redis-based sliding window using sorted sets
            try:
                pipe = self.redis_client.pipeline()
                # Remove old entries
                pipe.zremrangebyscore(key, 0, window_start)
                # Add current request
                pipe.zadd(key, {str(current_time): current_time})
                # Count current requests
                pipe.zcard(key)
                # Set expiration
                pipe.expire(key, config.window)
                results = await pipe.execute()
                
                request_count = results[2]
                
            except Exception as e:
                self.logger.warning(f"Redis sliding window failed, falling back to memory: {e}")
                request_count = await self._memory_sliding_window(key, config, current_time, window_start)
        else:
            request_count = await self._memory_sliding_window(key, config, current_time, window_start)
        
        allowed = request_count <= config.requests
        remaining = max(0, config.requests - request_count)
        reset_time = int(current_time + config.window)
        
        if not allowed:
            retry_after = config.cooldown_period if config.cooldown_period else config.window
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_time=reset_time,
                retry_after=retry_after,
                current_usage=request_count
            )
        
        return RateLimitResult(
            allowed=True,
            remaining=remaining,
            reset_time=reset_time,
            current_usage=request_count
        )
    
    async def _memory_sliding_window(self, key: str, config: RateLimitConfig, current_time: float, window_start: float) -> int:
        """In-memory sliding window implementation."""
        if key not in self._memory_store:
            self._memory_store[key] = {"requests": deque(), "last_cleanup": current_time}
        
        store = self._memory_store[key]
        requests = store["requests"]
        
        # Clean old requests
        while requests and requests[0] < window_start:
            requests.popleft()
        
        # Add current request
        requests.append(current_time)
        store["last_cleanup"] = current_time
        
        return len(requests)
    
    async def _check_fixed_window(self, key: str, config: RateLimitConfig, current_time: float) -> RateLimitResult:
        """Implement fixed window rate limiting."""
        window_id = int(current_time // config.window)
        window_key = f"{key}:{window_id}"
        
        if self.use_redis and self.redis_client:
            try:
                pipe = self.redis_client.pipeline()
                pipe.incr(window_key)
                pipe.expire(window_key, config.window)
                results = await pipe.execute()
                
                request_count = results[0]
                
            except Exception as e:
                self.logger.warning(f"Redis fixed window failed, falling back to memory: {e}")
                request_count = await self._memory_fixed_window(window_key, config)
        else:
            request_count = await self._memory_fixed_window(window_key, config)
        
        allowed = request_count <= config.requests
        remaining = max(0, config.requests - request_count)
        reset_time = int((window_id + 1) * config.window)
        
        if not allowed:
            retry_after = reset_time - int(current_time)
            if config.cooldown_period:
                retry_after = max(retry_after, config.cooldown_period)
            
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_time=reset_time,
                retry_after=retry_after,
                current_usage=request_count
            )
        
        return RateLimitResult(
            allowed=True,
            remaining=remaining,
            reset_time=reset_time,
            current_usage=request_count
        )
    
    async def _memory_fixed_window(self, window_key: str, config: RateLimitConfig) -> int:
        """In-memory fixed window implementation."""
        if window_key not in self._memory_store:
            self._memory_store[window_key] = {"count": 0}
        
        self._memory_store[window_key]["count"] += 1
        return self._memory_store[window_key]["count"]
    
    async def _check_token_bucket(self, key: str, config: RateLimitConfig, current_time: float) -> RateLimitResult:
        """Implement token bucket rate limiting."""
        if self.use_redis and self.redis_client:
            try:
                # Redis Lua script for atomic token bucket operation
                lua_script = """
                local key = KEYS[1]
                local capacity = tonumber(ARGV[1])
                local refill_rate = tonumber(ARGV[2])
                local current_time = tonumber(ARGV[3])
                local window = tonumber(ARGV[4])
                
                local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
                local tokens = tonumber(bucket[1]) or capacity
                local last_refill = tonumber(bucket[2]) or current_time
                
                -- Calculate tokens to add
                local time_passed = current_time - last_refill
                local tokens_to_add = math.floor(time_passed * refill_rate)
                tokens = math.min(capacity, tokens + tokens_to_add)
                
                -- Try to consume a token
                if tokens >= 1 then
                    tokens = tokens - 1
                    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', current_time)
                    redis.call('EXPIRE', key, window * 2)
                    return {1, tokens}
                else
                    redis.call('HMSET', key, 'tokens', tokens, 'last_refill', current_time)
                    redis.call('EXPIRE', key, window * 2)
                    return {0, tokens}
                end
                """
                
                refill_rate = config.requests / config.window
                result = await self.redis_client.eval(
                    lua_script, 1, key, 
                    config.requests, refill_rate, current_time, config.window
                )
                
                allowed = bool(result[0])
                tokens = result[1]
                
            except Exception as e:
                self.logger.warning(f"Redis token bucket failed, falling back to memory: {e}")
                allowed, tokens = await self._memory_token_bucket(key, config, current_time)
        else:
            allowed, tokens = await self._memory_token_bucket(key, config, current_time)
        
        remaining = int(tokens)
        reset_time = int(current_time + config.window)
        
        if not allowed:
            # Calculate when next token will be available
            refill_rate = config.requests / config.window
            time_for_token = 1.0 / refill_rate
            retry_after = int(time_for_token)
            
            return RateLimitResult(
                allowed=False,
                remaining=remaining,
                reset_time=reset_time,
                retry_after=retry_after,
                current_usage=config.requests - remaining
            )
        
        return RateLimitResult(
            allowed=True,
            remaining=remaining,
            reset_time=reset_time,
            current_usage=config.requests - remaining - 1
        )
    
    async def _memory_token_bucket(self, key: str, config: RateLimitConfig, current_time: float) -> Tuple[bool, float]:
        """In-memory token bucket implementation."""
        if key not in self._token_buckets:
            self._token_buckets[key] = {
                "tokens": float(config.requests),
                "last_refill": current_time
            }
        
        bucket = self._token_buckets[key]
        
        # Calculate tokens to add
        time_passed = current_time - bucket["last_refill"]
        refill_rate = config.requests / config.window
        tokens_to_add = time_passed * refill_rate
        bucket["tokens"] = min(config.requests, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = current_time
        
        # Try to consume a token
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True, bucket["tokens"]
        else:
            return False, bucket["tokens"]
    
    def get_rate_limit_decorator(self, config_name: str, scope: str = "user"):
        """
        Create a rate limiting decorator.
        
        Args:
            config_name: Name of rate limit configuration
            scope: How to identify the client ("user", "ip", "endpoint")
            
        Returns:
            Decorator function
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Extract identifier based on scope
                identifier = self._extract_identifier(args, kwargs, scope)
                endpoint = func.__name__
                
                # Check rate limit
                result = await self.check_rate_limit(identifier, config_name, endpoint)
                
                if not result.allowed:
                    self.logger.warning(f"Rate limit exceeded for {scope}:{identifier} on {endpoint}")
                    raise RateLimitError(
                        f"Rate limit exceeded. Try again in {result.retry_after} seconds.",
                        retry_after=result.retry_after,
                        endpoint=endpoint
                    )
                
                # Log successful request
                self.logger.info(f"Rate limit check passed: {scope}:{identifier} on {endpoint}, remaining: {result.remaining}")
                
                return await func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    def _extract_identifier(self, args: tuple, kwargs: dict, scope: str) -> str:
        """Extract identifier for rate limiting based on scope."""
        if scope == "user":
            # Try to extract user from various sources
            for arg in args:
                if hasattr(arg, 'user') and hasattr(arg.user, 'key'):
                    return arg.user.key
                elif hasattr(arg, '_current_user') and hasattr(arg._current_user, 'key'):
                    return arg._current_user.key
                elif hasattr(arg, 'page') and hasattr(arg.page, 'user') and hasattr(arg.page.user, 'key'):
                    return arg.page.user.key
            
            # Check kwargs
            if 'user' in kwargs and hasattr(kwargs['user'], 'key'):
                return kwargs['user'].key
            
            return "anonymous"
        
        elif scope == "ip":
            # Try to extract IP from request context
            for arg in args:
                if hasattr(arg, 'client_ip'):
                    return arg.client_ip
                elif hasattr(arg, 'page') and hasattr(arg.page, 'client_ip'):
                    return arg.page.client_ip
            
            return "unknown_ip"
        
        elif scope == "endpoint":
            return "global"
        
        else:
            return scope  # Custom scope
    
    async def reset_rate_limit(self, identifier: str, config_name: str, endpoint: str = ""):
        """Reset rate limit for a specific identifier."""
        config = self.configs.get(config_name)
        if not config:
            return False
        
        key = self._generate_key(identifier, config, endpoint)
        
        if self.use_redis and self.redis_client:
            try:
                await self.redis_client.delete(key)
                return True
            except Exception as e:
                self.logger.error(f"Failed to reset rate limit in Redis: {e}")
        
        # Reset in memory
        if key in self._memory_store:
            del self._memory_store[key]
        if key in self._token_buckets:
            del self._token_buckets[key]
        
        return True
    
    async def get_rate_limit_status(self, identifier: str, config_name: str, endpoint: str = "") -> Optional[RateLimitResult]:
        """Get current rate limit status without consuming a request."""
        config = self.configs.get(config_name)
        if not config:
            return None
        
        key = self._generate_key(identifier, config, endpoint)
        current_time = time.time()
        
        if config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            window_start = current_time - config.window
            
            if self.use_redis and self.redis_client:
                try:
                    count = await self.redis_client.zcount(key, window_start, current_time)
                except Exception:
                    if key in self._memory_store:
                        requests = self._memory_store[key]["requests"]
                        count = len([r for r in requests if r >= window_start])
                    else:
                        count = 0
            else:
                if key in self._memory_store:
                    requests = self._memory_store[key]["requests"]
                    count = len([r for r in requests if r >= window_start])
                else:
                    count = 0
            
            remaining = max(0, config.requests - count)
            reset_time = int(current_time + config.window)
            
            return RateLimitResult(
                allowed=count < config.requests,
                remaining=remaining,
                reset_time=reset_time,
                current_usage=count
            )
        
        # For other strategies, would need similar implementation
        return None
    
    def cleanup_expired_entries(self):
        """Clean up expired entries from memory storage."""
        current_time = time.time()
        expired_keys = []
        
        for key, data in self._memory_store.items():
            if "last_cleanup" in data and current_time - data["last_cleanup"] > 3600:  # 1 hour
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._memory_store[key]
        
        # Clean token buckets that haven't been used in a while
        expired_buckets = []
        for key, data in self._token_buckets.items():
            if current_time - data["last_refill"] > 3600:  # 1 hour
                expired_buckets.append(key)
        
        for key in expired_buckets:
            del self._token_buckets[key]
        
        self.logger.info(f"Cleaned up {len(expired_keys)} expired rate limit entries and {len(expired_buckets)} token buckets")


# Global rate limiter instance
_rate_limiter = None


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


# Convenience decorators
def rate_limit_login(func):
    """Rate limit login attempts."""
    limiter = get_rate_limiter()
    return limiter.get_rate_limit_decorator("login", "ip")(func)


def rate_limit_api(func):
    """Rate limit API calls."""
    limiter = get_rate_limiter()
    return limiter.get_rate_limit_decorator("api", "user")(func)


def rate_limit_search(func):
    """Rate limit search operations."""
    limiter = get_rate_limiter()
    return limiter.get_rate_limit_decorator("search", "user")(func)


def rate_limit_export(func):
    """Rate limit data export operations."""
    limiter = get_rate_limiter()
    return limiter.get_rate_limit_decorator("export", "user")(func)


def rate_limit_form(func):
    """Rate limit form submissions."""
    limiter = get_rate_limiter()
    return limiter.get_rate_limit_decorator("form_submission", "user")(func)


def rate_limit_password_reset(func):
    """Rate limit password reset attempts."""
    limiter = get_rate_limiter()
    return limiter.get_rate_limit_decorator("password_reset", "ip")(func)


# Export rate limiting components
__all__ = [
    'RateLimitStrategy',
    'RateLimitScope',
    'RateLimitConfig',
    'RateLimitResult',
    'RateLimiter',
    'get_rate_limiter',
    'rate_limit_login',
    'rate_limit_api',
    'rate_limit_search',
    'rate_limit_export',
    'rate_limit_form',
    'rate_limit_password_reset'
]