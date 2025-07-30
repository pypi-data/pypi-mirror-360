"""
Elevated button components with theme integration.
"""

from typing import Optional, Callable, Any
import flet as ft
from .theme_interface import get_theme_colors, get_button_style


class ThemedElevatedButton(ft.ElevatedButton):
    """Base themed elevated button that automatically uses theme colors.
    
    This button automatically adapts to the application's theme when mounted
    to a page. If no theme is available, it uses sensible defaults.
    
    Example:
        ```python
        button = ThemedElevatedButton(
            text="Click Me",
            on_click=lambda e: print("Clicked!"),
            variant="primary",
            size="medium"
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
        # Remove any color/style properties that would override theme
        kwargs.pop('color', None)
        kwargs.pop('bgcolor', None)
        custom_style = kwargs.pop('style', None)
        
        # Store configuration
        self._variant = variant
        self._size = size
        self._custom_style = custom_style
        
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
        
        # Apply button style
        self.style = get_button_style(
            variant=self._variant,
            size=self._size,
            theme=theme,
            custom_style=self._custom_style
        )
        
        if hasattr(self, 'update'):
            self.update()
    
    def update_variant(self, variant: str):
        """Update button variant and refresh styling.
        
        Args:
            variant: New variant ('primary', 'secondary', 'error', etc.)
        """
        self._variant = variant
        if hasattr(self, 'page'):
            theme = get_theme_colors(self.page)
            self.style = get_button_style(
                variant=variant,
                size=self._size,
                theme=theme,
                custom_style=self._custom_style
            )
            self.update()


class PrimaryButton(ThemedElevatedButton):
    """Primary action button with prominent styling.
    
    Used for main actions like 'Save', 'Submit', 'Continue'.
    """
    
    def __init__(self, text: Optional[str] = None, **kwargs):
        kwargs['variant'] = 'primary'
        super().__init__(text=text, **kwargs)


class SecondaryButton(ThemedElevatedButton):
    """Secondary action button with subdued styling.
    
    Used for secondary actions like 'Cancel', 'Back', 'Skip'.
    """
    
    def __init__(self, text: Optional[str] = None, **kwargs):
        kwargs['variant'] = 'secondary'
        super().__init__(text=text, **kwargs)


class ErrorButton(ThemedElevatedButton):
    """Error/danger button for destructive actions.
    
    Used for actions like 'Delete', 'Remove', 'Discard'.
    """
    
    def __init__(self, text: Optional[str] = None, **kwargs):
        kwargs['variant'] = 'error'
        # Add confirmation if not disabled
        if 'on_click' in kwargs and not kwargs.get('confirm', False):
            original_handler = kwargs['on_click']
            kwargs['on_click'] = self._create_confirmation_handler(original_handler)
        super().__init__(text=text, **kwargs)
    
    def _create_confirmation_handler(self, original_handler: Callable):
        """Create a handler that shows confirmation dialog."""
        def handler(e):
            if hasattr(self, 'page') and self.page:
                def close_dialog(confirmed):
                    dialog.open = False
                    self.page.update()
                    if confirmed and original_handler:
                        original_handler(e)
                
                dialog = ft.AlertDialog(
                    title=ft.Text("Confirm Action"),
                    content=ft.Text("Are you sure you want to perform this action?"),
                    actions=[
                        ft.TextButton("Cancel", on_click=lambda _: close_dialog(False)),
                        ft.TextButton("Confirm", on_click=lambda _: close_dialog(True)),
                    ],
                )
                
                self.page.overlay.append(dialog)
                dialog.open = True
                self.page.update()
            else:
                # No page available, call directly
                if original_handler:
                    original_handler(e)
        
        return handler


class SuccessButton(ThemedElevatedButton):
    """Success button for positive actions.
    
    Used for actions like 'Approve', 'Accept', 'Complete'.
    """
    
    def __init__(self, text: Optional[str] = None, **kwargs):
        kwargs['variant'] = 'success'
        super().__init__(text=text, **kwargs)


class WarningButton(ThemedElevatedButton):
    """Warning button for actions requiring caution.
    
    Used for actions like 'Reset', 'Clear', 'Restart'.
    """
    
    def __init__(self, text: Optional[str] = None, **kwargs):
        kwargs['variant'] = 'warning'
        super().__init__(text=text, **kwargs)


class InfoButton(ThemedElevatedButton):
    """Info button for informational actions.
    
    Used for actions like 'Learn More', 'Details', 'Help'.
    """
    
    def __init__(self, text: Optional[str] = None, **kwargs):
        kwargs['variant'] = 'info'
        if not kwargs.get('icon'):
            kwargs['icon'] = ft.Icons.INFO_OUTLINE
        super().__init__(text=text, **kwargs)