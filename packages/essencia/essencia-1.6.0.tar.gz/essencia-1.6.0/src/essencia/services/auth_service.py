"""Authentication service."""

import hashlib
try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False
import secrets
from typing import Optional

from essencia.models import User
from essencia.services.user_service import UserService
from essencia.core.exceptions import ValidationError


class AuthService:
    """Service for authentication."""
    
    def __init__(self, user_service: UserService):
        """Initialize auth service.
        
        Args:
            user_service: User service instance
        """
        self.user_service = user_service
        
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt if available, otherwise SHA256.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        if HAS_BCRYPT:
            # Use bcrypt for secure password hashing
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        else:
            # Fallback to SHA256 (not recommended for production)
            import warnings
            warnings.warn(
                "bcrypt not installed. Using SHA256 for password hashing. "
                "Install with: pip install essencia[security]",
                RuntimeWarning,
                stacklevel=2
            )
            return f"hashed_{hashlib.sha256(password.encode()).hexdigest()}"
        
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash.
        
        Args:
            password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password matches
        """
        if HAS_BCRYPT and hashed_password.startswith('$2'):
            # Verify bcrypt hash
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        else:
            # Fallback to SHA256 verification (for legacy or non-bcrypt hashes)
            return self._hash_password(password) == hashed_password
        
    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user.
        
        Args:
            username: Username or email
            password: Password
            
        Returns:
            User if authenticated
        """
        # Try to find user by username or email
        user = await self.user_service.get_user_by_username(username)
        if not user:
            user = await self.user_service.get_user_by_email(username)
            
        if not user:
            return None
            
        # Verify password
        if not self._verify_password(password, user.hashed_password):
            return None
            
        # Check if user is active
        if not user.is_active:
            raise ValidationError("User account is deactivated")
            
        return user
        
    def generate_token(self) -> str:
        """Generate a secure token.
        
        Returns:
            Secure token
        """
        return secrets.token_urlsafe(32)