"""
Checkbox and switch components with theme integration.
"""

from typing import Optional, Callable, Any
import flet as ft
from .theme_helper import get_theme_mode


class ThemedCheckbox(ft.Checkbox):
    """Checkbox with automatic theme-aware styling.
    
    A checkbox control that adapts to the application theme,
    providing consistent styling across light and dark modes.
    
    Example:
        ```python
        terms_checkbox = ThemedCheckbox(
            label="I agree to the terms and conditions",
            value=False,
            on_change=handle_terms_change
        )
        ```
    """
    
    def __init__(
        self,
        label: Optional[str] = None,
        value: bool = False,
        tristate: bool = False,
        on_change: Optional[Callable[[Any], None]] = None,
        **kwargs
    ):
        # Store theme-related overrides
        self._fill_color = kwargs.pop('fill_color', None)
        self._check_color = kwargs.pop('check_color', None)
        self._label_style = kwargs.pop('label_style', None)
        
        super().__init__(
            label=label,
            value=value,
            tristate=tristate,
            on_change=on_change,
            **kwargs
        )
        
    def did_mount(self):
        """Apply theme styling after control is mounted."""
        super().did_mount()
        
        # Determine theme mode
        is_light = get_theme_mode(self.page if hasattr(self, 'page') else None) == 'light'
        
        # Apply theme-aware colors if not overridden
        if not self._fill_color:
            if is_light:
                self.fill_color = {
                    ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
                    ft.ControlState.SELECTED: ft.Colors.PRIMARY,
                }
            else:
                self.fill_color = {
                    ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
                    ft.ControlState.SELECTED: ft.Colors.ORANGE_400,
                }
                
        if not self._check_color:
            if is_light:
                self.check_color = ft.Colors.WHITE
            else:
                self.check_color = ft.Colors.BLACK
                
        if not self._label_style:
            if is_light:
                self.label_style = ft.TextStyle(
                    color=ft.Colors.BLACK,
                    size=14
                )
            else:
                self.label_style = ft.TextStyle(
                    color=ft.Colors.WHITE,
                    size=14
                )
                
        if hasattr(self, 'update'):
            self.update()


class ThemedSwitch(ft.Switch):
    """Switch with automatic theme-aware styling.
    
    A toggle switch control that adapts to the application theme,
    ideal for on/off settings.
    
    Example:
        ```python
        notifications_switch = ThemedSwitch(
            label="Enable notifications",
            value=True,
            on_change=handle_notifications_toggle
        )
        ```
    """
    
    def __init__(
        self,
        label: Optional[str] = None,
        value: bool = False,
        on_change: Optional[Callable[[Any], None]] = None,
        **kwargs
    ):
        # Store theme-related overrides
        self._active_color = kwargs.pop('active_color', None)
        self._active_track_color = kwargs.pop('active_track_color', None)
        self._inactive_thumb_color = kwargs.pop('inactive_thumb_color', None)
        self._inactive_track_color = kwargs.pop('inactive_track_color', None)
        self._label_style = kwargs.pop('label_style', None)
        
        super().__init__(
            label=label,
            value=value,
            on_change=on_change,
            **kwargs
        )
        
    def did_mount(self):
        """Apply theme styling after control is mounted."""
        super().did_mount()
        
        # Determine theme mode
        is_light = get_theme_mode(self.page if hasattr(self, 'page') else None) == 'light'
        
        # Apply theme-aware colors if not overridden
        if not self._active_color:
            if is_light:
                self.active_color = ft.Colors.PRIMARY
            else:
                self.active_color = ft.Colors.ORANGE_400
                
        if not self._active_track_color:
            if is_light:
                self.active_track_color = ft.Colors.with_opacity(0.5, ft.Colors.PRIMARY)
            else:
                self.active_track_color = ft.Colors.with_opacity(0.5, ft.Colors.ORANGE_400)
                
        if not self._inactive_thumb_color:
            if is_light:
                self.inactive_thumb_color = ft.Colors.GREY_400
            else:
                self.inactive_thumb_color = ft.Colors.GREY_600
                
        if not self._inactive_track_color:
            if is_light:
                self.inactive_track_color = ft.Colors.GREY_300
            else:
                self.inactive_track_color = ft.Colors.GREY_800
                
        if not self._label_style:
            if is_light:
                self.label_style = ft.TextStyle(
                    color=ft.Colors.BLACK,
                    size=14
                )
            else:
                self.label_style = ft.TextStyle(
                    color=ft.Colors.WHITE,
                    size=14
                )
                
        if hasattr(self, 'update'):
            self.update()