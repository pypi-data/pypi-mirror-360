"""
Theme interface for button components.
"""

from typing import Optional, Dict, Any, Protocol
import flet as ft


class ThemeColors(Protocol):
    """Protocol for theme color access."""
    
    # Primary colors
    primary: str
    on_primary: str
    primary_container: str
    on_primary_container: str
    
    # Secondary colors
    secondary: str
    on_secondary: str
    secondary_container: str
    on_secondary_container: str
    
    # Error colors
    error: str
    on_error: str
    error_container: str
    on_error_container: str
    
    # Surface colors
    surface: str
    on_surface: str
    surface_variant: str
    on_surface_variant: str
    
    # Other semantic colors
    outline: str
    outline_variant: str
    
    def get_color(self, name: str) -> str:
        """Get a color by name."""
        ...
    
    def with_opacity(self, opacity: float, color: str) -> str:
        """Get a color with opacity."""
        ...


def get_theme_colors(page: Optional[ft.Page] = None) -> Optional[ThemeColors]:
    """Get theme colors from page or return None."""
    if not page:
        return None
        
    # Check if page has a theme_colors attribute (custom theme system)
    if hasattr(page, 'theme_colors'):
        return page.theme_colors
        
    # Try to get from page.data
    if hasattr(page, 'data') and isinstance(page.data, dict):
        return page.data.get('theme_colors')
        
    return None


def get_button_style(
    variant: str = "primary",
    size: str = "medium",
    theme: Optional[ThemeColors] = None,
    custom_style: Optional[ft.ButtonStyle] = None
) -> ft.ButtonStyle:
    """Generate button style based on variant and theme.
    
    Args:
        variant: Button variant ('primary', 'secondary', 'error', 'success', 'warning', 'info')
        size: Button size ('small', 'medium', 'large')
        theme: Theme colors object
        custom_style: Custom style to merge
        
    Returns:
        ButtonStyle configured for the variant
    """
    # Default colors if no theme
    default_colors = {
        "primary": ("#2196F3", "#FFFFFF"),  # blue/white
        "secondary": ("#757575", "#FFFFFF"),  # grey/white
        "error": ("#F44336", "#FFFFFF"),  # red/white
        "success": ("#4CAF50", "#FFFFFF"),  # green/white
        "warning": ("#FF9800", "#FFFFFF"),  # orange/white
        "info": ("#03A9F4", "#FFFFFF"),  # light blue/white
    }
    
    # Size configurations
    sizes = {
        "small": {"padding": 8, "text_size": 12},
        "medium": {"padding": 12, "text_size": 14},
        "large": {"padding": 16, "text_size": 16},
    }
    
    size_config = sizes.get(size, sizes["medium"])
    
    # Get colors based on variant
    if theme:
        if variant == "primary":
            bg_color = theme.primary
            text_color = theme.on_primary
            hover_bg = theme.primary
            pressed_bg = theme.primary_container
        elif variant == "secondary":
            bg_color = theme.secondary
            text_color = theme.on_secondary
            hover_bg = theme.secondary
            pressed_bg = theme.secondary_container
        elif variant == "error":
            bg_color = theme.error
            text_color = theme.on_error
            hover_bg = theme.error
            pressed_bg = theme.error_container
        elif variant in ["success", "warning", "info"]:
            # Use semantic colors if available, otherwise fall back to defaults
            bg_color, text_color = default_colors.get(variant, default_colors["primary"])
            hover_bg = bg_color
            pressed_bg = bg_color
        else:
            # Default to primary
            bg_color = theme.primary
            text_color = theme.on_primary
            hover_bg = theme.primary
            pressed_bg = theme.primary_container
            
        disabled_bg = theme.surface_variant
        disabled_text = theme.on_surface_variant
        overlay_color = theme.with_opacity(0.08, text_color) if hasattr(theme, 'with_opacity') else None
        overlay_pressed = theme.with_opacity(0.12, text_color) if hasattr(theme, 'with_opacity') else None
    else:
        # Use default colors
        bg_color, text_color = default_colors.get(variant, default_colors["primary"])
        hover_bg = bg_color
        pressed_bg = bg_color
        disabled_bg = "#E0E0E0"
        disabled_text = "#9E9E9E"
        overlay_color = None
        overlay_pressed = None
    
    # Build button style
    style = ft.ButtonStyle(
        color={
            ft.ControlState.DEFAULT: text_color,
            ft.ControlState.HOVERED: text_color,
            ft.ControlState.PRESSED: text_color,
            ft.ControlState.DISABLED: disabled_text,
        },
        bgcolor={
            ft.ControlState.DEFAULT: bg_color,
            ft.ControlState.HOVERED: hover_bg,
            ft.ControlState.PRESSED: pressed_bg,
            ft.ControlState.DISABLED: disabled_bg,
        },
        padding={
            ft.ControlState.DEFAULT: size_config["padding"],
        },
        text_style={
            ft.ControlState.DEFAULT: ft.TextStyle(size=size_config["text_size"]),
        }
    )
    
    # Add overlay colors if available
    if overlay_color and overlay_pressed:
        style.overlay_color = {
            ft.ControlState.HOVERED: overlay_color,
            ft.ControlState.PRESSED: overlay_pressed,
        }
    
    # Merge with custom style if provided
    if custom_style:
        # Merge custom style properties
        for attr in ['color', 'bgcolor', 'overlay_color', 'padding', 'text_style', 'shape', 'side', 'elevation']:
            if hasattr(custom_style, attr) and getattr(custom_style, attr) is not None:
                setattr(style, attr, getattr(custom_style, attr))
    
    return style