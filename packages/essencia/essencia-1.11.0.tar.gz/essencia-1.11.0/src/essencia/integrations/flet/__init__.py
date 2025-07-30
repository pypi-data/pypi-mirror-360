"""
Flet integration for Essencia framework.

Provides Flet-specific adapters and utilities for:
- Security middleware (rate limiting, authorization)
- Audit logging with Flet page context
- Session management for Flet apps
- UI component security mixins
"""

from .middleware import (
    FletRateLimiter,
    FletAuditLogger,
    FletSessionManager,
    FletAuthorizationMiddleware,
    apply_security_to_page,
    setup_page_security
)

from .decorators import (
    flet_rate_limit,
    flet_audit,
    flet_authorized,
    flet_session_required,
    with_page_context
)

from .components import (
    SecureButton,
    SecureTextField,
    SecureContainer,
    RateLimitedButton,
    AuthorizedView,
    AuditedForm
)

__all__ = [
    # Middleware
    'FletRateLimiter',
    'FletAuditLogger',
    'FletSessionManager',
    'FletAuthorizationMiddleware',
    'apply_security_to_page',
    'setup_page_security',
    
    # Decorators
    'flet_rate_limit',
    'flet_audit',
    'flet_authorized',
    'flet_session_required',
    'with_page_context',
    
    # Components
    'SecureButton',
    'SecureTextField',
    'SecureContainer',
    'RateLimitedButton',
    'AuthorizedView',
    'AuditedForm'
]