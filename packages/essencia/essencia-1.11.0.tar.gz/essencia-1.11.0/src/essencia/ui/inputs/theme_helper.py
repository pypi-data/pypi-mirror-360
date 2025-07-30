"""
Theme helper utilities for input components.
"""

from typing import Optional, Dict, Any, Tuple
import flet as ft


def get_theme_mode(page: Optional[ft.Page] = None) -> str:
    """Determine if the current theme is light or dark mode.
    
    Args:
        page: Flet page to check theme mode
        
    Returns:
        'light' or 'dark' based on theme mode
    """
    if not page:
        return 'light'
        
    theme_mode = getattr(page, 'theme_mode', ft.ThemeMode.SYSTEM)
    
    if theme_mode == ft.ThemeMode.LIGHT:
        return 'light'
    elif theme_mode == ft.ThemeMode.DARK:
        return 'dark'
    else:
        # System theme - check if we have a way to detect system preference
        # Default to light if unknown
        return 'light'


def get_input_colors(page: Optional[ft.Page] = None) -> Dict[str, Any]:
    """Get appropriate colors for input controls based on theme.
    
    Args:
        page: Flet page to get theme from
        
    Returns:
        Dictionary of color configurations
    """
    is_light = get_theme_mode(page) == 'light'
    
    if is_light:
        return {
            'fill_color': {
                ft.ControlState.DEFAULT: ft.Colors.SURFACE,
                ft.ControlState.HOVERED: ft.Colors.SURFACE_VARIANT,
                ft.ControlState.FOCUSED: ft.Colors.SURFACE,
            },
            'text_color': ft.Colors.BLACK,
            'label_color': ft.Colors.ON_SURFACE_VARIANT,
            'hint_color': ft.Colors.ON_SURFACE_VARIANT,
            'border_color': ft.Colors.OUTLINE,
            'focused_border_color': ft.Colors.PRIMARY,
            'cursor_color': ft.Colors.PRIMARY,
            'selection_color': ft.Colors.with_opacity(0.3, ft.Colors.PRIMARY),
            'error_color': ft.Colors.ERROR,
            'icon_color': ft.Colors.ON_SURFACE_VARIANT,
        }
    else:
        # Dark mode colors
        return {
            'fill_color': {
                ft.ControlState.DEFAULT: ft.Colors.GREY_800,
                ft.ControlState.HOVERED: ft.Colors.GREY_700,
                ft.ControlState.FOCUSED: ft.Colors.GREY_800,
            },
            'text_color': ft.Colors.WHITE,
            'label_color': ft.Colors.WHITE,
            'hint_color': ft.Colors.GREY_400,
            'border_color': ft.Colors.GREY_600,
            'focused_border_color': ft.Colors.ORANGE_400,
            'cursor_color': ft.Colors.ORANGE_400,
            'selection_color': ft.Colors.with_opacity(0.3, ft.Colors.ORANGE_400),
            'error_color': ft.Colors.RED_400,
            'icon_color': ft.Colors.WHITE,
        }


def apply_input_theme(control: ft.Control, page: Optional[ft.Page] = None, **overrides):
    """Apply theme-aware styling to an input control.
    
    Args:
        control: The input control to style
        page: Flet page for theme detection
        **overrides: Override specific style properties
    """
    colors = get_input_colors(page)
    
    # Apply common properties
    if hasattr(control, 'filled') and 'filled' not in overrides:
        control.filled = True
        
    if hasattr(control, 'fill_color') and 'fill_color' not in overrides:
        control.fill_color = colors['fill_color']
        
    if hasattr(control, 'color') and 'color' not in overrides:
        control.color = colors['text_color']
        
    if hasattr(control, 'label_style') and 'label_style' not in overrides:
        control.label_style = ft.TextStyle(
            color=colors['label_color'],
            size=14
        )
        
    if hasattr(control, 'hint_style') and 'hint_style' not in overrides:
        control.hint_style = ft.TextStyle(
            color=colors['hint_color'],
            size=14
        )
        
    if hasattr(control, 'border_color') and 'border_color' not in overrides:
        control.border_color = colors['border_color']
        
    if hasattr(control, 'focused_border_color') and 'focused_border_color' not in overrides:
        control.focused_border_color = colors['focused_border_color']
        
    if hasattr(control, 'border_width') and 'border_width' not in overrides:
        control.border_width = 1
        
    if hasattr(control, 'focused_border_width') and 'focused_border_width' not in overrides:
        control.focused_border_width = 2
        
    if hasattr(control, 'cursor_color') and 'cursor_color' not in overrides:
        control.cursor_color = colors['cursor_color']
        
    if hasattr(control, 'selection_color') and 'selection_color' not in overrides:
        control.selection_color = colors['selection_color']
        
    if hasattr(control, 'error_style') and 'error_style' not in overrides:
        control.error_style = ft.TextStyle(
            color=colors['error_color'],
            size=12
        )
        
    # For dropdowns
    if hasattr(control, 'text_style') and 'text_style' not in overrides:
        control.text_style = ft.TextStyle(color=colors['text_color'])
        
    if hasattr(control, 'icon_enabled_color') and 'icon_enabled_color' not in overrides:
        control.icon_enabled_color = colors['icon_color']
    
    # Apply any overrides
    for key, value in overrides.items():
        if hasattr(control, key):
            setattr(control, key, value)