"""
Advanced security patterns and utilities for essencia framework.
"""

import hashlib
import secrets
import time
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from functools import wraps
import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class SecurityEventType(Enum):
    """Types of security events."""
    LOGIN_ATTEMPT = "login_attempt"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"
    PERMISSION_DENIED = "permission_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SESSION_HIJACK_ATTEMPT = "session_hijack_attempt"
    BRUTE_FORCE_DETECTED = "brute_force_detected"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"


@dataclass
class SecurityEvent:
    """Represents a security event."""
    event_type: SecurityEventType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    risk_level: int = 0  # 0-10 scale
    blocked: bool = False


class SecurityMonitor:
    """
    Real-time security monitoring and threat detection.
    """
    
    def __init__(self):
        self.events: List[SecurityEvent] = []
        self.blocked_ips: Dict[str, datetime] = {}
        self.blocked_users: Dict[str, datetime] = {}
        self.suspicious_patterns: List[Callable] = []
        
    def log_event(self, event: SecurityEvent) -> None:
        """Log a security event."""
        self.events.append(event)
        
        # Check if action needed
        if event.risk_level >= 8:
            self._handle_high_risk_event(event)
            
        # Clean old events (keep last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.events = [e for e in self.events if e.timestamp > cutoff]
        
    def _handle_high_risk_event(self, event: SecurityEvent) -> None:
        """Handle high-risk security events."""
        logger.warning(f"High-risk security event: {event}")
        
        # Block IP if needed
        if event.ip_address and event.risk_level >= 9:
            self.block_ip(event.ip_address, duration=timedelta(hours=1))
            
        # Block user if needed
        if event.user_id and event.risk_level >= 10:
            self.block_user(event.user_id, duration=timedelta(hours=24))
            
    def block_ip(self, ip_address: str, duration: timedelta) -> None:
        """Block an IP address for specified duration."""
        self.blocked_ips[ip_address] = datetime.utcnow() + duration
        logger.info(f"Blocked IP {ip_address} until {self.blocked_ips[ip_address]}")
        
    def block_user(self, user_id: str, duration: timedelta) -> None:
        """Block a user for specified duration."""
        self.blocked_users[user_id] = datetime.utcnow() + duration
        logger.info(f"Blocked user {user_id} until {self.blocked_users[user_id]}")
        
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked."""
        if ip_address in self.blocked_ips:
            if datetime.utcnow() < self.blocked_ips[ip_address]:
                return True
            else:
                # Unblock if time expired
                del self.blocked_ips[ip_address]
        return False
        
    def is_user_blocked(self, user_id: str) -> bool:
        """Check if user is blocked."""
        if user_id in self.blocked_users:
            if datetime.utcnow() < self.blocked_users[user_id]:
                return True
            else:
                # Unblock if time expired
                del self.blocked_users[user_id]
        return False
        
    def detect_brute_force(self, user_email: str, window_minutes: int = 5, threshold: int = 5) -> bool:
        """Detect brute force login attempts."""
        cutoff = datetime.utcnow() - timedelta(minutes=window_minutes)
        
        failed_attempts = [
            e for e in self.events
            if e.event_type == SecurityEventType.LOGIN_FAILURE
            and e.timestamp > cutoff
            and e.details.get('email') == user_email
        ]
        
        if len(failed_attempts) >= threshold:
            # Log brute force detection
            self.log_event(SecurityEvent(
                event_type=SecurityEventType.BRUTE_FORCE_DETECTED,
                details={'email': user_email, 'attempts': len(failed_attempts)},
                risk_level=9
            ))
            return True
            
        return False
        
    def get_user_risk_score(self, user_id: str) -> int:
        """Calculate risk score for a user based on recent activity."""
        cutoff = datetime.utcnow() - timedelta(hours=1)
        
        user_events = [
            e for e in self.events
            if e.user_id == user_id and e.timestamp > cutoff
        ]
        
        if not user_events:
            return 0
            
        # Calculate risk based on event types and frequency
        risk_score = 0
        
        # Failed login attempts
        failed_logins = sum(1 for e in user_events if e.event_type == SecurityEventType.LOGIN_FAILURE)
        risk_score += min(failed_logins * 2, 20)
        
        # Permission denied events
        permission_denied = sum(1 for e in user_events if e.event_type == SecurityEventType.PERMISSION_DENIED)
        risk_score += min(permission_denied * 3, 30)
        
        # Suspicious activity
        suspicious = sum(1 for e in user_events if e.event_type == SecurityEventType.SUSPICIOUS_ACTIVITY)
        risk_score += min(suspicious * 5, 50)
        
        # Average risk level of events
        avg_risk = sum(e.risk_level for e in user_events) / len(user_events)
        risk_score += int(avg_risk * 10)
        
        return min(risk_score, 100)


class PasswordPolicy:
    """
    Password policy enforcement.
    """
    
    def __init__(
        self,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special: bool = True,
        max_age_days: int = 90,
        history_count: int = 5,
        min_complexity_score: int = 3
    ):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
        self.max_age_days = max_age_days
        self.history_count = history_count
        self.min_complexity_score = min_complexity_score
        
    def validate(self, password: str) -> tuple[bool, List[str]]:
        """
        Validate password against policy.
        
        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []
        
        # Length check
        if len(password) < self.min_length:
            violations.append(f"Password must be at least {self.min_length} characters")
            
        # Character requirements
        if self.require_uppercase and not any(c.isupper() for c in password):
            violations.append("Password must contain at least one uppercase letter")
            
        if self.require_lowercase and not any(c.islower() for c in password):
            violations.append("Password must contain at least one lowercase letter")
            
        if self.require_digit and not any(c.isdigit() for c in password):
            violations.append("Password must contain at least one digit")
            
        if self.require_special and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            violations.append("Password must contain at least one special character")
            
        # Complexity score
        if self.calculate_complexity(password) < self.min_complexity_score:
            violations.append("Password is not complex enough")
            
        return len(violations) == 0, violations
        
    def calculate_complexity(self, password: str) -> int:
        """Calculate password complexity score (0-5)."""
        score = 0
        
        # Length bonus
        if len(password) >= 10:
            score += 1
        if len(password) >= 14:
            score += 1
            
        # Character variety
        if any(c.isupper() for c in password):
            score += 0.5
        if any(c.islower() for c in password):
            score += 0.5
        if any(c.isdigit() for c in password):
            score += 0.5
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
            
        # Pattern detection (penalize common patterns)
        if self._has_sequential_chars(password):
            score -= 1
        if self._has_repeated_chars(password):
            score -= 0.5
            
        return max(0, min(5, int(score)))
        
    def _has_sequential_chars(self, password: str) -> bool:
        """Check for sequential characters (abc, 123)."""
        for i in range(len(password) - 2):
            if ord(password[i]) + 1 == ord(password[i + 1]) == ord(password[i + 2]) - 1:
                return True
        return False
        
    def _has_repeated_chars(self, password: str) -> bool:
        """Check for repeated characters (aaa, 111)."""
        for i in range(len(password) - 2):
            if password[i] == password[i + 1] == password[i + 2]:
                return True
        return False
        
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure password that meets policy requirements."""
        import string
        
        # Ensure minimum components
        password_chars = []
        
        if self.require_uppercase:
            password_chars.append(secrets.choice(string.ascii_uppercase))
        if self.require_lowercase:
            password_chars.append(secrets.choice(string.ascii_lowercase))
        if self.require_digit:
            password_chars.append(secrets.choice(string.digits))
        if self.require_special:
            password_chars.append(secrets.choice("!@#$%^&*()_+-=[]{}|;:,.<>?"))
            
        # Fill rest with random characters
        all_chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        remaining_length = max(length, self.min_length) - len(password_chars)
        
        for _ in range(remaining_length):
            password_chars.append(secrets.choice(all_chars))
            
        # Shuffle to avoid predictable patterns
        secrets.SystemRandom().shuffle(password_chars)
        
        return ''.join(password_chars)


class SecureTokenGenerator:
    """
    Generate and validate secure tokens for various purposes.
    """
    
    @staticmethod
    def generate_token(length: int = 32, prefix: str = "") -> str:
        """Generate a secure random token."""
        token = secrets.token_urlsafe(length)
        if prefix:
            return f"{prefix}_{token}"
        return token
        
    @staticmethod
    def generate_timed_token(data: Dict[str, Any], secret: str, ttl_seconds: int = 3600) -> str:
        """Generate a token with embedded timestamp and data."""
        import json
        import base64
        
        # Add timestamp
        token_data = {
            **data,
            'timestamp': int(time.time()),
            'ttl': ttl_seconds
        }
        
        # Serialize and encode
        json_data = json.dumps(token_data, sort_keys=True)
        encoded = base64.urlsafe_b64encode(json_data.encode()).decode()
        
        # Add signature
        signature = hashlib.sha256(f"{encoded}{secret}".encode()).hexdigest()[:16]
        
        return f"{encoded}.{signature}"
        
    @staticmethod
    def validate_timed_token(token: str, secret: str) -> Optional[Dict[str, Any]]:
        """Validate and extract data from timed token."""
        import json
        import base64
        
        try:
            # Split token
            parts = token.split('.')
            if len(parts) != 2:
                return None
                
            encoded, signature = parts
            
            # Verify signature
            expected_sig = hashlib.sha256(f"{encoded}{secret}".encode()).hexdigest()[:16]
            if signature != expected_sig:
                return None
                
            # Decode data
            json_data = base64.urlsafe_b64decode(encoded).decode()
            data = json.loads(json_data)
            
            # Check expiration
            timestamp = data.get('timestamp', 0)
            ttl = data.get('ttl', 0)
            if int(time.time()) > timestamp + ttl:
                return None
                
            return data
            
        except Exception:
            return None


class SecurityHeaders:
    """
    Security headers configuration for web applications.
    """
    
    @staticmethod
    def get_default_headers() -> Dict[str, str]:
        """Get default security headers."""
        return {
            # Prevent XSS
            'X-XSS-Protection': '1; mode=block',
            'X-Content-Type-Options': 'nosniff',
            
            # Clickjacking protection
            'X-Frame-Options': 'DENY',
            
            # HTTPS enforcement
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            
            # Content Security Policy
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';",
            
            # Referrer policy
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            
            # Permissions policy
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        }
        
    @staticmethod
    def get_medical_headers() -> Dict[str, str]:
        """Get security headers for medical applications (stricter)."""
        headers = SecurityHeaders.get_default_headers()
        
        # Stricter CSP for medical data
        headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self';"
        
        # No caching for sensitive data
        headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
        headers['Pragma'] = 'no-cache'
        headers['Expires'] = '0'
        
        return headers


def security_monitor_decorator(
    event_type: SecurityEventType,
    risk_level: int = 0,
    log_details: bool = True
):
    """
    Decorator to monitor security-sensitive operations.
    
    Args:
        event_type: Type of security event
        risk_level: Risk level (0-10)
        log_details: Whether to log operation details
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract context (assuming first arg might be self with page/user info)
            user_id = None
            ip_address = None
            
            if args and hasattr(args[0], 'current_user'):
                user_id = getattr(args[0].current_user, 'id', None)
            if args and hasattr(args[0], 'page'):
                ip_address = getattr(args[0].page, 'client_ip', None)
                
            details = {}
            if log_details:
                details['function'] = func.__name__
                details['args'] = str(args[1:])[:100]  # Limit size
                
            try:
                result = await func(*args, **kwargs)
                
                # Log successful operation
                event = SecurityEvent(
                    event_type=event_type,
                    user_id=user_id,
                    ip_address=ip_address,
                    details=details,
                    risk_level=risk_level
                )
                
                # Get monitor instance (would need to be injected)
                # monitor.log_event(event)
                
                return result
                
            except Exception as e:
                # Log failed operation with higher risk
                details['error'] = str(e)
                event = SecurityEvent(
                    event_type=event_type,
                    user_id=user_id,
                    ip_address=ip_address,
                    details=details,
                    risk_level=min(10, risk_level + 3),
                    blocked=True
                )
                
                # monitor.log_event(event)
                raise
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Similar logic for sync functions
            return func(*args, **kwargs)
            
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


# Global instances
_security_monitor = None
_password_policy = None


def get_security_monitor() -> SecurityMonitor:
    """Get global security monitor instance."""
    global _security_monitor
    if _security_monitor is None:
        _security_monitor = SecurityMonitor()
    return _security_monitor


def get_password_policy() -> PasswordPolicy:
    """Get global password policy instance."""
    global _password_policy
    if _password_policy is None:
        _password_policy = PasswordPolicy()
    return _password_policy