"""
Dependency injection utilities for FastAPI.
"""

from typing import Optional, List, Type, Any, Callable, AsyncGenerator
from functools import wraps
from datetime import datetime

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from ..database.mongodb import MongoDB
from ..database.async_mongodb import AsyncMongoDB
from ..cache import AsyncCacheManager as CacheManager
from ..services.auth_service import AuthService
from ..models.bases import MongoModel


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)


# Database dependencies
def get_db() -> MongoDB:
    """
    Get synchronous database connection.
    
    Returns:
        MongoDB instance
    """
    return MongoDB()


async def get_async_db() -> AsyncGenerator[AsyncMongoDB, None]:
    """
    Get asynchronous database connection.
    
    Yields:
        AsyncMongoDB instance
    """
    db = AsyncMongoDB()
    try:
        yield db
    finally:
        # Cleanup if needed
        pass


# Cache dependencies
async def get_cache() -> CacheManager:
    """
    Get cache manager instance.
    
    Returns:
        CacheManager instance
    """
    return CacheManager()


# Authentication dependencies
async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncMongoDB = Depends(get_async_db)
) -> Optional[Any]:
    """
    Get current authenticated user.
    
    Args:
        request: FastAPI request object
        token: JWT token from OAuth2 scheme
        db: Database connection
        
    Returns:
        User object or None
    """
    # Check session first (for Flet apps)
    if hasattr(request.state, "session") and request.state.session:
        if user := request.state.session.get("user"):
            return user
    
    # Check token
    if not token:
        return None
    
    # Verify token and get user
    auth_service = AuthService(db)
    try:
        user = await auth_service.get_user_from_token(token)
        return user
    except Exception:
        return None


def require_auth(user: Optional[Any] = Depends(get_current_user)) -> Any:
    """
    Require authenticated user.
    
    Args:
        user: Current user from get_current_user
        
    Returns:
        Authenticated user
        
    Raises:
        HTTPException: If user is not authenticated
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_role(roles: List[str]) -> Callable:
    """
    Require user to have specific role(s).
    
    Args:
        roles: List of allowed roles
        
    Returns:
        Dependency function
    """
    def role_checker(user: Any = Depends(require_auth)) -> Any:
        if not hasattr(user, "role") or user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {roles}"
            )
        return user
    
    return role_checker


# Model dependencies
def get_model_service(model_class: Type[MongoModel]) -> Callable:
    """
    Create a dependency for model-specific services.
    
    Args:
        model_class: MongoModel subclass
        
    Returns:
        Dependency function that returns model service
    """
    async def model_service(db: AsyncMongoDB = Depends(get_async_db)):
        # Return a service instance for the model
        class ModelService:
            def __init__(self, db: AsyncMongoDB, model: Type[MongoModel]):
                self.db = db
                self.model = model
                
            async def find_one(self, filter_dict: dict) -> Optional[MongoModel]:
                """Find single document."""
                data = await self.db.find_one(
                    self.model.COLLECTION_NAME,
                    filter_dict
                )
                return self.model(**data) if data else None
                
            async def find_many(
                self,
                filter_dict: dict,
                skip: int = 0,
                limit: int = 100
            ) -> List[MongoModel]:
                """Find multiple documents."""
                cursor = self.db.find(
                    self.model.COLLECTION_NAME,
                    filter_dict
                )
                data = await cursor.skip(skip).limit(limit).to_list(None)
                return [self.model(**doc) for doc in data]
                
            async def create(self, instance: MongoModel) -> MongoModel:
                """Create new document."""
                data = instance.model_dump()
                result = await self.db.insert_one(
                    self.model.COLLECTION_NAME,
                    data
                )
                instance.id = result.inserted_id
                return instance
                
            async def update(
                self,
                filter_dict: dict,
                update_data: dict
            ) -> Optional[MongoModel]:
                """Update document."""
                result = await self.db.update_one(
                    self.model.COLLECTION_NAME,
                    filter_dict,
                    {"$set": update_data}
                )
                if result.modified_count:
                    return await self.find_one(filter_dict)
                return None
                
            async def delete(self, filter_dict: dict) -> bool:
                """Delete document."""
                result = await self.db.delete_one(
                    self.model.COLLECTION_NAME,
                    filter_dict
                )
                return result.deleted_count > 0
        
        return ModelService(db, model_class)
    
    return model_service


# Pagination dependencies
class PaginationParams:
    """Common pagination parameters."""
    
    def __init__(
        self,
        skip: int = 0,
        limit: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "desc"
    ):
        self.skip = max(0, skip)
        self.limit = min(100, max(1, limit))  # Max 100 items per page
        self.sort_by = sort_by
        self.sort_order = sort_order
        
    @property
    def page(self) -> int:
        """Calculate page number from skip/limit."""
        return (self.skip // self.limit) + 1


def get_pagination(
    skip: int = 0,
    limit: int = 20,
    sort_by: Optional[str] = None,
    sort_order: str = "desc"
) -> PaginationParams:
    """
    Get pagination parameters.
    
    Args:
        skip: Number of items to skip
        limit: Number of items to return
        sort_by: Field to sort by
        sort_order: Sort order (asc/desc)
        
    Returns:
        PaginationParams instance
    """
    return PaginationParams(skip, limit, sort_by, sort_order)


# Request context dependencies
async def get_request_context(request: Request) -> dict:
    """
    Get request context information.
    
    Args:
        request: FastAPI request
        
    Returns:
        Context dictionary
    """
    return {
        "method": request.method,
        "path": request.url.path,
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "timestamp": datetime.utcnow(),
    }