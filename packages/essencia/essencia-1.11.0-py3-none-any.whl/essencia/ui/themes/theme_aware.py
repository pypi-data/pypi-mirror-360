"""
Theme-aware base components for consistent theming across applications.
"""

import flet as ft
from typing import Optional, Any, Protocol


class ThemeInterface(Protocol):
    """Protocol defining the interface for theme objects."""
    
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
    
    # Background colors
    background: str
    on_background: str
    
    # Surface colors
    surface: str
    on_surface: str
    surface_variant: str
    on_surface_variant: str
    
    # Additional colors
    outline: str
    outline_variant: str
    divider: str
    
    # Semantic colors (optional)
    success: Optional[str]
    warning: Optional[str]
    info: Optional[str]
    
    def with_opacity(self, opacity: float, color: Optional[str]) -> str:
        """Apply opacity to a color."""
        ...


def get_theme_from_page(page: Optional[ft.Page]) -> Optional[ThemeInterface]:
    """Get theme object from page if available.
    
    Checks for theme in:
    1. page.theme_object (custom property)
    2. page.data['theme'] 
    3. Returns None if no theme found
    """
    if not page:
        return None
        
    # Check for custom theme object
    if hasattr(page, 'theme_object'):
        return page.theme_object
        
    # Check in page data
    if hasattr(page, 'data') and isinstance(page.data, dict):
        return page.data.get('theme')
        
    return None


class ThemedComponent:
    """Mixin class that provides theme-aware properties to components.
    
    This mixin allows components to access theme colors dynamically,
    either from a provided theme object or from the page context.
    
    Example:
        ```python
        class MyComponent(ft.Container, ThemedComponent):
            def __init__(self, **kwargs):
                ThemedComponent.__init__(self)
                ft.Container.__init__(self, **kwargs)
                
            def did_mount(self):
                # Apply theme colors after mounting
                self.bgcolor = self.surface_color
                self.update()
        ```
    """
    
    def __init__(self, theme: Optional[ThemeInterface] = None):
        self._theme = theme
        self._page_ref = None
    
    @property
    def theme(self) -> Optional[ThemeInterface]:
        """Get the current theme object."""
        # Return provided theme if available
        if self._theme:
            return self._theme
            
        # Try to get from page
        if hasattr(self, 'page'):
            return get_theme_from_page(self.page)
            
        return None
    
    @property
    def primary_color(self) -> str:
        return self.theme.primary if self.theme else ft.Colors.BLUE
    
    @property
    def secondary_color(self) -> str:
        return self.theme.secondary if self.theme else ft.Colors.TEAL
    
    @property
    def background_color(self) -> str:
        return self.theme.background if self.theme else ft.Colors.BACKGROUND
    
    @property
    def surface_color(self) -> str:
        return self.theme.surface if self.theme else ft.Colors.SURFACE
    
    @property
    def surface_variant_color(self) -> str:
        return self.theme.surface_variant if self.theme else ft.Colors.SURFACE_VARIANT
    
    @property
    def error_color(self) -> str:
        return self.theme.error if self.theme else ft.Colors.ERROR
        
    @property
    def success_color(self) -> str:
        if self.theme and hasattr(self.theme, 'success'):
            return self.theme.success
        return ft.Colors.GREEN
        
    @property
    def warning_color(self) -> str:
        if self.theme and hasattr(self.theme, 'warning'):
            return self.theme.warning
        return ft.Colors.ORANGE
    
    @property
    def on_surface_color(self) -> str:
        return self.theme.on_surface if self.theme else ft.Colors.ON_SURFACE
    
    @property
    def on_background_color(self) -> str:
        return self.theme.on_background if self.theme else ft.Colors.ON_BACKGROUND
    
    @property
    def on_surface_variant_color(self) -> str:
        return self.theme.on_surface_variant if self.theme else ft.Colors.ON_SURFACE_VARIANT
    
    @property
    def divider_color(self) -> str:
        if self.theme and hasattr(self.theme, 'divider'):
            return self.theme.divider
        return ft.Colors.OUTLINE_VARIANT
    
    @property
    def outline_color(self) -> str:
        return self.theme.outline if self.theme else ft.Colors.OUTLINE
    
    def with_opacity(self, opacity: float, color: Optional[str] = None) -> str:
        """Apply opacity to a color."""
        if self.theme and hasattr(self.theme, 'with_opacity'):
            return self.theme.with_opacity(opacity, color)
        
        # Fallback implementation
        color = color or self.primary_color
        return ft.Colors.with_opacity(opacity, color)


class ThemedContainer(ft.Container, ThemedComponent):
    """Theme-aware Container that automatically applies theme colors.
    
    By default uses surface color as background unless overridden.
    
    Example:
        ```python
        container = ThemedContainer(
            content=ft.Text("Hello"),
            padding=20,
            border_radius=10
        )
        ```
    """
    
    def __init__(self, theme: Optional[ThemeInterface] = None, **kwargs):
        ThemedComponent.__init__(self, theme)
        
        # Store whether to use theme bgcolor
        self._use_theme_bgcolor = kwargs.pop('use_theme_bgcolor', True)
        
        # Don't apply theme in __init__ - wait for did_mount
        super().__init__(**kwargs)
        
    def did_mount(self):
        """Apply theme after mounting to page."""
        super().did_mount()
        
        # Apply theme bgcolor if not explicitly set and enabled
        if self._use_theme_bgcolor and not self.bgcolor:
            self.bgcolor = self.surface_color
            self.update()


class ThemedCard(ft.Card, ThemedComponent):
    """Theme-aware Card that automatically applies theme colors."""
    
    def __init__(self, theme: Optional[ThemeInterface] = None, **kwargs):
        ThemedComponent.__init__(self, theme)
        super().__init__(**kwargs)
        
    def did_mount(self):
        """Apply theme after mounting to page."""
        super().did_mount()
        
        # Apply theme color if not set
        if not self.color:
            self.color = self.surface_color
            self.update()


class ThemedText(ft.Text, ThemedComponent):
    """Theme-aware Text that automatically applies theme colors."""
    
    def __init__(self, value: str = "", theme: Optional[ThemeInterface] = None, **kwargs):
        ThemedComponent.__init__(self, theme)
        
        # Store whether to use theme color
        self._use_theme_color = kwargs.pop('use_theme_color', True)
        
        super().__init__(value, **kwargs)
        
    def did_mount(self):
        """Apply theme after mounting to page."""
        super().did_mount()
        
        # Apply theme color if not set and enabled
        if self._use_theme_color and not self.color:
            self.color = self.on_surface_color
            self.update()


class ThemedDivider(ft.Divider, ThemedComponent):
    """Theme-aware Divider that automatically applies theme colors."""
    
    def __init__(self, theme: Optional[ThemeInterface] = None, **kwargs):
        ThemedComponent.__init__(self, theme)
        super().__init__(**kwargs)
        
    def did_mount(self):
        """Apply theme after mounting to page."""
        super().did_mount()
        
        # Apply theme color if not set
        if not self.color:
            self.color = self.divider_color
            self.update()


def apply_theme_to_control(
    control: ft.Control,
    theme: Optional[ThemeInterface] = None,
    theme_property: Optional[str] = None
) -> ft.Control:
    """Apply theme colors to an existing control.
    
    Args:
        control: The Flet control to theme
        theme: Theme object to use (will try to get from page if not provided)
        theme_property: The theme property to use (e.g., 'primary', 'surface')
        
    Returns:
        The control with theme applied
        
    Example:
        ```python
        button = ft.ElevatedButton("Click Me")
        apply_theme_to_control(button, theme_property='primary')
        ```
    """
    # Get theme if not provided
    if not theme and hasattr(control, 'page'):
        theme = get_theme_from_page(control.page)
        
    if not theme:
        return control
        
    # Determine color to apply
    if theme_property:
        color = getattr(theme, theme_property, None)
        if not color:
            color = theme.primary
    else:
        color = theme.on_surface
    
    # Apply color based on control type
    if hasattr(control, 'color') and not control.color:
        control.color = color
    elif hasattr(control, 'bgcolor') and not control.bgcolor:
        if theme_property == 'surface':
            control.bgcolor = theme.surface
        else:
            control.bgcolor = color
    elif hasattr(control, 'icon_color') and not control.icon_color:
        control.icon_color = color
    elif hasattr(control, 'fill_color') and not control.fill_color:
        control.fill_color = color
    
    return control