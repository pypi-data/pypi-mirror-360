"""
Form builder for creating dynamic forms from configuration.

Provides a declarative way to build forms with validation,
layout control, and consistent styling.
"""

import logging
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

import flet as ft

from ..themes import ThemedComponent
from .secure import (
    SecureTextField,
    SecureEmailField,
    SecurePasswordField,
    SecureTextArea,
    SecureDropdown,
    InputSanitizer
)
from .validators import (
    Validator,
    RequiredValidator,
    EmailValidator,
    LengthValidator,
    PatternValidator,
    NumericValidator,
    DateValidator,
    CommonValidators
)

logger = logging.getLogger(__name__)


class FieldType(Enum):
    """Supported field types."""
    TEXT = "text"
    EMAIL = "email"
    PASSWORD = "password"
    NUMBER = "number"
    PHONE = "phone"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    TEXTAREA = "textarea"
    DROPDOWN = "dropdown"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    SWITCH = "switch"
    SLIDER = "slider"
    FILE = "file"


class ValidationRule(Enum):
    """Common validation rules."""
    REQUIRED = "required"
    EMAIL = "email"
    MIN_LENGTH = "min_length"
    MAX_LENGTH = "max_length"
    PATTERN = "pattern"
    MIN_VALUE = "min_value"
    MAX_VALUE = "max_value"
    CUSTOM = "custom"


@dataclass
class FieldValidation:
    """Field validation configuration."""
    rule: ValidationRule
    value: Any = None
    message: Optional[str] = None


@dataclass
class FormField:
    """Form field configuration."""
    name: str
    type: FieldType
    label: str
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    default_value: Any = None
    required: bool = False
    disabled: bool = False
    read_only: bool = False
    hidden: bool = False
    validations: List[FieldValidation] = field(default_factory=list)
    options: Optional[List[Union[str, Dict[str, Any]]]] = None  # For dropdowns/radio
    min_value: Optional[Union[int, float]] = None  # For number/slider
    max_value: Optional[Union[int, float]] = None  # For number/slider
    step: Optional[Union[int, float]] = None  # For number/slider
    rows: int = 3  # For textarea
    icon: Optional[str] = None
    suffix_text: Optional[str] = None
    prefix_text: Optional[str] = None
    col: Optional[Union[int, Dict[str, int]]] = None  # Grid column span
    on_change: Optional[Callable] = None


@dataclass
class FormConfig:
    """Form configuration."""
    title: Optional[str] = None
    description: Optional[str] = None
    submit_text: str = "Submit"
    cancel_text: str = "Cancel"
    show_cancel: bool = True
    columns: int = 1  # Number of columns in form grid
    spacing: int = 20
    validate_on_submit: bool = True
    validate_on_blur: bool = True
    show_required_indicator: bool = True
    success_message: str = "Form submitted successfully"
    error_message: str = "Please correct the errors below"


class FormBuilder(ft.Container, ThemedComponent):
    """
    Dynamic form builder that creates forms from configuration.
    
    Example:
        ```python
        # Define form fields
        fields = [
            FormField(
                name="email",
                type=FieldType.EMAIL,
                label="Email Address",
                required=True,
                validations=[
                    FieldValidation(ValidationRule.EMAIL)
                ]
            ),
            FormField(
                name="password",
                type=FieldType.PASSWORD,
                label="Password",
                required=True,
                validations=[
                    FieldValidation(ValidationRule.MIN_LENGTH, value=8)
                ]
            ),
            FormField(
                name="age",
                type=FieldType.NUMBER,
                label="Age",
                min_value=0,
                max_value=150
            )
        ]
        
        # Create form
        form = FormBuilder(
            fields=fields,
            config=FormConfig(title="User Registration"),
            on_submit=handle_registration
        )
        ```
    """
    
    def __init__(
        self,
        fields: List[FormField],
        config: Optional[FormConfig] = None,
        on_submit: Optional[Callable[[Dict[str, Any]], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        ThemedComponent.__init__(self)
        
        self.fields = fields
        self.config = config or FormConfig()
        self.on_submit = on_submit
        self.on_cancel = on_cancel
        
        # Field controls mapped by name
        self.field_controls: Dict[str, ft.Control] = {}
        
        # Build form
        self.form_content = self._build_form()
        
        super().__init__(
            content=self.form_content,
            padding=ft.padding.all(20),
            border_radius=10,
            **kwargs
        )
    
    def did_mount(self):
        """Apply theme after mounting."""
        super().did_mount()
        
        # Apply theme
        if not self.bgcolor:
            self.bgcolor = self.surface_color
        if not self.border:
            self.border = ft.border.all(1, self.outline_color)
            
        self.update()
    
    def _build_form(self) -> ft.Control:
        """Build the form UI from configuration."""
        controls = []
        
        # Title
        if self.config.title:
            controls.append(ft.Text(
                self.config.title,
                size=24,
                weight=ft.FontWeight.BOLD
            ))
            
        # Description
        if self.config.description:
            controls.append(ft.Text(
                self.config.description,
                size=14,
                color=ft.Colors.ON_SURFACE_VARIANT
            ))
            
        # Divider after header
        if self.config.title or self.config.description:
            controls.append(ft.Divider())
        
        # Build fields
        if self.config.columns > 1:
            # Multi-column layout
            field_rows = self._build_field_grid()
            controls.extend(field_rows)
        else:
            # Single column layout
            for field_def in self.fields:
                if not field_def.hidden:
                    field_control = self._build_field(field_def)
                    controls.append(field_control)
        
        # Buttons
        button_row = self._build_buttons()
        controls.append(button_row)
        
        return ft.Column(
            controls=controls,
            spacing=self.config.spacing,
            scroll=ft.ScrollMode.AUTO
        )
    
    def _build_field_grid(self) -> List[ft.Control]:
        """Build fields in a grid layout."""
        rows = []
        current_row = []
        current_col_count = 0
        
        for field_def in self.fields:
            if field_def.hidden:
                continue
                
            # Determine column span
            col_span = 1
            if field_def.col:
                if isinstance(field_def.col, int):
                    col_span = field_def.col
                else:
                    # Responsive column span
                    col_span = field_def.col.get('md', 1)
            
            # Check if field fits in current row
            if current_col_count + col_span > self.config.columns:
                # Start new row
                if current_row:
                    rows.append(ft.Row(current_row, spacing=self.config.spacing))
                current_row = []
                current_col_count = 0
            
            # Build field
            field_control = self._build_field(field_def)
            
            # Wrap in container for proper sizing
            field_container = ft.Container(
                content=field_control,
                expand=col_span
            )
            
            current_row.append(field_container)
            current_col_count += col_span
        
        # Add last row
        if current_row:
            rows.append(ft.Row(current_row, spacing=self.config.spacing))
            
        return rows
    
    def _build_field(self, field_def: FormField) -> ft.Control:
        """Build a single form field."""
        # Create validators
        validators = self._create_validators(field_def)
        
        # Build field based on type
        if field_def.type == FieldType.TEXT:
            control = SecureTextField(
                label=self._get_field_label(field_def),
                value=field_def.default_value or "",
                placeholder=field_def.placeholder,
                validators=validators,
                disabled=field_def.disabled,
                read_only=field_def.read_only,
                prefix_icon=field_def.icon,
                prefix_text=field_def.prefix_text,
                suffix_text=field_def.suffix_text,
                on_change=field_def.on_change
            )
            
        elif field_def.type == FieldType.EMAIL:
            control = SecureEmailField(
                label=self._get_field_label(field_def),
                value=field_def.default_value or "",
                placeholder=field_def.placeholder,
                required=field_def.required,
                disabled=field_def.disabled,
                read_only=field_def.read_only,
                prefix_icon=field_def.icon or ft.Icons.EMAIL,
                on_change=field_def.on_change
            )
            
        elif field_def.type == FieldType.PASSWORD:
            control = SecurePasswordField(
                label=self._get_field_label(field_def),
                value=field_def.default_value or "",
                placeholder=field_def.placeholder,
                required=field_def.required,
                disabled=field_def.disabled,
                prefix_icon=field_def.icon or ft.Icons.LOCK,
                on_change=field_def.on_change
            )
            
        elif field_def.type == FieldType.NUMBER:
            control = SecureTextField(
                label=self._get_field_label(field_def),
                value=str(field_def.default_value) if field_def.default_value is not None else "",
                placeholder=field_def.placeholder,
                validators=validators,
                keyboard_type=ft.KeyboardType.NUMBER,
                disabled=field_def.disabled,
                read_only=field_def.read_only,
                prefix_icon=field_def.icon,
                prefix_text=field_def.prefix_text,
                suffix_text=field_def.suffix_text,
                on_change=field_def.on_change
            )
            
        elif field_def.type == FieldType.PHONE:
            control = SecureTextField(
                label=self._get_field_label(field_def),
                value=field_def.default_value or "",
                placeholder=field_def.placeholder,
                sanitizer=InputSanitizer.sanitize_phone,
                validators=validators,
                keyboard_type=ft.KeyboardType.PHONE,
                disabled=field_def.disabled,
                read_only=field_def.read_only,
                prefix_icon=field_def.icon or ft.Icons.PHONE,
                on_change=field_def.on_change
            )
            
        elif field_def.type == FieldType.TEXTAREA:
            control = SecureTextArea(
                label=self._get_field_label(field_def),
                value=field_def.default_value or "",
                min_lines=field_def.rows,
                max_lines=field_def.rows * 2,
                validators=validators,
                disabled=field_def.disabled,
                read_only=field_def.read_only,
                on_change=field_def.on_change
            )
            
        elif field_def.type == FieldType.DROPDOWN:
            control = SecureDropdown(
                label=self._get_field_label(field_def),
                options=field_def.options or [],
                value=field_def.default_value,
                required=field_def.required,
                disabled=field_def.disabled
            )
            
        elif field_def.type == FieldType.CHECKBOX:
            control = ft.Checkbox(
                label=field_def.label,
                value=bool(field_def.default_value),
                disabled=field_def.disabled
            )
            
        elif field_def.type == FieldType.SWITCH:
            control = ft.Switch(
                label=field_def.label,
                value=bool(field_def.default_value),
                disabled=field_def.disabled
            )
            
        elif field_def.type == FieldType.SLIDER:
            control = ft.Slider(
                label=field_def.label,
                value=field_def.default_value or field_def.min_value or 0,
                min=field_def.min_value or 0,
                max=field_def.max_value or 100,
                divisions=int((field_def.max_value or 100 - field_def.min_value or 0) / (field_def.step or 1)),
                disabled=field_def.disabled
            )
            
        else:
            # Default to text field
            control = SecureTextField(
                label=self._get_field_label(field_def),
                value=str(field_def.default_value) if field_def.default_value else "",
                validators=validators,
                disabled=field_def.disabled,
                read_only=field_def.read_only
            )
        
        # Store control reference
        self.field_controls[field_def.name] = control
        
        # Add help text if provided
        if field_def.help_text:
            return ft.Column([
                control,
                ft.Text(
                    field_def.help_text,
                    size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ], spacing=5)
            
        return control
    
    def _get_field_label(self, field_def: FormField) -> str:
        """Get field label with required indicator."""
        label = field_def.label
        
        if field_def.required and self.config.show_required_indicator:
            label += " *"
            
        return label
    
    def _create_validators(self, field_def: FormField) -> List[Validator]:
        """Create validators for a field."""
        validators = []
        
        # Required validator
        if field_def.required:
            validators.append(RequiredValidator(f"{field_def.label} is required"))
        
        # Type-specific validators
        if field_def.type == FieldType.EMAIL:
            validators.append(EmailValidator())
            
        elif field_def.type == FieldType.NUMBER:
            validators.append(NumericValidator(
                min_value=field_def.min_value,
                max_value=field_def.max_value,
                integer_only=True
            ))
            
        elif field_def.type == FieldType.PHONE:
            validators.append(CommonValidators.phone())
        
        # Validation rules
        for validation in field_def.validations:
            if validation.rule == ValidationRule.MIN_LENGTH:
                validators.append(LengthValidator(
                    min_length=validation.value,
                    min_message=validation.message
                ))
                
            elif validation.rule == ValidationRule.MAX_LENGTH:
                validators.append(LengthValidator(
                    max_length=validation.value,
                    max_message=validation.message
                ))
                
            elif validation.rule == ValidationRule.PATTERN:
                validators.append(PatternValidator(
                    pattern=validation.value,
                    message=validation.message or "Invalid format"
                ))
                
            elif validation.rule == ValidationRule.MIN_VALUE:
                validators.append(NumericValidator(
                    min_value=validation.value,
                    min_message=validation.message
                ))
                
            elif validation.rule == ValidationRule.MAX_VALUE:
                validators.append(NumericValidator(
                    max_value=validation.value,
                    max_message=validation.message
                ))
                
            elif validation.rule == ValidationRule.CUSTOM and validation.value:
                validators.append(validation.value)
        
        return validators
    
    def _build_buttons(self) -> ft.Control:
        """Build form buttons."""
        buttons = []
        
        # Cancel button
        if self.config.show_cancel:
            buttons.append(ft.TextButton(
                self.config.cancel_text,
                on_click=lambda e: self._handle_cancel()
            ))
        
        # Submit button
        buttons.append(ft.ElevatedButton(
            self.config.submit_text,
            on_click=lambda e: self._handle_submit()
        ))
        
        return ft.Row(
            buttons,
            alignment=ft.MainAxisAlignment.END,
            spacing=10
        )
    
    def _handle_submit(self):
        """Handle form submission."""
        # Validate if enabled
        if self.config.validate_on_submit:
            if not self.validate():
                self._show_error(self.config.error_message)
                return
        
        # Get form data
        data = self.get_form_data()
        
        # Call submit handler
        if self.on_submit:
            try:
                self.on_submit(data)
                self._show_success(self.config.success_message)
            except Exception as e:
                logger.error(f"Form submission error: {e}")
                self._show_error(str(e))
        else:
            self._show_success(self.config.success_message)
    
    def _handle_cancel(self):
        """Handle form cancellation."""
        if self.on_cancel:
            self.on_cancel()
        else:
            self.reset()
    
    def validate(self) -> bool:
        """Validate all form fields."""
        all_valid = True
        
        for field_def in self.fields:
            control = self.field_controls.get(field_def.name)
            
            if control and hasattr(control, 'validate'):
                if not control.validate():
                    all_valid = False
                    
        return all_valid
    
    def get_form_data(self) -> Dict[str, Any]:
        """Get all form field values."""
        data = {}
        
        for field_def in self.fields:
            control = self.field_controls.get(field_def.name)
            
            if control:
                # Get value based on control type
                if hasattr(control, 'sanitized_value'):
                    value = control.sanitized_value
                elif hasattr(control, 'value'):
                    value = control.value
                else:
                    value = None
                    
                # Convert number fields
                if field_def.type == FieldType.NUMBER and value:
                    try:
                        value = int(value) if '.' not in str(value) else float(value)
                    except (ValueError, TypeError):
                        pass
                        
                data[field_def.name] = value
                
        return data
    
    def set_form_data(self, data: Dict[str, Any]):
        """Set form field values."""
        for name, value in data.items():
            control = self.field_controls.get(name)
            
            if control and hasattr(control, 'value'):
                control.value = value
                control.update()
    
    def reset(self):
        """Reset all form fields to defaults."""
        for field_def in self.fields:
            control = self.field_controls.get(field_def.name)
            
            if control:
                if hasattr(control, 'value'):
                    control.value = field_def.default_value or ""
                    
                if hasattr(control, '_clear_error'):
                    control._clear_error()
                    
                control.update()
    
    def _show_error(self, message: str):
        """Show error message."""
        if self.page:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(message),
                    bgcolor=ft.Colors.ERROR_CONTAINER
                )
            )
    
    def _show_success(self, message: str):
        """Show success message."""
        if self.page:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(message),
                    bgcolor=ft.Colors.PRIMARY_CONTAINER
                )
            )