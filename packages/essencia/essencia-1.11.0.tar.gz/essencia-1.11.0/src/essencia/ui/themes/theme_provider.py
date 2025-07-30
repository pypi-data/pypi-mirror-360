"""
Theme provider and utilities for managing application themes.
"""

import flet as ft
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class DefaultTheme:
    """Default theme implementation with all required colors.
    
    This provides a complete theme that can be customized by
    passing different color values.
    
    Example:
        ```python
        theme = DefaultTheme(
            primary="#1976D2",
            secondary="#009688",
            error="#D32F2F"
        )
        ```
    """
    # Primary colors
    primary: str = "#2196F3"
    on_primary: str = "#FFFFFF" 
    primary_container: str = "#BBDEFB"
    on_primary_container: str = "#0D47A1"
    
    # Secondary colors
    secondary: str = "#03DAC6"
    on_secondary: str = "#000000"
    secondary_container: str = "#A7FFEB" 
    on_secondary_container: str = "#00BFA5"
    
    # Error colors
    error: str = "#F44336"
    on_error: str = "#FFFFFF"
    error_container: str = "#FFCDD2"
    on_error_container: str = "#B71C1C"
    
    # Background colors
    background: str = "#FFFFFF"
    on_background: str = "#000000"
    
    # Surface colors
    surface: str = "#FFFFFF"
    on_surface: str = "#000000"
    surface_variant: str = "#F5F5F5"
    on_surface_variant: str = "#757575"
    
    # Additional colors
    outline: str = "#BDBDBD"
    outline_variant: str = "#E0E0E0"
    divider: str = "#E0E0E0"
    
    # Semantic colors
    success: str = "#4CAF50"
    warning: str = "#FF9800"
    info: str = "#2196F3"
    
    # Opacity cache
    _opacity_cache: Dict[tuple, str] = field(default_factory=dict)
    
    def with_opacity(self, opacity: float, color: Optional[str] = None) -> str:
        """Apply opacity to a color with caching."""
        color = color or self.primary
        cache_key = (opacity, color)
        
        if cache_key in self._opacity_cache:
            return self._opacity_cache[cache_key]
            
        result = ft.Colors.with_opacity(opacity, color)
        self._opacity_cache[cache_key] = result
        return result


class DarkTheme(DefaultTheme):
    """Dark theme variant with appropriate colors for dark mode."""
    
    def __init__(self):
        super().__init__(
            # Primary colors
            primary="#90CAF9",
            on_primary="#0D47A1",
            primary_container="#1565C0",
            on_primary_container="#E3F2FD",
            
            # Secondary colors  
            secondary="#80CBC4",
            on_secondary="#00695C",
            secondary_container="#00897B",
            on_secondary_container="#E0F2F1",
            
            # Error colors
            error="#EF9A9A",
            on_error="#FFEBEE",
            error_container="#C62828",
            on_error_container="#FFCDD2",
            
            # Background colors
            background="#121212",
            on_background="#FFFFFF",
            
            # Surface colors
            surface="#1E1E1E",
            on_surface="#FFFFFF",
            surface_variant="#2C2C2C",
            on_surface_variant="#BDBDBD",
            
            # Additional colors
            outline="#757575",
            outline_variant="#424242",
            divider="#424242",
            
            # Semantic colors
            success="#81C784",
            warning="#FFB74D",
            info="#64B5F6"
        )


class ThemeProvider:
    """Manages theme state and provides theme switching functionality.
    
    Example:
        ```python
        provider = ThemeProvider()
        
        # Apply theme to page
        provider.apply_to_page(page)
        
        # Switch themes
        provider.set_theme_mode(ft.ThemeMode.DARK)
        
        # Get current theme object
        theme = provider.current_theme
        ```
    """
    
    def __init__(
        self,
        light_theme: Optional[DefaultTheme] = None,
        dark_theme: Optional[DefaultTheme] = None,
        initial_mode: ft.ThemeMode = ft.ThemeMode.LIGHT
    ):
        self.light_theme = light_theme or DefaultTheme()
        self.dark_theme = dark_theme or DarkTheme()
        self._theme_mode = initial_mode
        self._page_ref: Optional[ft.Page] = None
        
    @property
    def current_theme(self) -> DefaultTheme:
        """Get the current theme based on theme mode."""
        if self._theme_mode == ft.ThemeMode.DARK:
            return self.dark_theme
        else:
            return self.light_theme
            
    @property
    def theme_mode(self) -> ft.ThemeMode:
        """Get current theme mode."""
        return self._theme_mode
        
    def set_theme_mode(self, mode: ft.ThemeMode):
        """Set theme mode and update page if attached."""
        self._theme_mode = mode
        
        if self._page_ref:
            self._page_ref.theme_mode = mode
            # Update theme object reference
            if hasattr(self._page_ref, 'data') and isinstance(self._page_ref.data, dict):
                self._page_ref.data['theme'] = self.current_theme
            self._page_ref.update()
            
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        new_mode = (
            ft.ThemeMode.LIGHT 
            if self._theme_mode == ft.ThemeMode.DARK 
            else ft.ThemeMode.DARK
        )
        self.set_theme_mode(new_mode)
        
    def apply_to_page(self, page: ft.Page):
        """Apply theme provider to a Flet page.
        
        This sets up the page with the current theme and stores
        the theme object for access by components.
        """
        self._page_ref = page
        
        # Set theme mode
        page.theme_mode = self._theme_mode
        
        # Create Flet theme from our theme
        page.theme = self._create_flet_theme(self.light_theme)
        page.dark_theme = self._create_flet_theme(self.dark_theme)
        
        # Store theme object for component access
        if not hasattr(page, 'data'):
            page.data = {}
        elif not isinstance(page.data, dict):
            page.data = {'_original': page.data}
            
        page.data['theme'] = self.current_theme
        page.data['theme_provider'] = self
        
        # Add custom property for easier access
        page.theme_object = self.current_theme
        
    def _create_flet_theme(self, theme: DefaultTheme) -> ft.Theme:
        """Create Flet Theme object from our theme."""
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=theme.primary,
                on_primary=theme.on_primary,
                primary_container=theme.primary_container,
                on_primary_container=theme.on_primary_container,
                secondary=theme.secondary,
                on_secondary=theme.on_secondary,
                secondary_container=theme.secondary_container,
                on_secondary_container=theme.on_secondary_container,
                error=theme.error,
                on_error=theme.on_error,
                error_container=theme.error_container,
                on_error_container=theme.on_error_container,
                background=theme.background,
                on_background=theme.on_background,
                surface=theme.surface,
                on_surface=theme.on_surface,
                surface_variant=theme.surface_variant,
                on_surface_variant=theme.on_surface_variant,
                outline=theme.outline,
                outline_variant=theme.outline_variant,
            ),
            use_material3=True
        )


def create_theme(**kwargs) -> DefaultTheme:
    """Create a theme with custom colors.
    
    Args:
        **kwargs: Color values to override defaults
        
    Returns:
        DefaultTheme with custom colors
        
    Example:
        ```python
        theme = create_theme(
            primary="#6200EE",
            secondary="#03DAC6",
            error="#B00020"
        )
        ```
    """
    return DefaultTheme(**kwargs)


def apply_theme_to_page(
    page: ft.Page,
    light_theme: Optional[DefaultTheme] = None,
    dark_theme: Optional[DefaultTheme] = None,
    initial_mode: ft.ThemeMode = ft.ThemeMode.LIGHT
) -> ThemeProvider:
    """Convenience function to quickly apply theme to a page.
    
    Args:
        page: Flet page to apply theme to
        light_theme: Custom light theme (uses default if not provided)
        dark_theme: Custom dark theme (uses default if not provided)
        initial_mode: Initial theme mode
        
    Returns:
        ThemeProvider instance managing the page theme
        
    Example:
        ```python
        def main(page: ft.Page):
            provider = apply_theme_to_page(page, initial_mode=ft.ThemeMode.DARK)
            
            # Add theme toggle button
            page.add(
                ft.IconButton(
                    icon=ft.Icons.BRIGHTNESS_6,
                    on_click=lambda _: provider.toggle_theme()
                )
            )
        ```
    """
    provider = ThemeProvider(light_theme, dark_theme, initial_mode)
    provider.apply_to_page(page)
    return provider