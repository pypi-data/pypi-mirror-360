"""
Icon button components with theme integration.
"""

from typing import Optional, Callable, Any, Union
import flet as ft
from .theme_interface import get_theme_colors


class ThemedIconButton(ft.IconButton):
    """Icon button with automatic theme-aware styling.
    
    Provides icon-only buttons suitable for toolbars, action bars,
    and compact UI elements.
    
    Example:
        ```python
        button = ThemedIconButton(
            icon=ft.Icons.FAVORITE,
            on_click=lambda e: toggle_favorite(),
            selected_icon=ft.Icons.FAVORITE_BORDER,
            selected=False
        )
        ```
    """
    
    def __init__(
        self,
        icon: Optional[Union[str, ft.Icons]] = None,
        icon_size: Optional[float] = None,
        variant: str = "default",
        selected: bool = False,
        selected_icon: Optional[Union[str, ft.Icons]] = None,
        tooltip: Optional[str] = None,
        disabled: bool = False,
        on_click: Optional[Callable[[Any], None]] = None,
        **kwargs
    ):
        # Store configuration
        self._variant = variant
        self._custom_style = kwargs.pop('style', None)
        
        # Initialize button
        super().__init__(
            icon=icon,
            icon_size=icon_size,
            selected=selected,
            selected_icon=selected_icon,
            tooltip=tooltip,
            disabled=disabled,
            on_click=on_click,
            **kwargs
        )
    
    def did_mount(self):
        """Apply theme styling after button is mounted to page."""
        super().did_mount()
        
        # Get theme from page
        theme = get_theme_colors(self.page) if hasattr(self, 'page') else None
        
        # Apply icon button style
        self.style = self._create_icon_style(theme)
        
        if hasattr(self, 'update'):
            self.update()
    
    def _create_icon_style(self, theme) -> ft.ButtonStyle:
        """Create icon button style based on theme and variant."""
        if theme:
            # Get colors based on variant
            if self._variant == "primary":
                color = theme.primary
                selected_color = theme.primary
                hover_bg = theme.with_opacity(0.08, theme.primary) if hasattr(theme, 'with_opacity') else None
            elif self._variant == "secondary":
                color = theme.secondary
                selected_color = theme.secondary
                hover_bg = theme.with_opacity(0.08, theme.secondary) if hasattr(theme, 'with_opacity') else None
            elif self._variant == "error":
                color = theme.error
                selected_color = theme.error
                hover_bg = theme.with_opacity(0.08, theme.error) if hasattr(theme, 'with_opacity') else None
            else:
                # Default variant
                color = theme.on_surface_variant
                selected_color = theme.primary
                hover_bg = theme.with_opacity(0.08, theme.on_surface) if hasattr(theme, 'with_opacity') else None
                
            disabled_color = theme.on_surface_variant
            pressed_bg = theme.with_opacity(0.12, color) if hasattr(theme, 'with_opacity') else None
        else:
            # Default colors
            default_colors = {
                "primary": "#2196F3",
                "secondary": "#757575",
                "error": "#F44336",
                "default": "#757575"
            }
            color = default_colors.get(self._variant, default_colors["default"])
            selected_color = color
            disabled_color = "#9E9E9E"
            hover_bg = None
            pressed_bg = None
        
        # Build style
        style = ft.ButtonStyle(
            color={
                ft.ControlState.DEFAULT: color,
                ft.ControlState.SELECTED: selected_color,
                ft.ControlState.DISABLED: disabled_color,
            },
        )
        
        # Add background colors if available
        if hover_bg or pressed_bg:
            style.bgcolor = {}
            if hover_bg:
                style.bgcolor[ft.ControlState.HOVERED] = hover_bg
            if pressed_bg:
                style.bgcolor[ft.ControlState.PRESSED] = pressed_bg
        
        # Merge with custom style if provided
        if self._custom_style:
            for attr in ['color', 'bgcolor', 'padding', 'shape']:
                if hasattr(self._custom_style, attr) and getattr(self._custom_style, attr) is not None:
                    setattr(style, attr, getattr(self._custom_style, attr))
        
        return style


class ThemedFloatingActionButton(ft.FloatingActionButton):
    """Floating action button with theme integration.
    
    Provides a prominent circular button for primary actions,
    typically positioned in the bottom-right corner of a view.
    
    Example:
        ```python
        fab = ThemedFloatingActionButton(
            icon=ft.Icons.ADD,
            on_click=lambda e: create_new_item(),
            mini=False,
            tooltip="Create New"
        )
        ```
    """
    
    def __init__(
        self,
        icon: Optional[Union[str, ft.Icons]] = None,
        text: Optional[str] = None,
        variant: str = "primary",
        mini: bool = False,
        shape: Optional[ft.ControlState] = None,
        tooltip: Optional[str] = None,
        disabled: bool = False,
        on_click: Optional[Callable[[Any], None]] = None,
        **kwargs
    ):
        # Store configuration
        self._variant = variant
        
        # Set default shape if not provided
        if shape is None:
            shape = ft.CircleBorder() if mini else ft.RoundedRectangleBorder(radius=16)
        
        # Initialize FAB
        super().__init__(
            icon=icon,
            text=text,
            mini=mini,
            shape=shape,
            tooltip=tooltip,
            disabled=disabled,
            on_click=on_click,
            **kwargs
        )
    
    def did_mount(self):
        """Apply theme styling after button is mounted to page."""
        super().did_mount()
        
        # Get theme from page
        theme = get_theme_colors(self.page) if hasattr(self, 'page') else None
        
        # Apply FAB styling
        if theme:
            if self._variant == "primary":
                self.bgcolor = theme.primary_container
                self.foreground_color = theme.on_primary_container
            elif self._variant == "secondary":
                self.bgcolor = theme.secondary_container
                self.foreground_color = theme.on_secondary_container
            elif self._variant == "surface":
                self.bgcolor = theme.surface
                self.foreground_color = theme.primary
            else:
                # Default to primary
                self.bgcolor = theme.primary_container
                self.foreground_color = theme.on_primary_container
        else:
            # Default colors
            if self._variant == "primary":
                self.bgcolor = "#E3F2FD"  # Light blue
                self.foreground_color = "#1976D2"  # Dark blue
            elif self._variant == "secondary":
                self.bgcolor = "#F5F5F5"  # Light grey
                self.foreground_color = "#616161"  # Dark grey
            else:
                self.bgcolor = "#FFFFFF"
                self.foreground_color = "#2196F3"
        
        if hasattr(self, 'update'):
            self.update()