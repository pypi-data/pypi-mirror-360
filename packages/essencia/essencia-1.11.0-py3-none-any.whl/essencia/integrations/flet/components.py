"""
Secure Flet components with built-in security features.

Provides drop-in replacements for common Flet components that include
security features like rate limiting, authorization, and audit logging.
"""

import logging
from typing import Optional, Callable, Any, List, Union
from datetime import datetime

try:
    import flet as ft
except ImportError:
    raise ImportError("Flet is required for this module. Install with: pip install flet")

from .middleware import (
    FletRateLimiter,
    FletAuditLogger,
    FletAuthorizationMiddleware
)
from .decorators import (
    flet_rate_limit,
    flet_audit,
    flet_authorized
)

logger = logging.getLogger(__name__)


class SecureButton(ft.ElevatedButton):
    """
    Secure button with built-in rate limiting and audit logging.
    """
    
    def __init__(
        self,
        text: str = None,
        on_click: Callable = None,
        rate_limit: Optional[dict] = None,
        audit_action: Optional[str] = None,
        required_permission: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize secure button.
        
        Args:
            text: Button text
            on_click: Click handler
            rate_limit: Rate limit config (action, limit, window)
            audit_action: Action name for audit logging
            required_permission: Required permission to click
            **kwargs: Other button properties
        """
        self._original_on_click = on_click
        self._rate_limit = rate_limit or {'action': 'button_click', 'limit': 10, 'window': 60}
        self._audit_action = audit_action
        self._required_permission = required_permission
        
        # Wrap the click handler with security features
        if on_click:
            on_click = self._create_secure_handler(on_click)
        
        super().__init__(text=text, on_click=on_click, **kwargs)
    
    def _create_secure_handler(self, handler):
        """Create a secure wrapper for the click handler."""
        # Apply decorators in order
        secure_handler = handler
        
        # Add audit logging
        if self._audit_action:
            secure_handler = flet_audit(self._audit_action)(secure_handler)
        
        # Add authorization
        if self._required_permission:
            secure_handler = flet_authorized(self._required_permission)(secure_handler)
        
        # Add rate limiting
        secure_handler = flet_rate_limit(**self._rate_limit)(secure_handler)
        
        return secure_handler


class SecureTextField(ft.TextField):
    """
    Secure text field with input sanitization and validation.
    """
    
    def __init__(
        self,
        label: str = None,
        value: str = None,
        on_change: Callable = None,
        sanitize: bool = True,
        max_length: Optional[int] = None,
        pattern: Optional[str] = None,
        audit_changes: bool = False,
        **kwargs
    ):
        """
        Initialize secure text field.
        
        Args:
            label: Field label
            value: Initial value
            on_change: Change handler
            sanitize: Whether to sanitize input
            max_length: Maximum input length
            pattern: Validation pattern (regex)
            audit_changes: Whether to audit value changes
            **kwargs: Other text field properties
        """
        self._sanitize = sanitize
        self._pattern = pattern
        self._audit_changes = audit_changes
        self._original_on_change = on_change
        
        # Set max length
        if max_length:
            kwargs['max_length'] = max_length
        
        # Wrap the change handler
        if on_change or sanitize or pattern:
            on_change = self._create_secure_handler(on_change)
        
        super().__init__(label=label, value=value, on_change=on_change, **kwargs)
    
    def _create_secure_handler(self, handler):
        """Create a secure wrapper for the change handler."""
        def secure_handler(e):
            # Sanitize input
            if self._sanitize:
                # Remove potentially dangerous characters
                e.control.value = self._sanitize_input(e.control.value)
            
            # Validate pattern
            if self._pattern and e.control.value:
                import re
                if not re.match(self._pattern, e.control.value):
                    e.control.error_text = "Formato inválido"
                    e.control.update()
                    return
                else:
                    e.control.error_text = None
            
            # Audit if enabled
            if self._audit_changes:
                self._audit_change(e)
            
            # Call original handler
            if self._original_on_change:
                self._original_on_change(e)
        
        return secure_handler
    
    def _sanitize_input(self, value: str) -> str:
        """Basic input sanitization."""
        if not value:
            return value
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Remove control characters (except newline and tab)
        import re
        value = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', value)
        
        return value.strip()
    
    def _audit_change(self, e):
        """Audit field value change."""
        try:
            if hasattr(e.page, '_security') and 'audit_logger' in e.page._security:
                audit_logger = e.page._security['audit_logger']
                audit_logger.log_action(
                    e.page,
                    'FIELD_CHANGE',
                    self.label or 'text_field',
                    'SUCCESS',
                    {'field': self.label, 'has_value': bool(e.control.value)}
                )
        except Exception as ex:
            logger.error(f"Failed to audit field change: {ex}")


class SecureContainer(ft.Container):
    """
    Secure container that enforces authorization.
    """
    
    def __init__(
        self,
        content: Any = None,
        required_permission: Optional[str] = None,
        required_role: Optional[str] = None,
        fallback_content: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize secure container.
        
        Args:
            content: Container content
            required_permission: Required permission to view
            required_role: Required role to view
            fallback_content: Content to show if unauthorized
            **kwargs: Other container properties
        """
        self._original_content = content
        self._required_permission = required_permission
        self._required_role = required_role
        self._fallback_content = fallback_content or ft.Text(
            "Você não tem permissão para visualizar este conteúdo.",
            color=ft.colors.ERROR
        )
        
        # Start with fallback content (will be updated in did_mount)
        super().__init__(content=self._fallback_content, **kwargs)
    
    def did_mount(self):
        """Check authorization when mounted."""
        super().did_mount()
        self._check_authorization()
    
    def _check_authorization(self):
        """Check if user is authorized to view content."""
        try:
            if not self.page:
                return
            
            authorized = True
            
            # Check permission
            if self._required_permission:
                if hasattr(self.page, '_security') and 'auth_middleware' in self.page._security:
                    auth_middleware = self.page._security['auth_middleware']
                    authorized = auth_middleware.check_permission(self.page, self._required_permission)
                else:
                    authorized = False
            
            # Check role
            if authorized and self._required_role:
                if hasattr(self.page, 'session'):
                    user_role = self.page.session.get('user_role')
                    authorized = user_role == self._required_role
                else:
                    authorized = False
            
            # Update content based on authorization
            if authorized:
                self.content = self._original_content
            else:
                self.content = self._fallback_content
            
            self.update()
            
        except Exception as e:
            logger.error(f"Authorization check failed: {e}")


class RateLimitedButton(SecureButton):
    """
    Convenience button with pre-configured rate limiting.
    """
    
    def __init__(
        self,
        text: str = None,
        on_click: Callable = None,
        action: str = 'button_click',
        limit: int = 5,
        window: int = 60,
        **kwargs
    ):
        """
        Initialize rate-limited button.
        
        Args:
            text: Button text
            on_click: Click handler
            action: Rate limit action name
            limit: Max clicks allowed
            window: Time window in seconds
            **kwargs: Other button properties
        """
        rate_limit = {'action': action, 'limit': limit, 'window': window}
        super().__init__(text=text, on_click=on_click, rate_limit=rate_limit, **kwargs)


class AuthorizedView(ft.View):
    """
    View that enforces authorization before rendering.
    """
    
    def __init__(
        self,
        route: str = None,
        controls: List[ft.Control] = None,
        required_permission: Optional[str] = None,
        required_role: Optional[str] = None,
        require_auth: bool = True,
        unauthorized_route: str = '/unauthorized',
        **kwargs
    ):
        """
        Initialize authorized view.
        
        Args:
            route: View route
            controls: View controls
            required_permission: Required permission
            required_role: Required role
            require_auth: Whether authentication is required
            unauthorized_route: Route to redirect if unauthorized
            **kwargs: Other view properties
        """
        self._required_permission = required_permission
        self._required_role = required_role
        self._require_auth = require_auth
        self._unauthorized_route = unauthorized_route
        self._original_controls = controls or []
        
        # Start with loading indicator
        loading_controls = [
            ft.Container(
                content=ft.ProgressRing(),
                alignment=ft.alignment.center,
                expand=True
            )
        ]
        
        super().__init__(route=route, controls=loading_controls, **kwargs)
    
    def did_mount(self):
        """Check authorization when mounted."""
        super().did_mount()
        self._check_authorization()
    
    def _check_authorization(self):
        """Check if user is authorized to view."""
        try:
            if not self.page:
                return
            
            # Check authentication
            if self._require_auth:
                if not hasattr(self.page, 'session') or not self.page.session.get('authenticated'):
                    self.page.go('/login')
                    return
            
            authorized = True
            
            # Check permission
            if self._required_permission:
                if hasattr(self.page, '_security') and 'auth_middleware' in self.page._security:
                    auth_middleware = self.page._security['auth_middleware']
                    authorized = auth_middleware.check_permission(self.page, self._required_permission)
                else:
                    authorized = False
            
            # Check role
            if authorized and self._required_role:
                if hasattr(self.page, 'session'):
                    user_role = self.page.session.get('user_role')
                    authorized = user_role == self._required_role
                else:
                    authorized = False
            
            # Update view based on authorization
            if authorized:
                self.controls = self._original_controls
            else:
                self.page.go(self._unauthorized_route)
            
            self.update()
            
        except Exception as e:
            logger.error(f"Authorization check failed: {e}")


class AuditedForm(ft.Column):
    """
    Form container that automatically audits submissions.
    """
    
    def __init__(
        self,
        form_name: str,
        controls: List[ft.Control] = None,
        on_submit: Optional[Callable] = None,
        rate_limit_submit: bool = True,
        **kwargs
    ):
        """
        Initialize audited form.
        
        Args:
            form_name: Form identifier for audit logs
            controls: Form controls
            on_submit: Submit handler
            rate_limit_submit: Whether to rate limit submissions
            **kwargs: Other column properties
        """
        self.form_name = form_name
        self._on_submit = on_submit
        self._form_data = {}
        
        # Create submit button
        submit_button_config = {
            'text': 'Enviar',
            'on_click': self._handle_submit,
            'audit_action': f'FORM_SUBMIT_{form_name}'
        }
        
        if rate_limit_submit:
            submit_button_config['rate_limit'] = {
                'action': f'form_submit_{form_name}',
                'limit': 5,
                'window': 60
            }
        
        submit_button = SecureButton(**submit_button_config)
        
        # Add submit button to controls
        all_controls = (controls or []) + [submit_button]
        
        super().__init__(controls=all_controls, **kwargs)
    
    def _handle_submit(self, e):
        """Handle form submission with audit logging."""
        try:
            # Collect form data
            self._collect_form_data()
            
            # Log form submission attempt
            if hasattr(e.page, '_security') and 'audit_logger' in e.page._security:
                audit_logger = e.page._security['audit_logger']
                audit_logger.log_action(
                    e.page,
                    'FORM_SUBMIT',
                    self.form_name,
                    'ATTEMPT',
                    {'fields': list(self._form_data.keys())}
                )
            
            # Call original submit handler
            if self._on_submit:
                self._on_submit(e, self._form_data)
            
        except Exception as ex:
            logger.error(f"Form submission failed: {ex}")
            
            # Log failure
            if hasattr(e.page, '_security') and 'audit_logger' in e.page._security:
                audit_logger = e.page._security['audit_logger']
                audit_logger.log_action(
                    e.page,
                    'FORM_SUBMIT',
                    self.form_name,
                    'FAILURE',
                    {'error': str(ex)}
                )
    
    def _collect_form_data(self):
        """Collect data from form fields."""
        self._form_data = {}
        
        def collect_from_control(control):
            if isinstance(control, ft.TextField) and control.label:
                self._form_data[control.label] = control.value
            elif isinstance(control, ft.Dropdown) and control.label:
                self._form_data[control.label] = control.value
            elif isinstance(control, ft.Checkbox) and control.label:
                self._form_data[control.label] = control.value
            elif hasattr(control, 'controls'):
                for child in control.controls:
                    collect_from_control(child)
        
        for control in self.controls:
            collect_from_control(control)