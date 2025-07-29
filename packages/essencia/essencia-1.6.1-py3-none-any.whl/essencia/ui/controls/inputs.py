"""
Themed input components for essencia.

This module provides theme-aware input controls that automatically adapt
to the configured theme provider.
"""

from typing import Optional, Any, Callable, List, Union
from datetime import datetime, date
import flet as ft

from .base import ThemedControl, ControlConfig, get_controls_config, DefaultTheme


class ThemedTextField(ThemedControl):
    """Theme-aware text field with consistent styling."""
    
    def __init__(self,
                 label: str = "",
                 value: str = "",
                 hint_text: Optional[str] = None,
                 helper_text: Optional[str] = None,
                 error_text: Optional[str] = None,
                 prefix_icon: Optional[str] = None,
                 suffix_icon: Optional[str] = None,
                 password: bool = False,
                 multiline: bool = False,
                 max_lines: Optional[int] = None,
                 min_lines: int = 1,
                 read_only: bool = False,
                 autofocus: bool = False,
                 capitalization: Optional[ft.TextCapitalization] = None,
                 keyboard_type: ft.KeyboardType = ft.KeyboardType.TEXT,
                 on_change: Optional[Callable] = None,
                 on_submit: Optional[Callable] = None,
                 on_focus: Optional[Callable] = None,
                 on_blur: Optional[Callable] = None,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.label = label
        self.value = value
        self.hint_text = hint_text
        self.helper_text = helper_text
        self.error_text = error_text
        self.prefix_icon = prefix_icon
        self.suffix_icon = suffix_icon
        self.password = password
        self.multiline = multiline
        self.max_lines = max_lines
        self.min_lines = min_lines
        self.read_only = read_only
        self.autofocus = autofocus
        self.capitalization = capitalization
        self.keyboard_type = keyboard_type
        self.on_change = on_change
        self.on_submit = on_submit
        self.on_focus = on_focus
        self.on_blur = on_blur
    
    def build(self) -> ft.TextField:
        """Build the themed text field."""
        theme = self.theme or DefaultTheme()
        
        self._control = ft.TextField(
            label=self.label,
            value=self.value,
            hint_text=self.hint_text,
            helper_text=self.helper_text,
            error_text=self.error_text,
            prefix_icon=self.prefix_icon,
            suffix_icon=self.suffix_icon,
            password=self.password,
            multiline=self.multiline,
            max_lines=self.max_lines,
            min_lines=self.min_lines,
            read_only=self.read_only,
            autofocus=self.autofocus,
            capitalization=self.capitalization,
            keyboard_type=self.keyboard_type,
            on_change=self.on_change,
            on_submit=self.on_submit,
            on_focus=self.on_focus,
            on_blur=self.on_blur,
            visible=self.config.visible,
            disabled=self.config.disabled,
            tooltip=self.config.tooltip,
            data=self.config.data,
            # Theme styling
            color=theme.on_surface,
            bgcolor=theme.surface,
            focused_color=theme.primary,
            focused_bgcolor=theme.surface,
            focused_border_color=theme.primary,
            error_style=ft.TextStyle(color=theme.error),
            label_style=ft.TextStyle(color=theme.on_surface_variant),
            hint_style=ft.TextStyle(color=theme.on_surface_variant),
            helper_style=ft.TextStyle(color=theme.on_surface_variant, size=12),
            border_color=theme.outline,
            cursor_color=theme.primary,
            selection_color=theme.primary_container,
        )
        
        return self._control
    
    def _apply_theme(self) -> None:
        """Apply theme to text field."""
        if self._control and self.theme:
            self._control.color = self.theme.on_surface
            self._control.bgcolor = self.theme.surface
            self._control.focused_color = self.theme.primary
            self._control.focused_border_color = self.theme.primary
            self._control.border_color = self.theme.outline
            self._control.cursor_color = self.theme.primary
            self._control.selection_color = self.theme.primary_container
            self._control.update()


class ThemedDatePicker(ThemedControl):
    """Theme-aware date picker with consistent styling."""
    
    def __init__(self,
                 label: str = "",
                 value: Optional[Union[datetime, date]] = None,
                 first_date: Optional[datetime] = None,
                 last_date: Optional[datetime] = None,
                 helper_text: Optional[str] = None,
                 error_text: Optional[str] = None,
                 on_change: Optional[Callable] = None,
                 date_format: Optional[str] = None,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.label = label
        self.value = value
        self.first_date = first_date or datetime(1900, 1, 1)
        self.last_date = last_date or datetime(2100, 12, 31)
        self.helper_text = helper_text
        self.error_text = error_text
        self.on_change = on_change
        self.date_format = date_format or get_controls_config().date_format
        self._picker = None
        self._text_field = None
    
    def build(self) -> ft.Control:
        """Build the themed date picker."""
        theme = self.theme or DefaultTheme()
        
        # Create the date picker
        self._picker = ft.DatePicker(
            first_date=self.first_date,
            last_date=self.last_date,
            value=self.value if isinstance(self.value, datetime) else None,
            date_picker_mode=ft.DatePickerMode.DAY,
            on_change=self._handle_date_change,
        )
        
        # Format the display value
        display_value = ""
        if self.value:
            if isinstance(self.value, datetime):
                display_value = self.value.strftime(self.date_format)
            elif isinstance(self.value, date):
                display_value = self.value.strftime(self.date_format)
        
        # Create the text field that shows the date
        self._text_field = ThemedTextField(
            label=self.label,
            value=display_value,
            helper_text=self.helper_text,
            error_text=self.error_text,
            read_only=True,
            suffix_icon=ft.Icons.CALENDAR_TODAY,
            config=self.config,
        )
        
        text_field_control = self._text_field.build()
        text_field_control.on_click = self._open_picker
        
        self._control = text_field_control
        return self._control
    
    def _handle_date_change(self, e):
        """Handle date selection."""
        if e.data and self._text_field and self._text_field._control:
            # Parse the date string
            selected_date = datetime.fromisoformat(e.data.replace('Z', '+00:00'))
            self.value = selected_date
            
            # Update the text field
            self._text_field._control.value = selected_date.strftime(self.date_format)
            self._text_field._control.update()
            
            # Call user's on_change handler
            if self.on_change:
                self.on_change(e)
    
    def _open_picker(self, e):
        """Open the date picker."""
        if e.page and self._picker:
            open_themed_date_picker(e.page, self._picker)
    
    def get_picker(self) -> ft.DatePicker:
        """Get the date picker control for manual handling."""
        return self._picker


def open_themed_date_picker(page: ft.Page, picker: ft.DatePicker) -> None:
    """Helper function to properly open a themed date picker."""
    if picker not in page.overlay:
        page.overlay.append(picker)
    picker.open = True
    page.update()
    page.open(picker)


class ThemedDropdown(ThemedControl):
    """Theme-aware dropdown with consistent styling."""
    
    def __init__(self,
                 label: str = "",
                 value: Optional[str] = None,
                 options: Optional[List[ft.dropdown.Option]] = None,
                 helper_text: Optional[str] = None,
                 error_text: Optional[str] = None,
                 on_change: Optional[Callable] = None,
                 autofocus: bool = False,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.label = label
        self.value = value
        self.options = options or []
        self.helper_text = helper_text
        self.error_text = error_text
        self.on_change = on_change
        self.autofocus = autofocus
    
    def build(self) -> ft.Dropdown:
        """Build the themed dropdown."""
        theme = self.theme or DefaultTheme()
        
        self._control = ft.Dropdown(
            label=self.label,
            value=self.value,
            options=self.options,
            helper_text=self.helper_text,
            error_text=self.error_text,
            on_change=self.on_change,
            autofocus=self.autofocus,
            visible=self.config.visible,
            disabled=self.config.disabled,
            tooltip=self.config.tooltip,
            data=self.config.data,
            # Theme styling
            color=theme.on_surface,
            bgcolor=theme.surface,
            focused_color=theme.primary,
            focused_bgcolor=theme.surface,
            focused_border_color=theme.primary,
            error_style=ft.TextStyle(color=theme.error),
            label_style=ft.TextStyle(color=theme.on_surface_variant),
            hint_style=ft.TextStyle(color=theme.on_surface_variant),
            helper_style=ft.TextStyle(color=theme.on_surface_variant, size=12),
            border_color=theme.outline,
        )
        
        return self._control


class ThemedCheckbox(ThemedControl):
    """Theme-aware checkbox with consistent styling."""
    
    def __init__(self,
                 label: str = "",
                 value: bool = False,
                 on_change: Optional[Callable] = None,
                 tristate: bool = False,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.label = label
        self.value = value
        self.on_change = on_change
        self.tristate = tristate
    
    def build(self) -> ft.Checkbox:
        """Build the themed checkbox."""
        theme = self.theme or DefaultTheme()
        
        self._control = ft.Checkbox(
            label=self.label,
            value=self.value,
            on_change=self.on_change,
            tristate=self.tristate,
            visible=self.config.visible,
            disabled=self.config.disabled,
            tooltip=self.config.tooltip,
            data=self.config.data,
            # Theme styling
            active_color=theme.primary,
            check_color=theme.on_primary,
            overlay_color=theme.primary_container,
            label_style=ft.TextStyle(color=theme.on_surface),
        )
        
        return self._control


class ThemedRadioGroup(ThemedControl):
    """Theme-aware radio group with consistent styling."""
    
    def __init__(self,
                 label: str = "",
                 value: Optional[str] = None,
                 options: Optional[List[ft.Radio]] = None,
                 on_change: Optional[Callable] = None,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.label = label
        self.value = value
        self.options = options or []
        self.on_change = on_change
    
    def build(self) -> ft.Column:
        """Build the themed radio group."""
        theme = self.theme or DefaultTheme()
        
        # Apply theme to each radio button
        for radio in self.options:
            radio.active_color = theme.primary
            radio.overlay_color = theme.primary_container
            if hasattr(radio, 'label_style'):
                radio.label_style = ft.TextStyle(color=theme.on_surface)
        
        # Create radio group
        radio_group = ft.RadioGroup(
            value=self.value,
            on_change=self.on_change,
            content=ft.Column(
                controls=self.options,
                spacing=get_controls_config().default_spacing,
            )
        )
        
        # Create container with label
        controls = []
        if self.label:
            controls.append(ft.Text(
                self.label,
                size=14,
                color=theme.on_surface_variant,
                weight=ft.FontWeight.W_500,
            ))
        controls.append(radio_group)
        
        self._control = ft.Column(
            controls=controls,
            spacing=get_controls_config().default_spacing,
            visible=self.config.visible,
            disabled=self.config.disabled,
            tooltip=self.config.tooltip,
            data=self.config.data,
        )
        
        return self._control


class ThemedSlider(ThemedControl):
    """Theme-aware slider with consistent styling."""
    
    def __init__(self,
                 label: str = "",
                 value: float = 0,
                 min: float = 0,
                 max: float = 100,
                 divisions: Optional[int] = None,
                 on_change: Optional[Callable] = None,
                 on_change_start: Optional[Callable] = None,
                 on_change_end: Optional[Callable] = None,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.label = label
        self.value = value
        self.min = min
        self.max = max
        self.divisions = divisions
        self.on_change = on_change
        self.on_change_start = on_change_start
        self.on_change_end = on_change_end
    
    def build(self) -> ft.Control:
        """Build the themed slider."""
        theme = self.theme or DefaultTheme()
        
        slider = ft.Slider(
            value=self.value,
            min=self.min,
            max=self.max,
            divisions=self.divisions,
            label="{value}",
            on_change=self.on_change,
            on_change_start=self.on_change_start,
            on_change_end=self.on_change_end,
            # Theme styling
            active_color=theme.primary,
            inactive_color=theme.surface_variant,
            thumb_color=theme.primary,
            overlay_color=theme.primary_container,
        )
        
        if self.label:
            self._control = ft.Column(
                controls=[
                    ft.Text(
                        self.label,
                        size=14,
                        color=theme.on_surface_variant,
                        weight=ft.FontWeight.W_500,
                    ),
                    slider,
                ],
                spacing=get_controls_config().default_spacing,
                visible=self.config.visible,
                disabled=self.config.disabled,
                tooltip=self.config.tooltip,
                data=self.config.data,
            )
        else:
            slider.visible = self.config.visible
            slider.disabled = self.config.disabled
            slider.tooltip = self.config.tooltip
            slider.data = self.config.data
            self._control = slider
        
        return self._control


class ThemedSwitch(ThemedControl):
    """Theme-aware switch with consistent styling."""
    
    def __init__(self,
                 label: str = "",
                 value: bool = False,
                 on_change: Optional[Callable] = None,
                 label_position: ft.LabelPosition = ft.LabelPosition.RIGHT,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.label = label
        self.value = value
        self.on_change = on_change
        self.label_position = label_position
    
    def build(self) -> ft.Switch:
        """Build the themed switch."""
        theme = self.theme or DefaultTheme()
        
        self._control = ft.Switch(
            label=self.label,
            value=self.value,
            on_change=self.on_change,
            label_position=self.label_position,
            visible=self.config.visible,
            disabled=self.config.disabled,
            tooltip=self.config.tooltip,
            data=self.config.data,
            # Theme styling
            active_color=theme.primary,
            active_track_color=theme.primary_container,
            inactive_thumb_color=theme.outline,
            inactive_track_color=theme.surface_variant,
            label_style=ft.TextStyle(color=theme.on_surface),
        )
        
        return self._control