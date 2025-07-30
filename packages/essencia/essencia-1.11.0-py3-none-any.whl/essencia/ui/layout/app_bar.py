"""
Customizable app bar component for Flet applications.
"""

from typing import Optional, List, Union
import flet as ft


class AppBar(ft.CupertinoAppBar):
    """A customizable app bar component that follows application styling guidelines.
    
    Provides a consistent header with configurable title, leading/trailing controls,
    and theme integration.
    
    Example:
        ```python
        from essencia.ui import AppBar, ThemeToggle
        
        app_bar = AppBar(
            title="My Application",
            trailing_controls=[ThemeToggle()],
            on_back=lambda e: page.go("/")
        )
        ```
    
    Args:
        title (str): The title text to display
        leading (Optional[ft.Control]): Control to show on the left (defaults to back button if on_back provided)
        trailing_controls (List[ft.Control]): List of controls to show on the right
        on_back (Optional[callable]): Callback for back navigation
        bgcolor (Optional[str]): Background color (uses theme surface by default)
        **kwargs: Additional arguments passed to CupertinoAppBar
    """
    def __init__(
        self,
        title: str = "Application",
        leading: Optional[ft.Control] = None,
        trailing_controls: Optional[List[ft.Control]] = None,
        on_back: Optional[callable] = None,
        bgcolor: Optional[str] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        # Set title with proper styling
        self.middle = ft.Text(
            title,
            size=18,
            weight=ft.FontWeight.W_500
        )
        
        # Configure leading control
        if leading:
            self.leading = leading
        elif on_back:
            self.leading = ft.IconButton(
                icon=ft.Icons.ARROW_BACK_IOS,
                on_click=on_back
            )
        
        # Configure trailing controls
        if trailing_controls:
            if len(trailing_controls) == 1:
                self.trailing = trailing_controls[0]
            else:
                self.trailing = ft.Row(
                    controls=trailing_controls,
                    spacing=5
                )
        
        # Set background color
        if bgcolor:
            self.bgcolor = bgcolor
            
        # Enable smooth transitions
        self.transition_between_routes = True
        
    def set_title(self, title: str):
        """Update the app bar title.
        
        Args:
            title: New title text
        """
        if hasattr(self.middle, 'value'):
            self.middle.value = title
        else:
            self.middle = ft.Text(title, size=18, weight=ft.FontWeight.W_500)
            
    def add_trailing_control(self, control: ft.Control):
        """Add a control to the trailing section.
        
        Args:
            control: Control to add
        """
        if not self.trailing:
            self.trailing = control
        elif isinstance(self.trailing, ft.Row):
            self.trailing.controls.append(control)
        else:
            # Convert single control to row
            existing = self.trailing
            self.trailing = ft.Row(
                controls=[existing, control],
                spacing=5
            )
            
    def remove_trailing_control(self, control: ft.Control):
        """Remove a control from the trailing section.
        
        Args:
            control: Control to remove
        """
        if isinstance(self.trailing, ft.Row):
            self.trailing.controls.remove(control)
            if len(self.trailing.controls) == 1:
                self.trailing = self.trailing.controls[0]
            elif len(self.trailing.controls) == 0:
                self.trailing = None
        elif self.trailing == control:
            self.trailing = None