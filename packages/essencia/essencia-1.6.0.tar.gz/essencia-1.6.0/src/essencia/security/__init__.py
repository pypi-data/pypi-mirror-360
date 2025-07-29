"""
Security module for Essência.
Provides security utilities and protection mechanisms.
"""

from .sanitizer import (
    HTMLSanitizer, 
    MarkdownSanitizer, 
    sanitize_input,
    sanitize_name,
    sanitize_email,
    sanitize_phone,
    sanitize_cpf,
    sanitize_multiline_text
)

from .session_manager import (
    SessionManager,
    get_session_manager,
    create_secure_session,
    validate_current_session,
    destroy_current_session,
    get_csrf_token,
    validate_csrf,
    require_session,
    require_csrf_token,
    regenerate_session_on_login
)

from .authorization import (
    Role,
    Permission,
    PermissionManager,
    get_permission_manager,
    require_admin,
    require_medical_role,
    require_financial_access
)

from .rate_limiter import (
    RateLimitStrategy,
    RateLimitScope,
    RateLimitConfig,
    RateLimitResult,
    RateLimiter,
    get_rate_limiter,
    rate_limit_login,
    rate_limit_api,
    rate_limit_search,
    rate_limit_export,
    rate_limit_form,
    rate_limit_password_reset
)

from .encryption_service import (
    EncryptionService,
    get_encryption_service,
    encrypt_field,
    decrypt_field,
    is_field_encrypted,
    encrypt_cpf,
    decrypt_cpf,
    encrypt_rg,
    decrypt_rg,
    encrypt_medical_data,
    decrypt_medical_data
)

from .patterns import (
    SecurityEventType,
    SecurityEvent,
    SecurityMonitor,
    PasswordPolicy,
    SecureTokenGenerator,
    SecurityHeaders,
    security_monitor_decorator,
    get_security_monitor,
    get_password_policy,
)

__all__ = [
    # XSS Prevention
    'HTMLSanitizer',
    'MarkdownSanitizer', 
    'sanitize_input',
    'sanitize_name',
    'sanitize_email',
    'sanitize_phone',
    'sanitize_cpf',
    'sanitize_multiline_text',
    
    # Session Security
    'SessionManager',
    'get_session_manager',
    'create_secure_session',
    'validate_current_session',
    'destroy_current_session',
    'get_csrf_token',
    'validate_csrf',
    'require_session',
    'require_csrf_token',
    'regenerate_session_on_login',
    
    # Authorization Framework
    'Role',
    'Permission',
    'PermissionManager',
    'get_permission_manager',
    'require_admin',
    'require_medical_role',
    'require_financial_access',
    
    # Rate Limiting System
    'RateLimitStrategy',
    'RateLimitScope', 
    'RateLimitConfig',
    'RateLimitResult',
    'RateLimiter',
    'get_rate_limiter',
    'rate_limit_login',
    'rate_limit_api',
    'rate_limit_search',
    'rate_limit_export',
    'rate_limit_form',
    'rate_limit_password_reset',
    
    # Encryption Service
    'EncryptionService',
    'get_encryption_service',
    'encrypt_field',
    'decrypt_field',
    'is_field_encrypted',
    'encrypt_cpf',
    'decrypt_cpf',
    'encrypt_rg',
    'decrypt_rg',
    'encrypt_medical_data',
    'decrypt_medical_data',
    
    # Security Patterns
    'SecurityEventType',
    'SecurityEvent',
    'SecurityMonitor',
    'PasswordPolicy',
    'SecureTokenGenerator',
    'SecurityHeaders',
    'security_monitor_decorator',
    'get_security_monitor',
    'get_password_policy',
]