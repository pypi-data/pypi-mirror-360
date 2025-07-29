"""
Authorization framework for role-based access control (RBAC).

Provides comprehensive permission management for the Essência system:
- Role-based access control with granular permissions
- Method-level authorization decorators
- Resource-specific permission checking
- Audit logging for security events
"""

import logging
from typing import Dict, List, Optional, Set, Any, Callable
from functools import wraps
from enum import Enum

logger = logging.getLogger(__name__)


class AuthorizationError(Exception):
    """Authorization error."""
    pass


class SecurityError(Exception):
    """Security error."""
    pass


class Role(str, Enum):
    """System roles with hierarchical privileges."""
    ADMIN = "admin"
    DOCTOR = "doctor"
    THERAPIST = "therapist"
    RECEPTION = "reception"
    EMPLOYEE = "employee"


class Permission(str, Enum):
    """Granular system permissions."""
    # Patient permissions
    PATIENT_VIEW = "patient.view"
    PATIENT_EDIT = "patient.edit"
    PATIENT_CREATE = "patient.create"
    PATIENT_DELETE = "patient.delete"
    
    # Medical record permissions
    MEDICAL_RECORD_VIEW = "medical_record.view"
    MEDICAL_RECORD_EDIT = "medical_record.edit"
    MEDICAL_RECORD_CREATE = "medical_record.create"
    MEDICAL_RECORD_DELETE = "medical_record.delete"
    
    # Financial permissions
    FINANCIAL_VIEW = "financial.view"
    FINANCIAL_EDIT = "financial.edit"
    FINANCIAL_CREATE = "financial.create"
    FINANCIAL_DELETE = "financial.delete"
    
    # Appointment permissions
    APPOINTMENT_VIEW = "appointment.view"
    APPOINTMENT_EDIT = "appointment.edit"
    APPOINTMENT_CREATE = "appointment.create"
    APPOINTMENT_DELETE = "appointment.delete"
    
    # System administration permissions
    USER_MANAGEMENT = "user.management"
    SYSTEM_CONFIG = "system.config"
    AUDIT_VIEW = "audit.view"
    
    # Prescription permissions
    PRESCRIPTION_VIEW = "prescription.view"
    PRESCRIPTION_EDIT = "prescription.edit"
    PRESCRIPTION_CREATE = "prescription.create"
    
    # Report permissions
    REPORT_VIEW = "report.view"
    REPORT_GENERATE = "report.generate"


class PermissionManager:
    """
    Centralized permission management system.
    
    Implements role-based access control with granular permissions
    and resource-specific authorization.
    """
    
    # Role-to-permissions mapping
    ROLE_PERMISSIONS: Dict[Role, Set[Permission]] = {
        Role.ADMIN: {
            # Admin has all permissions
            Permission.PATIENT_VIEW, Permission.PATIENT_EDIT, Permission.PATIENT_CREATE, Permission.PATIENT_DELETE,
            Permission.MEDICAL_RECORD_VIEW, Permission.MEDICAL_RECORD_EDIT, Permission.MEDICAL_RECORD_CREATE, Permission.MEDICAL_RECORD_DELETE,
            Permission.FINANCIAL_VIEW, Permission.FINANCIAL_EDIT, Permission.FINANCIAL_CREATE, Permission.FINANCIAL_DELETE,
            Permission.APPOINTMENT_VIEW, Permission.APPOINTMENT_EDIT, Permission.APPOINTMENT_CREATE, Permission.APPOINTMENT_DELETE,
            Permission.USER_MANAGEMENT, Permission.SYSTEM_CONFIG, Permission.AUDIT_VIEW,
            Permission.PRESCRIPTION_VIEW, Permission.PRESCRIPTION_EDIT, Permission.PRESCRIPTION_CREATE,
            Permission.REPORT_VIEW, Permission.REPORT_GENERATE
        },
        
        Role.DOCTOR: {
            # Doctor permissions for medical practice
            Permission.PATIENT_VIEW, Permission.PATIENT_EDIT, Permission.PATIENT_CREATE,
            Permission.MEDICAL_RECORD_VIEW, Permission.MEDICAL_RECORD_EDIT, Permission.MEDICAL_RECORD_CREATE,
            Permission.APPOINTMENT_VIEW, Permission.APPOINTMENT_EDIT, Permission.APPOINTMENT_CREATE,
            Permission.PRESCRIPTION_VIEW, Permission.PRESCRIPTION_EDIT, Permission.PRESCRIPTION_CREATE,
            Permission.REPORT_VIEW
        },
        
        Role.THERAPIST: {
            # Therapist permissions for therapy sessions
            Permission.PATIENT_VIEW, Permission.PATIENT_EDIT,
            Permission.MEDICAL_RECORD_VIEW, Permission.MEDICAL_RECORD_EDIT, Permission.MEDICAL_RECORD_CREATE,
            Permission.APPOINTMENT_VIEW, Permission.APPOINTMENT_EDIT, Permission.APPOINTMENT_CREATE,
            Permission.REPORT_VIEW
        },
        
        Role.RECEPTION: {
            # Reception permissions for front desk operations
            Permission.PATIENT_VIEW, Permission.PATIENT_EDIT, Permission.PATIENT_CREATE,
            Permission.APPOINTMENT_VIEW, Permission.APPOINTMENT_EDIT, Permission.APPOINTMENT_CREATE,
            Permission.FINANCIAL_VIEW, Permission.FINANCIAL_EDIT, Permission.FINANCIAL_CREATE,
            Permission.REPORT_VIEW
        },
        
        Role.EMPLOYEE: {
            # General employee permissions
            Permission.PATIENT_VIEW, Permission.PATIENT_EDIT, Permission.PATIENT_CREATE,
            Permission.APPOINTMENT_VIEW, Permission.APPOINTMENT_EDIT, Permission.APPOINTMENT_CREATE,
            Permission.FINANCIAL_VIEW, Permission.FINANCIAL_EDIT, Permission.FINANCIAL_CREATE,
            Permission.REPORT_VIEW
        }
    }
    
    def __init__(self):
        """Initialize permission manager."""
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def get_user_permissions(self, user: Any) -> Set[Permission]:
        """
        Get all permissions for a user based on their role.
        
        Args:
            user: User object with role information
            
        Returns:
            Set of permissions the user has
        """
        if not user or not hasattr(user, 'role'):
            return set()
        
        try:
            role = Role(user.role.lower())
            return self.ROLE_PERMISSIONS.get(role, set())
        except ValueError:
            self.logger.warning(f"Unknown role: {user.role}")
            return set()
    
    def has_permission(self, user: Any, permission: Permission, resource_id: Optional[str] = None) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            user: User to check permissions for
            permission: Permission to check
            resource_id: Optional resource identifier for resource-specific checks
            
        Returns:
            True if user has permission, False otherwise
        """
        if not user:
            return False
        
        # Admin users have all permissions
        if hasattr(user, 'admin') and user.admin:
            self.logger.info(f"Admin user {user.email} granted permission {permission}")
            return True
        
        user_permissions = self.get_user_permissions(user)
        has_perm = permission in user_permissions
        
        # Resource-specific authorization logic
        if has_perm and resource_id:
            has_perm = self._check_resource_access(user, permission, resource_id)
        
        # Log authorization check
        self.logger.info(f"Permission check: user={user.email if hasattr(user, 'email') else 'unknown'}, permission={permission}, resource={resource_id}, granted={has_perm}")
        
        return has_perm
    
    def _check_resource_access(self, user: Any, permission: Permission, resource_id: str) -> bool:
        """
        Check resource-specific access rules.
        
        Args:
            user: User requesting access
            permission: Permission being checked
            resource_id: Resource identifier
            
        Returns:
            True if user has access to the specific resource
        """
        # Doctors and therapists can only access their assigned patients
        if permission in [Permission.PATIENT_VIEW, Permission.PATIENT_EDIT, Permission.MEDICAL_RECORD_VIEW, Permission.MEDICAL_RECORD_EDIT]:
            if hasattr(user, 'role') and user.role.lower() in ['doctor', 'therapist']:
                # TODO: Implement patient assignment logic
                # For now, allow access (will be enhanced with patient assignment system)
                return True
        
        # Default: allow access if user has the permission
        return True
    
    def require_permission(self, permission: Permission, resource_id: Optional[str] = None):
        """
        Decorator to require specific permission for method access.
        
        Args:
            permission: Required permission
            resource_id: Optional resource identifier
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                # Get user from page context (Flet-specific)
                user = getattr(self, '_current_user', None)
                if not user and hasattr(self, 'page'):
                    user = getattr(self.page, 'user', None)
                
                if not user:
                    raise AuthorizationError(f"Authentication required for {func.__name__}")
                
                if not self.has_permission(user, permission, resource_id):
                    raise AuthorizationError(f"Permission {permission} required for {func.__name__}")
                
                return func(self, *args, **kwargs)
            return wrapper
        return decorator
    
    def check_multiple_permissions(self, user: Any, permissions: List[Permission], require_all: bool = True) -> bool:
        """
        Check multiple permissions at once.
        
        Args:
            user: User to check permissions for
            permissions: List of permissions to check
            require_all: If True, user must have ALL permissions. If False, user needs ANY permission.
            
        Returns:
            True if permission check passes
        """
        if not user:
            return False
        
        # Empty permissions list should return True (no permissions required)
        if not permissions:
            return True
        
        user_permissions = self.get_user_permissions(user)
        
        if require_all:
            return all(perm in user_permissions for perm in permissions)
        else:
            return any(perm in user_permissions for perm in permissions)
    
    def get_accessible_resources(self, user: Any, resource_type: str) -> List[str]:
        """
        Get list of resources user can access.
        
        Args:
            user: User requesting access
            resource_type: Type of resource (patient, appointment, etc.)
            
        Returns:
            List of resource IDs user can access
        """
        # TODO: Implement resource-specific access logic
        # This would integrate with the database to return actual accessible resources
        self.logger.info(f"Getting accessible {resource_type} resources for user {user.email if hasattr(user, 'email') else 'unknown'}")
        return []
    
    def log_authorization_event(self, user: Any, action: str, resource: Optional[str] = None, granted: bool = True):
        """
        Log authorization events for audit trail.
        
        Args:
            user: User performing the action
            action: Action being performed
            resource: Resource being accessed
            granted: Whether access was granted
        """
        event_data = {
            'user': user.email if hasattr(user, 'email') else 'anonymous',
            'user_role': user.role if hasattr(user, 'role') else None,
            'action': action,
            'resource': resource,
            'granted': granted,
            'timestamp': logger.handlers[0].formatter.formatTime(logger.makeRecord(
                logger.name, logging.INFO, '', 0, '', (), None
            )) if logger.handlers else None
        }
        
        if granted:
            self.logger.info(f"Authorization granted: {event_data}")
        else:
            self.logger.warning(f"Authorization denied: {event_data}")


# Global permission manager instance
_permission_manager = None


def get_permission_manager() -> PermissionManager:
    """Get global permission manager instance."""
    global _permission_manager
    if _permission_manager is None:
        _permission_manager = PermissionManager()
    return _permission_manager


# Convenience functions for common permission checks
def require_admin(func: Callable) -> Callable:
    """Decorator to require admin role."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        user = getattr(self, '_current_user', None) or getattr(getattr(self, 'page', None), 'user', None)
        if not user or not hasattr(user, 'admin') or not user.admin:
            raise AuthorizationError("Admin privileges required")
        return func(self, *args, **kwargs)
    return wrapper


def require_medical_role(func: Callable) -> Callable:
    """Decorator to require medical role (doctor or therapist)."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        user = getattr(self, '_current_user', None) or getattr(getattr(self, 'page', None), 'user', None)
        if not user or not hasattr(user, 'role') or user.role.lower() not in ['doctor', 'therapist']:
            raise AuthorizationError("Medical privileges required")
        return func(self, *args, **kwargs)
    return wrapper


def require_financial_access(func: Callable) -> Callable:
    """Decorator to require financial access."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        user = getattr(self, '_current_user', None) or getattr(getattr(self, 'page', None), 'user', None)
        pm = get_permission_manager()
        if not pm.has_permission(user, Permission.FINANCIAL_VIEW):
            raise AuthorizationError("Financial access required")
        return func(self, *args, **kwargs)
    return wrapper


# Export authorization components
__all__ = [
    'Role',
    'Permission',
    'PermissionManager',
    'get_permission_manager',
    'require_admin',
    'require_medical_role',
    'require_financial_access'
]