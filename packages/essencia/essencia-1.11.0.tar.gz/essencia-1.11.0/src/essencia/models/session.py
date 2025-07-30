"""Session model for user sessions."""

from datetime import datetime, timedelta
from typing import Optional

from pydantic import Field

from .base import BaseModel


class Session(BaseModel):
    """User session model."""
    
    user_id: str = Field(..., description="User ID")
    token: str = Field(..., description="Session token")
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(hours=24),
        description="Session expiration time"
    )
    is_active: bool = Field(True, description="Is session active")
    user_agent: Optional[str] = Field(None, description="User agent string")
    ip_address: Optional[str] = Field(None, description="IP address")
    
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at