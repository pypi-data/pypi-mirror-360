"""
Text button components with theme integration.
"""

from typing import Optional, Callable, Any
import flet as ft
from .theme_interface import get_theme_colors


class ThemedTextButton(ft.TextButton):
    """Text button with automatic theme-aware styling.
    
    Provides a minimal button style suitable for inline actions,
    navigation links, and less prominent interactions.
    
    Example:
        ```python
        button = ThemedTextButton(
            text="Learn More",
            on_click=lambda e: page.go("/help")
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
        
        # Apply text button style
        self.style = self._create_text_style(theme)
        
        if hasattr(self, 'update'):
            self.update()
    
    def _create_text_style(self, theme) -> ft.ButtonStyle:
        """Create text button style based on theme and variant."""
        # Size configurations
        sizes = {
            "small": {"padding": 4, "text_size": 12},
            "medium": {"padding": 8, "text_size": 14},
            "large": {"padding": 12, "text_size": 16},
        }
        
        size_config = sizes.get(self._size, sizes["medium"])
        
        if theme:
            # Get colors based on variant
            if self._variant == "primary":
                color = theme.primary
                disabled_color = theme.on_surface_variant
            elif self._variant == "secondary":
                color = theme.secondary
                disabled_color = theme.on_surface_variant
            elif self._variant == "error":
                color = theme.error
                disabled_color = theme.on_surface_variant
            else:
                # Default text color
                color = theme.on_surface
                disabled_color = theme.on_surface_variant
                
            overlay_hover = theme.with_opacity(0.08, color) if hasattr(theme, 'with_opacity') else None
            overlay_pressed = theme.with_opacity(0.12, color) if hasattr(theme, 'with_opacity') else None
        else:
            # Default colors
            default_colors = {
                "primary": "#2196F3",
                "secondary": "#757575",
                "error": "#F44336"
            }
            color = default_colors.get(self._variant, "#000000")
            disabled_color = "#9E9E9E"
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
            for attr in ['color', 'overlay_color', 'padding', 'text_style']:
                if hasattr(self._custom_style, attr) and getattr(self._custom_style, attr) is not None:
                    setattr(style, attr, getattr(self._custom_style, attr))
        
        return style


class LinkButton(ThemedTextButton):
    """Specialized text button styled as a hyperlink.
    
    Features underline on hover and appropriate cursor styling.
    
    Example:
        ```python
        link = LinkButton(
            text="Privacy Policy",
            url="https://example.com/privacy",
            open_in_new_tab=True
        )
        ```
    """
    
    def __init__(
        self,
        text: Optional[str] = None,
        url: Optional[str] = None,
        open_in_new_tab: bool = True,
        **kwargs
    ):
        self._url = url
        self._open_in_new_tab = open_in_new_tab
        
        # Set up click handler if URL provided
        if url and 'on_click' not in kwargs:
            kwargs['on_click'] = self._handle_link_click
        
        # Default to primary variant
        kwargs.setdefault('variant', 'primary')
        
        super().__init__(text=text, **kwargs)
    
    def _handle_link_click(self, e):
        """Handle link click to open URL."""
        if self._url and hasattr(self, 'page') and self.page:
            self.page.launch_url(
                self._url,
                web_window_name="_blank" if self._open_in_new_tab else "_self"
            )
    
    def _create_text_style(self, theme) -> ft.ButtonStyle:
        """Create link-specific text style with underline on hover."""
        style = super()._create_text_style(theme)
        
        # Add underline decoration on hover
        if not hasattr(style, 'text_style') or style.text_style is None:
            style.text_style = {}
            
        # Ensure we have entries for all states
        for state in [ft.ControlState.DEFAULT, ft.ControlState.HOVERED, ft.ControlState.PRESSED]:
            if state not in style.text_style:
                style.text_style[state] = ft.TextStyle()
        
        # Add underline on hover
        style.text_style[ft.ControlState.HOVERED].decoration = ft.TextDecoration.UNDERLINE
        
        return style