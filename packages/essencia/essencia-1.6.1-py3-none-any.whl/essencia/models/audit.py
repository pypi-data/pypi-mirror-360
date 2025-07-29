"""
Audit trail model for tracking security-relevant events.
Implements comprehensive logging per SECURITY.md requirements.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Literal
from enum import Enum

from pydantic import Field, ConfigDict

from .bases import MongoModel, StrEnum


class AuditEventType(StrEnum):
    """Types of security events to audit"""
    # Authentication events
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_LOGIN_FAILED = "user_login_failed"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    
    # Authorization events
    ROLE_MODIFICATION = "role_modification"
    PERMISSION_CHANGE = "permission_change"
    PRIVILEGE_ESCALATION_ATTEMPT = "privilege_escalation_attempt"
    
    # Data access events
    DATA_ACCESS = "data_access"
    DATA_CREATE = "data_create"
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    
    # Medical record events
    PATIENT_RECORD_ACCESS = "patient_record_access"
    PATIENT_RECORD_MODIFY = "patient_record_modify"
    PRESCRIPTION_CREATE = "prescription_create"
    PRESCRIPTION_MODIFY = "prescription_modify"
    
    # Financial events
    PAYMENT_PROCESS = "payment_process"
    PAYMENT_MODIFY = "payment_modify"
    FINANCIAL_REPORT_ACCESS = "financial_report_access"
    
    # System events
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    BACKUP_CREATE = "backup_create"
    BACKUP_RESTORE = "backup_restore"
    
    # Security events
    SECURITY_ALERT = "security_alert"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"


class AuditOutcome(StrEnum):
    """Result of the audited action"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    BLOCKED = "blocked"


class AuditLog(MongoModel):
    """
    Audit log entry for security and compliance tracking.
    
    Stores comprehensive information about security-relevant events
    including who, what, when, where, and outcome.
    """
    
    model_config = ConfigDict(
        extra='ignore',
        populate_by_name=False,
        arbitrary_types_allowed=True,
    )
    
    COLLECTION_NAME = 'audit_logs'
    
    # When - Timestamp is automatically set
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Who - User information
    user_id: Optional[str] = Field(None, description="ID of user performing action")
    user_email: Optional[str] = Field(None, description="Email of user")
    user_role: Optional[str] = Field(None, description="User role at time of action")
    
    # What - Action details
    event_type: AuditEventType = Field(..., description="Type of security event")
    action: str = Field(..., description="Specific action performed")
    resource_type: Optional[str] = Field(None, description="Type of resource accessed")
    resource_id: Optional[str] = Field(None, description="ID of resource accessed")
    
    # Where - Context information
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    session_id: Optional[str] = Field(None, description="Session identifier")
    
    # Outcome - Result of action
    outcome: AuditOutcome = Field(..., description="Result of the action")
    error_message: Optional[str] = Field(None, description="Error details if failed")
    
    # Additional context
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional event data")
    
    # Compliance fields
    data_classification: Optional[str] = Field(None, description="Sensitivity level of accessed data")
    compliance_flags: list[str] = Field(default_factory=list, description="Compliance markers (LGPD, HIPAA)")
    
    @classmethod
    def create_log(
        cls,
        event_type: AuditEventType,
        action: str,
        outcome: AuditOutcome,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        user_role: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        data_classification: Optional[str] = None,
        compliance_flags: Optional[list[str]] = None
    ) -> 'AuditLog':
        """
        Factory method to create and save an audit log entry.
        
        Args:
            event_type: Type of security event
            action: Specific action performed
            outcome: Result of the action
            **kwargs: Additional audit fields
            
        Returns:
            Saved AuditLog instance
        """
        log = cls(
            event_type=event_type,
            action=action,
            outcome=outcome,
            user_id=user_id,
            user_email=user_email,
            user_role=user_role,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            error_message=error_message,
            metadata=metadata or {},
            data_classification=data_classification,
            compliance_flags=compliance_flags or []
        )
        
        # Save to database
        return log.save_self()
    
    @classmethod
    def find_by_user(cls, user_id: str, limit: int = 100) -> list['AuditLog']:
        """Find audit logs for a specific user."""
        return cls.find(
            {'user_id': user_id},
            sort=[('timestamp', -1)],
            limit=limit
        )
    
    @classmethod
    def find_by_resource(
        cls,
        resource_type: str,
        resource_id: str,
        limit: int = 100
    ) -> list['AuditLog']:
        """Find audit logs for a specific resource."""
        return cls.find(
            {
                'resource_type': resource_type,
                'resource_id': resource_id
            },
            sort=[('timestamp', -1)],
            limit=limit
        )
    
    @classmethod
    def find_by_event_type(
        cls,
        event_type: AuditEventType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> list['AuditLog']:
        """Find audit logs by event type within date range."""
        query = {'event_type': event_type}
        
        if start_date or end_date:
            query['timestamp'] = {}
            if start_date:
                query['timestamp']['$gte'] = start_date
            if end_date:
                query['timestamp']['$lte'] = end_date
        
        return cls.find(
            query,
            sort=[('timestamp', -1)],
            limit=limit
        )
    
    @classmethod
    def find_failed_logins(
        cls,
        user_email: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> list['AuditLog']:
        """Find failed login attempts."""
        query = {
            'event_type': AuditEventType.USER_LOGIN_FAILED,
            'timestamp': {
                '$gte': datetime.utcnow() - timedelta(hours=hours)
            }
        }
        
        if user_email:
            query['user_email'] = user_email
        
        return cls.find(
            query,
            sort=[('timestamp', -1)],
            limit=limit
        )
    
    @classmethod
    def find_suspicious_activity(
        cls,
        hours: int = 24,
        limit: int = 100
    ) -> list['AuditLog']:
        """Find suspicious activity events."""
        return cls.find(
            {
                'event_type': {
                    '$in': [
                        AuditEventType.SUSPICIOUS_ACTIVITY,
                        AuditEventType.PRIVILEGE_ESCALATION_ATTEMPT,
                        AuditEventType.RATE_LIMIT_EXCEEDED
                    ]
                },
                'timestamp': {
                    '$gte': datetime.utcnow() - timedelta(hours=hours)
                }
            },
            sort=[('timestamp', -1)],
            limit=limit
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary."""
        return {
            'key': self.key,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'user_role': self.user_role,
            'event_type': self.event_type,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'session_id': self.session_id,
            'outcome': self.outcome,
            'error_message': self.error_message,
            'metadata': self.metadata,
            'data_classification': self.data_classification,
            'compliance_flags': self.compliance_flags
        }
    
    def to_log_format(self) -> str:
        """Format audit log for standard log output."""
        parts = [
            f"[{self.timestamp.isoformat()}]",
            f"EVENT={self.event_type}",
            f"ACTION={self.action}",
            f"USER={self.user_email or self.user_id or 'anonymous'}",
            f"RESOURCE={self.resource_type}:{self.resource_id}" if self.resource_type else "",
            f"IP={self.ip_address or 'unknown'}",
            f"OUTCOME={self.outcome}"
        ]
        
        if self.error_message:
            parts.append(f"ERROR={self.error_message}")
        
        return " ".join(filter(None, parts))
    
    def __str__(self) -> str:
        """String representation for logging."""
        return self.to_log_format()


# Convenience functions for common audit operations

def audit_login(user_email: str, user_id: str, user_role: str, ip_address: str, success: bool) -> AuditLog:
    """Audit a login attempt."""
    return AuditLog.create_log(
        event_type=AuditEventType.USER_LOGIN if success else AuditEventType.USER_LOGIN_FAILED,
        action=f"User login {'succeeded' if success else 'failed'}",
        outcome=AuditOutcome.SUCCESS if success else AuditOutcome.FAILURE,
        user_id=user_id if success else None,
        user_email=user_email,
        user_role=user_role if success else None,
        ip_address=ip_address
    )


def audit_data_access(
    user_id: str,
    user_email: str,
    user_role: str,
    resource_type: str,
    resource_id: str,
    action: str,
    ip_address: Optional[str] = None,
    data_classification: Optional[str] = None
) -> AuditLog:
    """Audit data access event."""
    return AuditLog.create_log(
        event_type=AuditEventType.DATA_ACCESS,
        action=action,
        outcome=AuditOutcome.SUCCESS,
        user_id=user_id,
        user_email=user_email,
        user_role=user_role,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        data_classification=data_classification,
        compliance_flags=['LGPD'] if data_classification == 'sensitive' else []
    )


def audit_patient_access(
    user_id: str,
    user_email: str,
    user_role: str,
    patient_id: str,
    action: str,
    ip_address: Optional[str] = None
) -> AuditLog:
    """Audit patient record access."""
    return AuditLog.create_log(
        event_type=AuditEventType.PATIENT_RECORD_ACCESS,
        action=action,
        outcome=AuditOutcome.SUCCESS,
        user_id=user_id,
        user_email=user_email,
        user_role=user_role,
        resource_type='patient',
        resource_id=patient_id,
        ip_address=ip_address,
        data_classification='highly_sensitive',
        compliance_flags=['LGPD', 'HIPAA']
    )