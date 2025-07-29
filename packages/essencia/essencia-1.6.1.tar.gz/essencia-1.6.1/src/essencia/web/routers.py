"""
Base router classes for FastAPI.
"""

from typing import Type, Optional, List, Dict, Any, Callable
from abc import ABC, abstractmethod

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..models.bases import MongoModel
from .dependencies import (
    get_async_db,
    get_current_user,
    require_auth,
    get_model_service,
    PaginationParams,
    get_pagination,
)
from .exceptions import ValidationException, PermissionException


class BaseRouter(ABC):
    """
    Abstract base router class.
    """
    
    def __init__(
        self,
        prefix: str = "",
        tags: Optional[List[str]] = None,
        dependencies: Optional[List[Depends]] = None
    ):
        self.router = APIRouter(
            prefix=prefix,
            tags=tags or [],
            dependencies=dependencies or []
        )
        self.setup_routes()
    
    @abstractmethod
    def setup_routes(self) -> None:
        """Setup router routes. Must be implemented by subclasses."""
        pass
    
    def get_router(self) -> APIRouter:
        """Get the configured router."""
        return self.router


class CRUDRouter(BaseRouter):
    """
    Generic CRUD router for MongoModel subclasses.
    
    Provides standard CRUD operations:
    - GET /items - List items with pagination
    - GET /items/{id} - Get single item
    - POST /items - Create new item
    - PUT /items/{id} - Update item
    - DELETE /items/{id} - Delete item
    """
    
    model_class: Type[MongoModel]
    create_schema: Optional[Type[BaseModel]] = None
    update_schema: Optional[Type[BaseModel]] = None
    response_schema: Optional[Type[BaseModel]] = None
    
    def __init__(
        self,
        model_class: Type[MongoModel],
        prefix: Optional[str] = None,
        tags: Optional[List[str]] = None,
        require_authentication: bool = True,
        **kwargs
    ):
        self.model_class = model_class
        
        # Set default prefix based on collection name
        if prefix is None:
            prefix = f"/{model_class.COLLECTION_NAME}"
            
        # Set default tags
        if tags is None:
            tags = [model_class.COLLECTION_NAME]
        
        # Add authentication dependency if required
        dependencies = kwargs.get("dependencies", [])
        if require_authentication:
            dependencies.append(Depends(require_auth))
        kwargs["dependencies"] = dependencies
        
        super().__init__(prefix=prefix, tags=tags, **kwargs)
    
    def setup_routes(self) -> None:
        """Setup CRUD routes."""
        
        @self.router.get("/", response_model=List[self.response_schema or Dict[str, Any]])
        async def list_items(
            pagination: PaginationParams = Depends(get_pagination),
            search: Optional[str] = Query(None, description="Search query"),
            filters: Optional[str] = Query(None, description="JSON filter string"),
            service=Depends(get_model_service(self.model_class))
        ):
            """List items with pagination."""
            # Parse filters
            filter_dict = {}
            if filters:
                try:
                    import json
                    filter_dict = json.loads(filters)
                except Exception:
                    raise ValidationException("Invalid filter format")
            
            # Add search if provided
            if search and hasattr(self.model_class, "search_fields"):
                search_conditions = []
                for field in self.model_class.search_fields:
                    search_conditions.append({
                        field: {"$regex": search, "$options": "i"}
                    })
                filter_dict["$or"] = search_conditions
            
            # Get items
            items = await service.find_many(
                filter_dict,
                skip=pagination.skip,
                limit=pagination.limit
            )
            
            return [item.model_dump() for item in items]
        
        @self.router.get("/{item_id}")
        async def get_item(
            item_id: str = Path(..., description="Item ID"),
            service=Depends(get_model_service(self.model_class))
        ):
            """Get single item by ID."""
            item = await service.find_one({"_id": item_id})
            if not item:
                raise HTTPException(status_code=404, detail="Item not found")
            return item.model_dump()
        
        @self.router.post("/", status_code=201)
        async def create_item(
            data: self.create_schema or Dict[str, Any] = Body(...),
            current_user=Depends(get_current_user),
            service=Depends(get_model_service(self.model_class))
        ):
            """Create new item."""
            # Convert schema to dict if needed
            if isinstance(data, BaseModel):
                data = data.model_dump()
            
            # Add creator if model supports it
            if hasattr(self.model_class, "creator") and current_user:
                data["creator"] = str(current_user.id)
            
            # Create instance
            try:
                instance = self.model_class(**data)
            except Exception as e:
                raise ValidationException(f"Invalid data: {e}")
            
            # Save to database
            saved = await service.create(instance)
            return saved.model_dump()
        
        @self.router.put("/{item_id}")
        async def update_item(
            item_id: str = Path(..., description="Item ID"),
            data: self.update_schema or Dict[str, Any] = Body(...),
            current_user=Depends(get_current_user),
            service=Depends(get_model_service(self.model_class))
        ):
            """Update existing item."""
            # Check if item exists
            existing = await service.find_one({"_id": item_id})
            if not existing:
                raise HTTPException(status_code=404, detail="Item not found")
            
            # Check permissions if needed
            if hasattr(existing, "creator") and current_user:
                if str(existing.creator) != str(current_user.id):
                    if not getattr(current_user, "is_admin", False):
                        raise PermissionException("You can only update your own items")
            
            # Convert schema to dict if needed
            if isinstance(data, BaseModel):
                data = data.model_dump()
            
            # Update item
            updated = await service.update({"_id": item_id}, data)
            if not updated:
                raise HTTPException(status_code=500, detail="Update failed")
            
            return updated.model_dump()
        
        @self.router.delete("/{item_id}", status_code=204)
        async def delete_item(
            item_id: str = Path(..., description="Item ID"),
            current_user=Depends(get_current_user),
            service=Depends(get_model_service(self.model_class))
        ):
            """Delete item."""
            # Check if item exists
            existing = await service.find_one({"_id": item_id})
            if not existing:
                raise HTTPException(status_code=404, detail="Item not found")
            
            # Check permissions if needed
            if hasattr(existing, "creator") and current_user:
                if str(existing.creator) != str(current_user.id):
                    if not getattr(current_user, "is_admin", False):
                        raise PermissionException("You can only delete your own items")
            
            # Delete item
            deleted = await service.delete({"_id": item_id})
            if not deleted:
                raise HTTPException(status_code=500, detail="Delete failed")
            
            return None


class AuthRouter(BaseRouter):
    """
    Authentication router providing login/logout endpoints.
    """
    
    def setup_routes(self) -> None:
        """Setup authentication routes."""
        
        @self.router.post("/login")
        async def login(
            username: str = Body(...),
            password: str = Body(...),
            db=Depends(get_async_db)
        ):
            """Login endpoint."""
            # This is a placeholder - implement with your auth service
            from ..services.auth_service import AuthService
            
            auth_service = AuthService(db)
            result = await auth_service.authenticate(username, password)
            
            if not result:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid credentials"
                )
            
            return result
        
        @self.router.post("/logout")
        async def logout(current_user=Depends(require_auth)):
            """Logout endpoint."""
            # Implement logout logic (e.g., invalidate token)
            return {"message": "Logged out successfully"}
        
        @self.router.get("/me")
        async def get_current_user_info(current_user=Depends(require_auth)):
            """Get current user information."""
            return current_user.model_dump()
        
        @self.router.post("/refresh")
        async def refresh_token(
            refresh_token: str = Body(...),
            db=Depends(get_async_db)
        ):
            """Refresh access token."""
            from ..services.auth_service import AuthService
            
            auth_service = AuthService(db)
            result = await auth_service.refresh_token(refresh_token)
            
            if not result:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid refresh token"
                )
            
            return result