"""
Radio button components with theme integration.
"""

from typing import Optional, List, Union, Callable, Any
import flet as ft
from .theme_helper import get_theme_mode


class RadioOption:
    """Represents a single radio button option.
    
    Example:
        ```python
        option = RadioOption(
            value="premium",
            label="Premium Plan",
            description="All features included"
        )
        ```
    """
    
    def __init__(
        self,
        value: str,
        label: str,
        description: Optional[str] = None,
        disabled: bool = False
    ):
        self.value = value
        self.label = label
        self.description = description
        self.disabled = disabled


class ThemedRadioGroup(ft.Container):
    """Radio button group with automatic theme-aware styling.
    
    A group of radio buttons that allows single selection from
    multiple options, with consistent theme styling.
    
    Example:
        ```python
        payment_options = ThemedRadioGroup(
            label="Payment Method",
            options=[
                RadioOption("card", "Credit Card"),
                RadioOption("paypal", "PayPal"),
                RadioOption("bank", "Bank Transfer", "Direct bank transfer")
            ],
            value="card",
            on_change=handle_payment_change
        )
        ```
    """
    
    def __init__(
        self,
        label: Optional[str] = None,
        options: List[Union[RadioOption, tuple, str]] = None,
        value: Optional[str] = None,
        on_change: Optional[Callable[[str], None]] = None,
        orientation: str = "vertical",
        spacing: int = 10,
        **kwargs
    ):
        self._on_change = on_change
        self._current_value = value
        self._radio_buttons = []
        
        # Convert options to RadioOption objects
        self._options = self._normalize_options(options or [])
        
        # Create content
        controls = []
        
        # Add label if provided
        if label:
            self._label = ft.Text(
                label,
                size=16,
                weight=ft.FontWeight.W_500
            )
            controls.append(self._label)
            controls.append(ft.Container(height=5))  # Spacing
        else:
            self._label = None
            
        # Create radio group
        self._radio_group = ft.RadioGroup(
            value=value,
            on_change=self._handle_change
        )
        
        # Create radio buttons
        radio_controls = []
        for option in self._options:
            radio_button = self._create_radio_button(option)
            self._radio_buttons.append(radio_button)
            radio_controls.append(radio_button)
            
        # Arrange radio buttons
        if orientation == "horizontal":
            self._radio_group.content = ft.Row(
                controls=radio_controls,
                spacing=spacing * 2
            )
        else:
            self._radio_group.content = ft.Column(
                controls=radio_controls,
                spacing=spacing
            )
            
        controls.append(self._radio_group)
        
        # Set container content
        content = ft.Column(controls=controls, spacing=0)
        
        super().__init__(content=content, **kwargs)
        
    def _normalize_options(self, options: List[Union[RadioOption, tuple, str]]) -> List[RadioOption]:
        """Convert various option formats to RadioOption objects."""
        normalized = []
        
        for option in options:
            if isinstance(option, RadioOption):
                normalized.append(option)
            elif isinstance(option, tuple):
                if len(option) >= 3:
                    normalized.append(RadioOption(option[0], option[1], option[2]))
                elif len(option) >= 2:
                    normalized.append(RadioOption(option[0], option[1]))
                else:
                    normalized.append(RadioOption(str(option[0]), str(option[0])))
            else:
                # String option
                normalized.append(RadioOption(str(option), str(option)))
                
        return normalized
        
    def _create_radio_button(self, option: RadioOption) -> ft.Radio:
        """Create a themed radio button for an option."""
        # Create label with optional description
        if option.description:
            label_content = ft.Column(
                controls=[
                    ft.Text(option.label, size=14),
                    ft.Text(
                        option.description,
                        size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    )
                ],
                spacing=2
            )
        else:
            label_content = ft.Text(option.label, size=14)
            
        radio = ft.Radio(
            value=option.value,
            label_content=label_content,
            disabled=option.disabled
        )
        
        return radio
        
    def _handle_change(self, e):
        """Handle radio selection change."""
        self._current_value = e.control.value
        
        if self._on_change:
            self._on_change(self._current_value)
            
    def did_mount(self):
        """Apply theme styling after control is mounted."""
        super().did_mount()
        
        # Determine theme mode
        is_light = get_theme_mode(self.page if hasattr(self, 'page') else None) == 'light'
        
        # Apply theme to label
        if self._label:
            if is_light:
                self._label.color = ft.Colors.BLACK
            else:
                self._label.color = ft.Colors.WHITE
                
        # Apply theme to radio buttons
        for i, radio in enumerate(self._radio_buttons):
            if is_light:
                radio.fill_color = {
                    ft.ControlState.DEFAULT: ft.Colors.ON_SURFACE_VARIANT,
                    ft.ControlState.SELECTED: ft.Colors.PRIMARY,
                }
                # Update label colors
                if isinstance(radio.label_content, ft.Column):
                    radio.label_content.controls[0].color = ft.Colors.BLACK
                    if len(radio.label_content.controls) > 1:
                        radio.label_content.controls[1].color = ft.Colors.ON_SURFACE_VARIANT
                elif isinstance(radio.label_content, ft.Text):
                    radio.label_content.color = ft.Colors.BLACK
            else:
                radio.fill_color = {
                    ft.ControlState.DEFAULT: ft.Colors.ON_SURFACE_VARIANT,
                    ft.ControlState.SELECTED: ft.Colors.ORANGE_400,
                }
                # Update label colors
                if isinstance(radio.label_content, ft.Column):
                    radio.label_content.controls[0].color = ft.Colors.WHITE
                    if len(radio.label_content.controls) > 1:
                        radio.label_content.controls[1].color = ft.Colors.GREY_400
                elif isinstance(radio.label_content, ft.Text):
                    radio.label_content.color = ft.Colors.WHITE
                    
        if hasattr(self, 'update'):
            self.update()
            
    @property
    def value(self) -> Optional[str]:
        """Get current selected value."""
        return self._current_value
        
    @value.setter
    def value(self, value: Optional[str]):
        """Set selected value."""
        self._current_value = value
        self._radio_group.value = value
        if hasattr(self, 'update'):
            self.update()
            
    def add_option(self, option: Union[RadioOption, tuple, str]):
        """Add a new option to the group."""
        normalized = self._normalize_options([option])[0]
        self._options.append(normalized)
        
        # Create and add radio button
        radio_button = self._create_radio_button(normalized)
        self._radio_buttons.append(radio_button)
        
        # Add to the appropriate container
        if isinstance(self._radio_group.content, ft.Row):
            self._radio_group.content.controls.append(radio_button)
        else:
            self._radio_group.content.controls.append(radio_button)
            
        if hasattr(self, 'update'):
            self.update()
            
    def set_enabled(self, value: str, enabled: bool):
        """Enable or disable a specific option."""
        for i, option in enumerate(self._options):
            if option.value == value:
                option.disabled = not enabled
                self._radio_buttons[i].disabled = not enabled
                break
                
        if hasattr(self, 'update'):
            self.update()