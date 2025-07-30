"""
Secure form components with input sanitization and validation.

Provides form controls that automatically sanitize user input
to prevent XSS and other security vulnerabilities.
"""

import re
import html
import logging
from typing import Optional, Callable, Any, List, Dict
from functools import wraps

import flet as ft

from ..themes import ThemedComponent
from .validators import Validator, ValidationResult, EmailValidator, RequiredValidator

logger = logging.getLogger(__name__)


class InputSanitizer:
    """Utility class for sanitizing various types of input."""
    
    @staticmethod
    def sanitize_text(value: str, max_length: Optional[int] = None) -> str:
        """Sanitize general text input."""
        if not value:
            return ""
            
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Strip leading/trailing whitespace
        value = value.strip()
        
        # HTML escape
        value = html.escape(value, quote=True)
        
        # Limit length
        if max_length and len(value) > max_length:
            value = value[:max_length]
            
        return value
    
    @staticmethod
    def sanitize_email(value: str) -> str:
        """Sanitize email input."""
        if not value:
            return ""
            
        # Basic email sanitization
        value = value.strip().lower()
        
        # Remove dangerous characters
        value = re.sub(r'[<>"\']', '', value)
        
        # Validate basic format
        if '@' not in value:
            return ""
            
        # Limit length (RFC 5321)
        if len(value) > 254:
            return ""
            
        return value
    
    @staticmethod
    def sanitize_phone(value: str) -> str:
        """Sanitize phone number input."""
        if not value:
            return ""
            
        # Keep only digits, spaces, and common phone characters
        value = re.sub(r'[^0-9\s\-\+\(\).]', '', value)
        
        # Limit length
        if len(value) > 20:
            value = value[:20]
            
        return value.strip()
    
    @staticmethod
    def sanitize_name(value: str) -> str:
        """Sanitize name input."""
        if not value:
            return ""
            
        # Remove digits and special characters except spaces, hyphens, apostrophes
        value = re.sub(r'[^a-zA-ZÀ-ÿ\s\-\']', '', value)
        
        # Normalize spaces
        value = ' '.join(value.split())
        
        # Limit length
        if len(value) > 100:
            value = value[:100]
            
        return value.strip()
    
    @staticmethod
    def sanitize_multiline(value: str, max_length: int = 5000) -> str:
        """Sanitize multiline text input."""
        if not value:
            return ""
            
        # Preserve newlines but escape HTML
        lines = value.split('\n')
        sanitized_lines = []
        
        for line in lines:
            # Strip each line
            line = line.strip()
            # HTML escape
            line = html.escape(line, quote=True)
            sanitized_lines.append(line)
            
        result = '\n'.join(sanitized_lines)
        
        # Limit total length
        if len(result) > max_length:
            result = result[:max_length]
            
        return result
    
    @staticmethod
    def sanitize_alphanumeric(value: str, allow_spaces: bool = False) -> str:
        """Sanitize to only alphanumeric characters."""
        if not value:
            return ""
            
        if allow_spaces:
            value = re.sub(r'[^a-zA-Z0-9\s]', '', value)
            value = ' '.join(value.split())  # Normalize spaces
        else:
            value = re.sub(r'[^a-zA-Z0-9]', '', value)
            
        return value.strip()


class SecureTextField(ft.TextField, ThemedComponent):
    """
    Secure text field that automatically sanitizes input.
    
    Example:
        ```python
        field = SecureTextField(
            label="Name",
            sanitizer=InputSanitizer.sanitize_name,
            validators=[RequiredValidator()],
            max_length=50
        )
        ```
    """
    
    def __init__(
        self,
        label: str = "",
        value: str = "",
        sanitizer: Optional[Callable[[str], str]] = None,
        validators: Optional[List[Validator]] = None,
        max_length: Optional[int] = None,
        on_change: Optional[Callable] = None,
        on_blur: Optional[Callable] = None,
        **kwargs
    ):
        ThemedComponent.__init__(self)
        
        self._sanitizer = sanitizer or (lambda x: InputSanitizer.sanitize_text(x, max_length))
        self._validators = validators or []
        self._user_on_change = on_change
        self._user_on_blur = on_blur
        self._max_length = max_length
        self._is_valid = True
        
        # Sanitize initial value
        sanitized_value = self._sanitizer(value) if value else ""
        
        super().__init__(
            label=label,
            value=sanitized_value,
            on_change=self._handle_change,
            on_blur=self._handle_blur,
            **kwargs
        )
    
    def did_mount(self):
        """Apply theme after mounting."""
        super().did_mount()
        
        # Apply theme colors
        if not self.border_color:
            self.border_color = self.outline_color
        if not self.focused_border_color:
            self.focused_border_color = self.primary_color
            
        self.update()
    
    def _handle_change(self, e):
        """Handle text change with sanitization."""
        if e.control.value is not None:
            # Sanitize the input
            original_value = e.control.value
            sanitized_value = self._sanitizer(original_value)
            
            # Update value if sanitization changed it
            if sanitized_value != original_value:
                e.control.value = sanitized_value
                e.control.update()
                logger.debug(f"Input sanitized in field '{self.label}'")
        
        # Clear error on change
        self._clear_error()
        
        # Call user's change handler
        if self._user_on_change:
            self._user_on_change(e)
    
    def _handle_blur(self, e):
        """Handle field blur with validation."""
        # Validate on blur
        self.validate()
        
        # Call user's blur handler
        if self._user_on_blur:
            self._user_on_blur(e)
    
    def validate(self) -> bool:
        """Validate the field value."""
        value = self.value
        
        for validator in self._validators:
            result = validator.validate(value)
            if not result.is_valid:
                self._show_error(result.error_message or "Invalid value")
                return False
                
        self._clear_error()
        return True
    
    def _show_error(self, message: str):
        """Show validation error."""
        self._is_valid = False
        self.error_text = message
        self.border_color = self.error_color
        self.update()
    
    def _clear_error(self):
        """Clear validation error."""
        self._is_valid = True
        self.error_text = None
        self.border_color = self.outline_color
        self.update()
    
    @property
    def is_valid(self) -> bool:
        """Check if field is valid."""
        return self._is_valid
    
    @property
    def sanitized_value(self) -> str:
        """Get the sanitized value."""
        return self._sanitizer(self.value) if self.value else ""


class SecureEmailField(SecureTextField):
    """Secure text field specifically for email addresses."""
    
    def __init__(self, label: str = "Email", required: bool = False, **kwargs):
        validators = [EmailValidator()]
        if required:
            validators.insert(0, RequiredValidator("Email is required"))
            
        super().__init__(
            label=label,
            sanitizer=InputSanitizer.sanitize_email,
            validators=validators,
            max_length=254,
            keyboard_type=ft.KeyboardType.EMAIL,
            **kwargs
        )


class SecurePasswordField(SecureTextField):
    """Secure text field for passwords."""
    
    def __init__(
        self,
        label: str = "Password",
        required: bool = False,
        min_length: int = 8,
        **kwargs
    ):
        validators = []
        if required:
            validators.append(RequiredValidator("Password is required"))
            
        super().__init__(
            label=label,
            password=True,
            can_reveal_password=True,
            validators=validators,
            **kwargs
        )


class SecureTextArea(ft.TextField, ThemedComponent):
    """Secure multiline text field with sanitization."""
    
    def __init__(
        self,
        label: str = "",
        value: str = "",
        max_length: int = 5000,
        min_lines: int = 3,
        max_lines: int = 10,
        validators: Optional[List[Validator]] = None,
        on_change: Optional[Callable] = None,
        **kwargs
    ):
        ThemedComponent.__init__(self)
        
        self._max_length = max_length
        self._validators = validators or []
        self._user_on_change = on_change
        
        # Sanitize initial value
        sanitized_value = InputSanitizer.sanitize_multiline(value, max_length) if value else ""
        
        super().__init__(
            label=label,
            value=sanitized_value,
            multiline=True,
            min_lines=min_lines,
            max_lines=max_lines,
            on_change=self._handle_change,
            **kwargs
        )
    
    def _handle_change(self, e):
        """Handle text change with sanitization."""
        if e.control.value:
            # Sanitize the input
            original_value = e.control.value
            sanitized_value = InputSanitizer.sanitize_multiline(original_value, self._max_length)
            
            # Update value if sanitization changed it
            if sanitized_value != original_value:
                e.control.value = sanitized_value
                e.control.update()
        
        # Call user's change handler
        if self._user_on_change:
            self._user_on_change(e)


class SecureDropdown(ft.Dropdown, ThemedComponent):
    """Secure dropdown that sanitizes option labels."""
    
    def __init__(
        self,
        label: str = "",
        options: Optional[List[Any]] = None,
        value: Any = None,
        required: bool = False,
        **kwargs
    ):
        ThemedComponent.__init__(self)
        
        # Sanitize label
        sanitized_label = InputSanitizer.sanitize_text(label) if label else ""
        
        # Sanitize options
        sanitized_options = []
        if options:
            for option in options:
                if isinstance(option, str):
                    sanitized_options.append(
                        ft.dropdown.Option(
                            key=option,
                            text=InputSanitizer.sanitize_text(option)
                        )
                    )
                elif isinstance(option, ft.dropdown.Option):
                    # Sanitize the display text
                    option.text = InputSanitizer.sanitize_text(option.text)
                    sanitized_options.append(option)
                elif isinstance(option, dict):
                    # Handle dict format
                    sanitized_options.append(
                        ft.dropdown.Option(
                            key=str(option.get('key', '')),
                            text=InputSanitizer.sanitize_text(str(option.get('text', '')))
                        )
                    )
        
        super().__init__(
            label=sanitized_label,
            options=sanitized_options,
            value=value,
            **kwargs
        )
        
        self._required = required
        
    def validate(self) -> bool:
        """Validate dropdown selection."""
        if self._required and not self.value:
            self.error_text = "Please select an option"
            self.update()
            return False
            
        self.error_text = None
        self.update()
        return True


class SecureForm(ft.Container, ThemedComponent):
    """
    Base secure form container with validation support.
    
    Example:
        ```python
        form = SecureForm(
            title="User Registration",
            on_submit=handle_registration
        )
        
        form.add_field(SecureEmailField(label="Email", required=True))
        form.add_field(SecurePasswordField(label="Password", required=True))
        form.add_submit_button("Register")
        ```
    """
    
    def __init__(
        self,
        title: str = "",
        on_submit: Optional[Callable] = None,
        **kwargs
    ):
        ThemedComponent.__init__(self)
        
        self.title = title
        self.on_submit = on_submit
        self.fields: List[ft.Control] = []
        self.submit_button: Optional[ft.ElevatedButton] = None
        
        # Form content
        self.form_content = ft.Column(
            controls=[],
            spacing=20,
            tight=True
        )
        
        super().__init__(
            content=self.form_content,
            padding=ft.padding.all(20),
            border_radius=10,
            **kwargs
        )
        
        self._setup_form()
    
    def did_mount(self):
        """Apply theme after mounting."""
        super().did_mount()
        
        # Apply theme
        if not self.bgcolor:
            self.bgcolor = self.surface_color
        if not self.border:
            self.border = ft.border.all(1, self.outline_color)
            
        self.update()
    
    def _setup_form(self):
        """Set up the basic form structure."""
        if self.title:
            title_text = ft.Text(
                self.title,
                size=24,
                weight=ft.FontWeight.BOLD
            )
            self.form_content.controls.append(title_text)
            self.form_content.controls.append(ft.Divider())
    
    def add_field(self, field: ft.Control):
        """Add a field to the form."""
        self.fields.append(field)
        self.form_content.controls.append(field)
    
    def add_submit_button(self, text: str = "Submit", icon: Optional[str] = None):
        """Add submit button to the form."""
        self.submit_button = ft.ElevatedButton(
            text=text,
            icon=icon,
            on_click=self._handle_submit
        )
        
        self.form_content.controls.append(self.submit_button)
    
    def _handle_submit(self, e):
        """Handle form submission with validation."""
        # Validate all fields
        all_valid = True
        
        for field in self.fields:
            if hasattr(field, 'validate'):
                if not field.validate():
                    all_valid = False
                    
        if not all_valid:
            self._show_error("Please correct the errors above")
            return
            
        # Get form data
        form_data = self.get_form_data()
        
        # Call submit handler
        if self.on_submit:
            self.on_submit(form_data)
        else:
            self._show_info("Form submitted successfully")
    
    def get_form_data(self) -> Dict[str, Any]:
        """Get sanitized form data."""
        form_data = {}
        
        for field in self.fields:
            if hasattr(field, 'value'):
                # Get field key/name
                key = getattr(field, 'key', None) or getattr(field, 'label', f'field_{id(field)}')
                
                # Get sanitized value
                if hasattr(field, 'sanitized_value'):
                    value = field.sanitized_value
                else:
                    value = field.value
                    
                form_data[key] = value
                
        return form_data
    
    def _show_error(self, message: str):
        """Show error message."""
        if self.page:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(message),
                    bgcolor=ft.Colors.ERROR_CONTAINER
                )
            )
    
    def _show_info(self, message: str):
        """Show info message."""
        if self.page:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(message),
                    bgcolor=ft.Colors.PRIMARY_CONTAINER
                )
            )
    
    def reset(self):
        """Reset all form fields."""
        for field in self.fields:
            if hasattr(field, 'value'):
                field.value = ""
                if hasattr(field, '_clear_error'):
                    field._clear_error()
                field.update()


def create_secure_field(field_type: str, **kwargs) -> ft.Control:
    """
    Factory function to create secure input fields.
    
    Args:
        field_type: Type of field ('text', 'email', 'password', 'textarea', 'dropdown')
        **kwargs: Field-specific parameters
        
    Returns:
        Secure input control
        
    Example:
        ```python
        email_field = create_secure_field(
            'email',
            label='Email Address',
            required=True
        )
        ```
    """
    field_map = {
        'text': SecureTextField,
        'email': SecureEmailField,
        'password': SecurePasswordField,
        'textarea': SecureTextArea,
        'dropdown': SecureDropdown
    }
    
    field_class = field_map.get(field_type, SecureTextField)
    return field_class(**kwargs)