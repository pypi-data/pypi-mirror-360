"""
Secure Session Management.
Implements session regeneration, CSRF protection, and secure session storage.
"""

import secrets
import hashlib
import time
import logging
from typing import Dict, Any, Optional, Set
from datetime import datetime, timedelta
from functools import wraps

import flet as ft

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Secure session manager with CSRF protection and session regeneration.
    """
    
    # Session configuration
    SESSION_TIMEOUT = 3600  # 1 hour in seconds
    CSRF_TOKEN_TIMEOUT = 1800  # 30 minutes for CSRF tokens
    MAX_SESSION_SIZE = 1024 * 1024  # 1MB max session data
    
    # Security settings
    REGENERATE_ON_LOGIN = True
    REGENERATE_ON_PRIVILEGE_CHANGE = True
    SECURE_SESSION_COOKIES = True
    
    def __init__(self):
        """Initialize session manager with secure defaults."""
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._csrf_tokens: Dict[str, Dict[str, Any]] = {}
        self._session_activity: Dict[str, float] = {}
        self._suspicious_activity: Set[str] = set()
        
    def create_session(self, page: ft.Page, user_data: Dict[str, Any]) -> str:
        """
        Create a new secure session.
        
        Args:
            page: Flet page object
            user_data: User information to store in session
            
        Returns:
            Session ID
        """
        # Generate secure session ID
        session_id = self._generate_session_id()
        
        # Create session data with security metadata
        session_data = {
            'user': user_data,
            'created_at': time.time(),
            'last_activity': time.time(),
            'csrf_token': self._generate_csrf_token(session_id),
            'ip_address': getattr(page, 'client_ip', 'unknown'),
            'user_agent': getattr(page, 'user_agent', 'unknown'),
            'regenerated': False,
            'privilege_level': user_data.get('role', 'user'),
        }
        
        # Store session
        self._sessions[session_id] = session_data
        self._session_activity[session_id] = time.time()
        
        # Set session in page
        page.session.set('session_id', session_id)
        page.session.set('csrf_token', session_data['csrf_token'])
        
        logger.info(f"New session created for user {user_data.get('email', 'unknown')}")
        return session_id
    
    def regenerate_session(self, page: ft.Page, reason: str = "security") -> Optional[str]:
        """
        Regenerate session ID for security.
        
        Args:
            page: Flet page object
            reason: Reason for regeneration (for logging)
            
        Returns:
            New session ID or None if failed
        """
        old_session_id = page.session.get('session_id')
        if not old_session_id or old_session_id not in self._sessions:
            return None
        
        # Get old session data
        old_session = self._sessions[old_session_id]
        
        # Generate new session ID
        new_session_id = self._generate_session_id()
        
        # Copy session data with new metadata
        new_session = old_session.copy()
        new_session.update({
            'regenerated': True,
            'regeneration_reason': reason,
            'regenerated_at': time.time(),
            'previous_session_id': old_session_id,
            'csrf_token': self._generate_csrf_token(new_session_id),
        })
        
        # Store new session and remove old one
        self._sessions[new_session_id] = new_session
        del self._sessions[old_session_id]
        
        # Update activity tracking
        if old_session_id in self._session_activity:
            self._session_activity[new_session_id] = self._session_activity[old_session_id]
            del self._session_activity[old_session_id]
        
        # Update page session
        page.session.set('session_id', new_session_id)
        page.session.set('csrf_token', new_session['csrf_token'])
        
        logger.info(f"Session regenerated for reason: {reason}")
        return new_session_id
    
    def validate_session(self, page: ft.Page) -> Optional[Dict[str, Any]]:
        """
        Validate and refresh session.
        
        Args:
            page: Flet page object
            
        Returns:
            Session data if valid, None if invalid
        """
        session_id = page.session.get('session_id')
        if not session_id or session_id not in self._sessions:
            return None
        
        session_data = self._sessions[session_id]
        current_time = time.time()
        
        # Check session timeout
        if current_time - session_data['last_activity'] > self.SESSION_TIMEOUT:
            self.destroy_session(page, reason="timeout")
            return None
        
        # Check for suspicious activity
        if session_id in self._suspicious_activity:
            self.destroy_session(page, reason="suspicious_activity")
            return None
        
        # Update last activity
        session_data['last_activity'] = current_time
        self._session_activity[session_id] = current_time
        
        return session_data
    
    def destroy_session(self, page: ft.Page, reason: str = "logout"):
        """
        Destroy session securely.
        
        Args:
            page: Flet page object
            reason: Reason for destruction (for logging)
        """
        session_id = page.session.get('session_id')
        if session_id:
            # Remove from all tracking structures
            self._sessions.pop(session_id, None)
            self._session_activity.pop(session_id, None)
            self._suspicious_activity.discard(session_id)
            
            # Clear page session
            page.session.clear()
            
            logger.info(f"Session destroyed: {reason}")
    
    def generate_csrf_token(self, page: ft.Page) -> str:
        """
        Generate CSRF token for current session.
        
        Args:
            page: Flet page object
            
        Returns:
            CSRF token
        """
        session_id = page.session.get('session_id')
        if not session_id:
            raise ValueError("No active session")
        
        csrf_token = self._generate_csrf_token(session_id)
        
        # Store CSRF token with expiration
        self._csrf_tokens[csrf_token] = {
            'session_id': session_id,
            'created_at': time.time(),
            'used': False
        }
        
        # Update session with new CSRF token
        if session_id in self._sessions:
            self._sessions[session_id]['csrf_token'] = csrf_token
        
        page.session.set('csrf_token', csrf_token)
        return csrf_token
    
    def validate_csrf_token(self, page: ft.Page, token: str, 
                           one_time_use: bool = False) -> bool:
        """
        Validate CSRF token.
        
        Args:
            page: Flet page object
            token: CSRF token to validate
            one_time_use: Whether token should be invalidated after use
            
        Returns:
            True if valid, False if invalid
        """
        if not token or token not in self._csrf_tokens:
            return False
        
        csrf_data = self._csrf_tokens[token]
        current_time = time.time()
        
        # Check if token expired
        if current_time - csrf_data['created_at'] > self.CSRF_TOKEN_TIMEOUT:
            del self._csrf_tokens[token]
            return False
        
        # Check if token was already used (for one-time use)
        if one_time_use and csrf_data['used']:
            return False
        
        # Check if token belongs to current session
        session_id = page.session.get('session_id')
        if csrf_data['session_id'] != session_id:
            return False
        
        # Mark as used if one-time use
        if one_time_use:
            csrf_data['used'] = True
        
        return True
    
    def check_session_security(self, page: ft.Page) -> Dict[str, Any]:
        """
        Check session security status.
        
        Args:
            page: Flet page object
            
        Returns:
            Security status information
        """
        session_id = page.session.get('session_id')
        if not session_id or session_id not in self._sessions:
            return {'status': 'no_session', 'secure': False}
        
        session_data = self._sessions[session_id]
        current_time = time.time()
        
        # Calculate session age and activity
        session_age = current_time - session_data['created_at']
        time_since_activity = current_time - session_data['last_activity']
        
        # Security checks
        security_status = {
            'status': 'active',
            'secure': True,
            'session_age': session_age,
            'time_since_activity': time_since_activity,
            'regenerated': session_data.get('regenerated', False),
            'csrf_protected': bool(session_data.get('csrf_token')),
            'warnings': []
        }
        
        # Add warnings for security concerns
        if session_age > self.SESSION_TIMEOUT * 0.8:
            security_status['warnings'].append('session_expiring_soon')
        
        if time_since_activity > self.SESSION_TIMEOUT * 0.5:
            security_status['warnings'].append('inactive_session')
        
        if not session_data.get('regenerated') and session_age > 1800:  # 30 minutes
            security_status['warnings'].append('session_not_regenerated')
        
        return security_status
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions and CSRF tokens."""
        current_time = time.time()
        
        # Clean up expired sessions
        expired_sessions = []
        for session_id, session_data in self._sessions.items():
            if current_time - session_data['last_activity'] > self.SESSION_TIMEOUT:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self._sessions[session_id]
            self._session_activity.pop(session_id, None)
            self._suspicious_activity.discard(session_id)
        
        # Clean up expired CSRF tokens
        expired_tokens = []
        for token, token_data in self._csrf_tokens.items():
            if current_time - token_data['created_at'] > self.CSRF_TOKEN_TIMEOUT:
                expired_tokens.append(token)
        
        for token in expired_tokens:
            del self._csrf_tokens[token]
        
        if expired_sessions or expired_tokens:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions "
                       f"and {len(expired_tokens)} expired CSRF tokens")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get session statistics for monitoring.
        
        Returns:
            Session statistics
        """
        current_time = time.time()
        active_sessions = 0
        
        for session_data in self._sessions.values():
            if current_time - session_data['last_activity'] <= self.SESSION_TIMEOUT:
                active_sessions += 1
        
        return {
            'total_sessions': len(self._sessions),
            'active_sessions': active_sessions,
            'csrf_tokens': len(self._csrf_tokens),
            'suspicious_sessions': len(self._suspicious_activity),
        }
    
    def _generate_session_id(self) -> str:
        """Generate cryptographically secure session ID."""
        # Use 32 bytes of random data
        random_bytes = secrets.token_bytes(32)
        # Add timestamp for uniqueness
        timestamp = str(time.time()).encode()
        # Create hash
        session_hash = hashlib.sha256(random_bytes + timestamp).hexdigest()
        return session_hash
    
    def _generate_csrf_token(self, session_id: str) -> str:
        """Generate CSRF token for session."""
        # Use session ID and random data
        random_bytes = secrets.token_bytes(16)
        session_bytes = session_id.encode()
        timestamp = str(time.time()).encode()
        
        # Create CSRF token hash
        csrf_hash = hashlib.sha256(session_bytes + random_bytes + timestamp).hexdigest()[:32]
        return csrf_hash


# Global session manager instance
_session_manager = None

def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


# Decorators for session security

def require_session(func):
    """Decorator to require valid session."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Find page parameter
        page = None
        for arg in args:
            if hasattr(arg, 'page'):
                page = arg.page
                break
        if 'page' in kwargs:
            page = kwargs['page']
        
        if not page:
            raise ValueError("No page found for session validation")
        
        session_manager = get_session_manager()
        session_data = session_manager.validate_session(page)
        
        if not session_data:
            # Redirect to login or raise exception
            page.go('/login')
            return None
        
        return func(*args, **kwargs)
    return wrapper


def require_csrf_token(one_time_use: bool = False):
    """Decorator to require CSRF token validation."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Find page and CSRF token
            page = None
            csrf_token = None
            
            for arg in args:
                if hasattr(arg, 'page'):
                    page = arg.page
                    break
            if 'page' in kwargs:
                page = kwargs['page']
            if 'csrf_token' in kwargs:
                csrf_token = kwargs.pop('csrf_token')
            
            if not page:
                raise ValueError("No page found for CSRF validation")
            
            # Get CSRF token from session if not provided
            if not csrf_token:
                csrf_token = page.session.get('csrf_token')
            
            session_manager = get_session_manager()
            if not session_manager.validate_csrf_token(page, csrf_token, one_time_use):
                raise ValueError("Invalid CSRF token")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def regenerate_session_on_login(func):
    """Decorator to regenerate session after login."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        
        # Find page parameter
        page = None
        for arg in args:
            if hasattr(arg, 'page'):
                page = arg.page
                break
        if 'page' in kwargs:
            page = kwargs['page']
        
        if page and result:  # Only regenerate on successful login
            session_manager = get_session_manager()
            session_manager.regenerate_session(page, "login")
        
        return result
    return wrapper


# Utility functions

def create_secure_session(page: ft.Page, user_data: Dict[str, Any]) -> str:
    """Create a new secure session."""
    return get_session_manager().create_session(page, user_data)


def validate_current_session(page: ft.Page) -> Optional[Dict[str, Any]]:
    """Validate current session."""
    return get_session_manager().validate_session(page)


def destroy_current_session(page: ft.Page, reason: str = "logout"):
    """Destroy current session."""
    get_session_manager().destroy_session(page, reason)


def get_csrf_token(page: ft.Page) -> str:
    """Get CSRF token for current session."""
    return get_session_manager().generate_csrf_token(page)


def validate_csrf(page: ft.Page, token: str, one_time_use: bool = False) -> bool:
    """Validate CSRF token."""
    return get_session_manager().validate_csrf_token(page, token, one_time_use)