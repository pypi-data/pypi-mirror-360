"""Session service for managing user sessions."""

from typing import Optional
from datetime import datetime, timedelta

from essencia.database import RedisClient
from essencia.models import Session, User
from essencia.services.auth_service import AuthService


class SessionService:
    """Service for session management."""
    
    def __init__(self, redis_client: RedisClient, auth_service: AuthService):
        """Initialize session service.
        
        Args:
            redis_client: Redis client instance
            auth_service: Auth service instance
        """
        self.redis = redis_client
        self.auth_service = auth_service
        self.session_prefix = "session:"
        self.user_sessions_prefix = "user_sessions:"
        
    async def create_session(
        self,
        user: User,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        ttl_hours: int = 24
    ) -> Session:
        """Create a new session.
        
        Args:
            user: User object
            user_agent: User agent string
            ip_address: IP address
            ttl_hours: Session TTL in hours
            
        Returns:
            Created session
        """
        # Generate session
        session = Session(
            user_id=user.key,
            token=self.auth_service.generate_token(),
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.utcnow() + timedelta(hours=ttl_hours)
        )
        
        # Store session in Redis
        session_key = f"{self.session_prefix}{session.token}"
        ttl_seconds = ttl_hours * 3600
        
        await self.redis.set_json(
            session_key,
            session.model_dump(mode="json"),
            ttl=ttl_seconds
        )
        
        # Add to user's session list
        user_sessions_key = f"{self.user_sessions_prefix}{user.key}"
        await self.redis.hset(
            user_sessions_key,
            session.token,
            datetime.utcnow().isoformat()
        )
        await self.redis.expire(user_sessions_key, ttl_seconds)
        
        return session
        
    async def get_session(self, token: str) -> Optional[Session]:
        """Get session by token.
        
        Args:
            token: Session token
            
        Returns:
            Session if found and valid
        """
        session_key = f"{self.session_prefix}{token}"
        session_data = await self.redis.get_json(session_key)
        
        if not session_data:
            return None
            
        session = Session(**session_data)
        
        # Check if expired
        if session.is_expired():
            await self.delete_session(token)
            return None
            
        return session
        
    async def refresh_session(self, token: str, ttl_hours: int = 24) -> Optional[Session]:
        """Refresh session expiration.
        
        Args:
            token: Session token
            ttl_hours: New TTL in hours
            
        Returns:
            Updated session if found
        """
        session = await self.get_session(token)
        
        if not session:
            return None
            
        # Update expiration
        session.expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
        session.updated_at = datetime.utcnow()
        
        # Update in Redis
        session_key = f"{self.session_prefix}{token}"
        ttl_seconds = ttl_hours * 3600
        
        await self.redis.set_json(
            session_key,
            session.model_dump(mode="json"),
            ttl=ttl_seconds
        )
        
        return session
        
    async def delete_session(self, token: str) -> bool:
        """Delete session.
        
        Args:
            token: Session token
            
        Returns:
            True if deleted
        """
        session = await self.get_session(token)
        
        if not session:
            return False
            
        # Delete from Redis
        session_key = f"{self.session_prefix}{token}"
        await self.redis.delete(session_key)
        
        # Remove from user's session list
        user_sessions_key = f"{self.user_sessions_prefix}{session.user_id}"
        await self.redis.hdel(user_sessions_key, token)
        
        return True
        
    async def delete_user_sessions(self, user_id: str) -> int:
        """Delete all sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of sessions deleted
        """
        user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
        sessions = await self.redis.hgetall(user_sessions_key)
        
        deleted = 0
        for token in sessions:
            if await self.delete_session(token):
                deleted += 1
                
        return deleted
        
    async def get_user_sessions(self, user_id: str) -> list[Session]:
        """Get all active sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of active sessions
        """
        user_sessions_key = f"{self.user_sessions_prefix}{user_id}"
        session_tokens = await self.redis.hgetall(user_sessions_key)
        
        sessions = []
        for token in session_tokens:
            session = await self.get_session(token)
            if session:
                sessions.append(session)
                
        return sessions