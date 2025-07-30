"""
Outlined button components with theme integration.
"""

from typing import Optional, Callable, Any
import flet as ft
from .theme_interface import get_theme_colors


class ThemedOutlinedButton(ft.OutlinedButton):
    """Outlined button with automatic theme-aware styling.
    
    Provides a button with border styling that adapts to the application theme.
    Suitable for secondary actions where less visual prominence is desired.
    
    Example:
        ```python
        button = ThemedOutlinedButton(
            text="Cancel",
            on_click=lambda e: page.go("/"),
            variant="primary"
        )
        ```
    """
    
    def __init__(
        self,
        text: Optional[str] = None,
        variant: str = "primary",
        size: str = "medium",
        icon: Optional[str] = None,
        icon_size: Optional[float] = None,
        disabled: bool = False,
        on_click: Optional[Callable[[Any], None]] = None,
        **kwargs
    ):
        # Store configuration
        self._variant = variant
        self._size = size
        self._custom_style = kwargs.pop('style', None)
        
        # Initialize button
        super().__init__(
            text=text,
            icon=icon,
            icon_size=icon_size,
            disabled=disabled,
            on_click=on_click,
            **kwargs
        )
    
    def did_mount(self):
        """Apply theme styling after button is mounted to page."""
        super().did_mount()
        
        # Get theme from page
        theme = get_theme_colors(self.page) if hasattr(self, 'page') else None
        
        # Apply outlined button style
        self.style = self._create_outlined_style(theme)
        
        if hasattr(self, 'update'):
            self.update()
    
    def _create_outlined_style(self, theme) -> ft.ButtonStyle:
        """Create outlined button style based on theme and variant."""
        # Size configurations
        sizes = {
            "small": {"padding": 8, "text_size": 12, "border_width": 1},
            "medium": {"padding": 12, "text_size": 14, "border_width": 1},
            "large": {"padding": 16, "text_size": 16, "border_width": 2},
        }
        
        size_config = sizes.get(self._size, sizes["medium"])
        
        if theme:
            # Get colors based on variant
            if self._variant == "primary":
                color = theme.primary
                border_color = theme.primary
                hover_border = theme.primary
                disabled_color = theme.on_surface_variant
                disabled_border = theme.outline_variant
            elif self._variant == "secondary":
                color = theme.secondary
                border_color = theme.secondary
                hover_border = theme.secondary
                disabled_color = theme.on_surface_variant
                disabled_border = theme.outline_variant
            elif self._variant == "error":
                color = theme.error
                border_color = theme.error
                hover_border = theme.error
                disabled_color = theme.on_surface_variant
                disabled_border = theme.outline_variant
            else:
                # Default to primary
                color = theme.primary
                border_color = theme.outline
                hover_border = theme.primary
                disabled_color = theme.on_surface_variant
                disabled_border = theme.outline_variant
                
            overlay_hover = theme.with_opacity(0.08, color) if hasattr(theme, 'with_opacity') else None
            overlay_pressed = theme.with_opacity(0.12, color) if hasattr(theme, 'with_opacity') else None
        else:
            # Default colors
            default_colors = {
                "primary": "#2196F3",
                "secondary": "#757575",
                "error": "#F44336"
            }
            color = default_colors.get(self._variant, default_colors["primary"])
            border_color = color
            hover_border = color
            disabled_color = "#9E9E9E"
            disabled_border = "#E0E0E0"
            overlay_hover = None
            overlay_pressed = None
        
        # Build style
        style = ft.ButtonStyle(
            color={
                ft.ControlState.DEFAULT: color,
                ft.ControlState.HOVERED: color,
                ft.ControlState.PRESSED: color,
                ft.ControlState.DISABLED: disabled_color,
            },
            side={
                ft.ControlState.DEFAULT: ft.BorderSide(size_config["border_width"], border_color),
                ft.ControlState.HOVERED: ft.BorderSide(size_config["border_width"] + 1, hover_border),
                ft.ControlState.PRESSED: ft.BorderSide(size_config["border_width"] + 1, hover_border),
                ft.ControlState.DISABLED: ft.BorderSide(size_config["border_width"], disabled_border),
            },
            padding={
                ft.ControlState.DEFAULT: size_config["padding"],
            },
            text_style={
                ft.ControlState.DEFAULT: ft.TextStyle(size=size_config["text_size"]),
            }
        )
        
        # Add overlay colors if available
        if overlay_hover and overlay_pressed:
            style.overlay_color = {
                ft.ControlState.HOVERED: overlay_hover,
                ft.ControlState.PRESSED: overlay_pressed,
            }
        
        # Merge with custom style if provided
        if self._custom_style:
            for attr in ['color', 'side', 'overlay_color', 'padding', 'text_style', 'shape']:
                if hasattr(self._custom_style, attr) and getattr(self._custom_style, attr) is not None:
                    setattr(style, attr, getattr(self._custom_style, attr))
        
        return style
    
    def update_variant(self, variant: str):
        """Update button variant and refresh styling.
        
        Args:
            variant: New variant ('primary', 'secondary', 'error')
        """
        self._variant = variant
        if hasattr(self, 'page'):
            theme = get_theme_colors(self.page)
            self.style = self._create_outlined_style(theme)
            self.update()


class OutlinedPrimaryButton(ThemedOutlinedButton):
    """Primary outlined button for less prominent primary actions."""
    
    def __init__(self, text: Optional[str] = None, **kwargs):
        kwargs['variant'] = 'primary'
        super().__init__(text=text, **kwargs)


class OutlinedSecondaryButton(ThemedOutlinedButton):
    """Secondary outlined button for alternative actions."""
    
    def __init__(self, text: Optional[str] = None, **kwargs):
        kwargs['variant'] = 'secondary'
        super().__init__(text=text, **kwargs)