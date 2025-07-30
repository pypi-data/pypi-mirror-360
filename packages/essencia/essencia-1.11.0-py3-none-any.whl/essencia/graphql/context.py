"""
GraphQL context for request handling.
"""
from typing import Optional, Any
from dataclasses import dataclass

from motor.motor_asyncio import AsyncIOMotorDatabase
from essencia.models import User
from essencia.cache import AsyncCache


@dataclass
class GraphQLContext:
    """Context passed to all GraphQL resolvers."""
    request: Any  # Starlette Request
    db: AsyncIOMotorDatabase
    cache: Optional[AsyncCache]
    current_user: Optional[User]
    settings: Any  # App settings
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.current_user is not None
    
    def require_auth(self):
        """Require authentication."""
        if not self.is_authenticated:
            from essencia.core import EssenciaException
            raise EssenciaException(
                "Authentication required",
                error_code="UNAUTHENTICATED",
                status_code=401
            )
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has permission."""
        if not self.current_user:
            return False
        return self.current_user.has_permission(permission)


async def get_context(request: Any, settings: Any) -> GraphQLContext:
    """Create GraphQL context from request."""
    from jose import jwt, JWTError
    
    # Get database
    db = request.app.state.db.db
    
    # Get cache if available
    cache = getattr(request.app.state, "cache", None)
    
    # Get current user from token
    current_user = None
    
    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        
        try:
            # Decode token
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=["HS256"]
            )
            
            # Get user
            user_id = payload.get("sub")
            if user_id:
                User.set_db(db)
                current_user = await User.find_by_id(user_id)
                
        except JWTError:
            pass  # Invalid token, user remains None
    
    return GraphQLContext(
        request=request,
        db=db,
        cache=cache,
        current_user=current_user,
        settings=settings
    )