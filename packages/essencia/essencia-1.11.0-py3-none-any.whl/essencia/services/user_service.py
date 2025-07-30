"""User service for managing users."""

from typing import List, Optional
from datetime import datetime

from essencia.database import MongoDB
from essencia.models import User, UserCreate, UserUpdate
from essencia.core.exceptions import ValidationError


class UserService:
    """Service for user management."""
    
    def __init__(self, db: MongoDB):
        """Initialize user service.
        
        Args:
            db: MongoDB instance
        """
        self.db = db
        self.collection = "users"
        
    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user.
        
        Args:
            user_create: User creation data
            
        Returns:
            Created user
            
        Raises:
            ValidationError: If user already exists
        """
        # Check if user already exists
        existing = await self.db.find_one(
            self.collection,
            {"$or": [
                {"username": user_create.username},
                {"email": user_create.email}
            ]}
        )
        
        if existing:
            raise ValidationError("User with this username or email already exists")
            
        # Create user document
        user_dict = user_create.model_dump()
        # Hash password (in real app, use proper hashing)
        user_dict["hashed_password"] = f"hashed_{user_dict.pop('password')}"
        user_dict["created_at"] = datetime.utcnow()
        user_dict["updated_at"] = datetime.utcnow()
        
        # Insert user
        user_id = await self.db.insert_one(self.collection, user_dict)
        user_dict["key"] = user_id
        
        return User(**user_dict)
        
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User if found
        """
        user_dict = await self.db.find_one(
            self.collection,
            {"key": user_id}
        )
        
        if user_dict:
            return User(**user_dict)
        return None
        
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username.
        
        Args:
            username: Username
            
        Returns:
            User if found
        """
        user_dict = await self.db.find_one(
            self.collection,
            {"username": username}
        )
        
        if user_dict:
            return User(**user_dict)
        return None
        
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email.
        
        Args:
            email: Email address
            
        Returns:
            User if found
        """
        user_dict = await self.db.find_one(
            self.collection,
            {"email": email}
        )
        
        if user_dict:
            return User(**user_dict)
        return None
        
    async def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Update user.
        
        Args:
            user_id: User ID
            user_update: Update data
            
        Returns:
            Updated user if found
        """
        update_dict = user_update.model_dump(exclude_unset=True)
        
        if not update_dict:
            return await self.get_user(user_id)
            
        # Handle password update
        if "password" in update_dict:
            update_dict["hashed_password"] = f"hashed_{update_dict.pop('password')}"
            
        update_dict["updated_at"] = datetime.utcnow()
        
        # Update user
        modified = await self.db.update_one(
            self.collection,
            {"key": user_id},
            update_dict
        )
        
        if modified:
            return await self.get_user(user_id)
        return None
        
    async def delete_user(self, user_id: str) -> bool:
        """Delete user.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted
        """
        deleted = await self.db.delete_one(
            self.collection,
            {"key": user_id}
        )
        return deleted > 0
        
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 10,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """List users.
        
        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return
            is_active: Filter by active status
            
        Returns:
            List of users
        """
        filter_dict = {}
        if is_active is not None:
            filter_dict["is_active"] = is_active
            
        user_dicts = await self.db.find_many(
            self.collection,
            filter_dict,
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)]
        )
        
        return [User(**user_dict) for user_dict in user_dicts]
        
    async def count_users(self, is_active: Optional[bool] = None) -> int:
        """Count users.
        
        Args:
            is_active: Filter by active status
            
        Returns:
            User count
        """
        filter_dict = {}
        if is_active is not None:
            filter_dict["is_active"] = is_active
            
        return await self.db.count_documents(self.collection, filter_dict)