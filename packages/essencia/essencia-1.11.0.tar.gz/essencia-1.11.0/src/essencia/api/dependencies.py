"""
FastAPI dependencies for the API.
"""
from typing import Optional, Annotated
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorDatabase

from essencia.models import User
from essencia.cache import AsyncCache


# Security scheme
security = HTTPBearer()


async def get_db(request: Request) -> AsyncIOMotorDatabase:
    """Get database connection."""
    return request.app.state.db.db


async def get_cache(request: Request) -> Optional[AsyncCache]:
    """Get cache connection."""
    return getattr(request.app.state, "cache", None)


async def decode_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    request: Request
) -> dict:
    """Decode and validate JWT token."""
    token = credentials.credentials
    settings = request.app.state.settings
    
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token_data: Annotated[dict, Depends(decode_token)],
    db: Annotated[AsyncIOMotorDatabase, Depends(get_db)]
) -> User:
    """Get current authenticated user."""
    user_id = token_data.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database
    User.set_db(db)
    user = await User.find_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


def require_permission(permission: str):
    """Require specific permission for endpoint."""
    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ):
        if not current_user.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission}"
            )
        return current_user
    
    return permission_checker


def require_role(role: str):
    """Require specific role for endpoint."""
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)]
    ):
        if current_user.role != role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role}"
            )
        return current_user
    
    return role_checker


class RateLimitDep:
    """Rate limiting dependency."""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def __call__(
        self,
        request: Request,
        current_user: Annotated[User, Depends(get_current_user)],
        cache: Annotated[Optional[AsyncCache], Depends(get_cache)]
    ):
        if not cache:
            return  # Skip rate limiting if no cache
        
        # Create rate limit key
        key = f"rate_limit:{current_user.id}:{request.url.path}"
        
        # Get current count
        count = await cache.get(key)
        if count is None:
            count = 0
        else:
            count = int(count)
        
        # Check limit
        if count >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded",
                headers={
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(datetime.now().timestamp()) + self.window_seconds)
                }
            )
        
        # Increment counter
        await cache.set(key, count + 1, ttl=self.window_seconds)
        
        # Add headers to response
        request.state.rate_limit_headers = {
            "X-RateLimit-Limit": str(self.max_requests),
            "X-RateLimit-Remaining": str(self.max_requests - count - 1),
            "X-RateLimit-Reset": str(int(datetime.now().timestamp()) + self.window_seconds)
        }


def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """Create rate limit dependency."""
    return Depends(RateLimitDep(max_requests, window_seconds))


# Pagination dependencies
async def pagination_params(
    skip: int = 0,
    limit: int = 100
) -> dict:
    """Common pagination parameters."""
    return {"skip": skip, "limit": min(limit, 1000)}


# Sorting dependencies
async def sorting_params(
    sort_by: Optional[str] = None,
    sort_order: str = "asc"
) -> dict:
    """Common sorting parameters."""
    if sort_by:
        order = -1 if sort_order.lower() == "desc" else 1
        return {"sort": [(sort_by, order)]}
    return {}


# Filter dependencies
def create_filter_dependency(allowed_fields: list[str]):
    """Create filter dependency for specific fields."""
    async def filter_params(request: Request) -> dict:
        filters = {}
        for field in allowed_fields:
            value = request.query_params.get(field)
            if value is not None:
                filters[field] = value
        return filters
    
    return filter_params