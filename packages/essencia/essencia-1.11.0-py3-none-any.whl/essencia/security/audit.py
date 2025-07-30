"""
Audit logging for security events.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AuditEventType(str, Enum):
    """Types of audit events."""
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    API_ACCESS = "API_ACCESS"
    DATA_ACCESS = "DATA_ACCESS"
    DATA_MODIFICATION = "DATA_MODIFICATION"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    SECURITY_ALERT = "SECURITY_ALERT"


class AuditLogger:
    """
    Simple audit logger for security events.
    """
    
    def __init__(self, logger_name: str = "essencia.audit"):
        self.logger = logging.getLogger(logger_name)
        
    async def log_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True
    ) -> None:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event
            user_id: User ID (if authenticated)
            resource: Resource being accessed
            details: Additional event details
            success: Whether the action was successful
        """
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "resource": resource,
            "success": success,
            "details": details or {}
        }
        
        if success:
            self.logger.info(f"Audit: {event_type} - {resource}", extra=event)
        else:
            self.logger.warning(f"Audit: {event_type} FAILED - {resource}", extra=event)
            
    def log_login(self, user_id: str, success: bool = True, details: Optional[Dict[str, Any]] = None):
        """Log login attempt."""
        return self.log_event(
            AuditEventType.LOGIN,
            user_id=user_id,
            success=success,
            details=details
        )
        
    def log_logout(self, user_id: str):
        """Log logout."""
        return self.log_event(
            AuditEventType.LOGOUT,
            user_id=user_id
        )
        
    def log_api_access(self, user_id: Optional[str], resource: str, details: Optional[Dict[str, Any]] = None):
        """Log API access."""
        return self.log_event(
            AuditEventType.API_ACCESS,
            user_id=user_id,
            resource=resource,
            details=details
        )
        
    def log_permission_denied(self, user_id: Optional[str], resource: str, required_permission: str):
        """Log permission denied event."""
        return self.log_event(
            AuditEventType.PERMISSION_DENIED,
            user_id=user_id,
            resource=resource,
            success=False,
            details={"required_permission": required_permission}
        )


# Global audit logger instance
_audit_logger = AuditLogger()


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance."""
    return _audit_logger