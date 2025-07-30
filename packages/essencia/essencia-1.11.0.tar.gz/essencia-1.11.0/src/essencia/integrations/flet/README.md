# Flet Integration for Essencia Framework

This module provides seamless integration between Essencia's security features and Flet applications.

## Features

- **Rate Limiting**: Protect against abuse with configurable rate limits
- **Audit Logging**: Automatic audit trails with Flet page context
- **Session Management**: Secure session handling integrated with Flet
- **Authorization**: Role and permission-based access control
- **Secure Components**: Drop-in replacements for Flet components with built-in security

## Installation

```bash
pip install essencia[flet]
```

## Quick Start

```python
import flet as ft
from essencia.integrations.flet import (
    apply_security_to_page,
    SecureButton,
    flet_rate_limit,
    flet_audit
)

def main(page: ft.Page):
    # Apply security to your page
    apply_security_to_page(page)
    
    # Use secure components
    @flet_audit("USER_ACTION")
    @flet_rate_limit(limit=5, window=60)
    def handle_click(e):
        print("Button clicked!")
    
    secure_btn = SecureButton(
        text="Click Me",
        on_click=handle_click
    )
    
    page.add(secure_btn)

ft.app(target=main)
```

## Components

### Middleware

- `FletRateLimiter`: Rate limiting with Flet page context
- `FletAuditLogger`: Audit logging with automatic context extraction
- `FletSessionManager`: Session management integrated with Flet
- `FletAuthorizationMiddleware`: Permission and role checking

### Decorators

- `@flet_rate_limit`: Add rate limiting to event handlers
- `@flet_audit`: Add audit logging to functions
- `@flet_authorized`: Require permissions or roles
- `@flet_session_required`: Require valid session

### Secure Components

- `SecureButton`: Button with rate limiting and audit logging
- `SecureTextField`: Text field with input sanitization
- `SecureContainer`: Container with authorization checks
- `AuthorizedView`: View that enforces permissions
- `AuditedForm`: Form that automatically logs submissions

## Examples

### Secure Login Form

```python
from essencia.integrations.flet import (
    SecureTextField,
    SecureButton,
    audit_login,
    rate_limit_login
)

username = SecureTextField(
    label="Username",
    max_length=50,
    sanitize=True
)

password = SecureTextField(
    label="Password",
    password=True,
    sanitize=True
)

@audit_login
@rate_limit_login
def handle_login(e):
    # Your login logic here
    pass

login_btn = SecureButton(
    text="Login",
    on_click=handle_login
)
```

### Protected Dashboard

```python
from essencia.integrations.flet import (
    setup_page_security,
    SecureContainer
)

@setup_page_security(
    require_auth=True,
    required_permissions=['view_dashboard']
)
def dashboard_view(page: ft.Page):
    # Only authenticated users with permission can access
    
    admin_section = SecureContainer(
        content=admin_controls,
        required_role="admin"
    )
    
    return ft.Column([
        ft.Text("Dashboard"),
        admin_section
    ])
```

### Rate-Limited API Calls

```python
from essencia.integrations.flet import flet_rate_limit

@flet_rate_limit(action='api_call', limit=100, window=60)
def fetch_data(e):
    # This can only be called 100 times per minute
    response = api.get_data()
    update_ui(response)
```

## Configuration

Configure Essencia's security features in your app initialization:

```python
from essencia.config import SecurityConfig
from essencia.integrations.flet import apply_security_to_page

config = SecurityConfig(
    session_timeout=3600,
    max_login_attempts=5,
    enable_audit_logging=True
)

def main(page: ft.Page):
    apply_security_to_page(page, config)
    # Your app code
```

## Best Practices

1. **Always apply security to pages**: Use `apply_security_to_page()` at the start of your main function
2. **Use secure components**: Replace standard Flet components with secure versions where appropriate
3. **Add audit logging**: Use `@flet_audit` for sensitive operations
4. **Implement rate limiting**: Protect forms and APIs with `@flet_rate_limit`
5. **Validate sessions**: Use `@flet_session_required` for protected routes

## Integration with Existing Apps

The Flet integration is designed to be non-intrusive. You can gradually adopt security features:

1. Start by applying security to pages
2. Replace critical buttons with `SecureButton`
3. Add decorators to sensitive functions
4. Implement authorization for admin features

## Debugging

Enable debug logging to see security events:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Support

For issues or questions, please refer to the Essencia documentation or create an issue on GitHub.