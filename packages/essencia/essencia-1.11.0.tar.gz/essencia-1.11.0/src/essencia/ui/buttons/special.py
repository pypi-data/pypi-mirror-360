"""
Special button components for advanced use cases.
"""

from typing import Optional, Callable, Any, List, Union
import asyncio
import flet as ft
from .elevated import ThemedElevatedButton
from .theme_interface import get_theme_colors


class LoadingButton(ThemedElevatedButton):
    """Button that shows loading state during async operations.
    
    Automatically disables and shows progress indicator while
    the async operation is running.
    
    Example:
        ```python
        async def save_data(e):
            await asyncio.sleep(2)  # Simulate API call
            return "Success!"
        
        button = LoadingButton(
            text="Save",
            on_click=save_data,
            loading_text="Saving...",
            on_complete=lambda result: show_message(result)
        )
        ```
    """
    
    def __init__(
        self,
        text: Optional[str] = None,
        loading_text: Optional[str] = None,
        on_click: Optional[Callable] = None,
        on_complete: Optional[Callable[[Any], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        **kwargs
    ):
        self._original_text = text
        self._loading_text = loading_text or "Loading..."
        self._async_handler = on_click
        self._on_complete = on_complete
        self._on_error = on_error
        self._is_loading = False
        
        # Replace on_click with our wrapper
        kwargs['on_click'] = self._handle_click
        
        super().__init__(text=text, **kwargs)
    
    async def _handle_click(self, e):
        """Handle button click with loading state."""
        if self._is_loading or not self._async_handler:
            return
        
        # Start loading
        self._is_loading = True
        self.disabled = True
        self.text = self._loading_text
        
        # Show progress indicator
        if not self.icon:
            self.icon = ft.ProgressRing(width=16, height=16, stroke_width=2)
        
        self.update()
        
        try:
            # Execute async handler
            if asyncio.iscoroutinefunction(self._async_handler):
                result = await self._async_handler(e)
            else:
                result = self._async_handler(e)
            
            # Call completion handler
            if self._on_complete:
                self._on_complete(result)
                
        except Exception as error:
            # Handle error
            if self._on_error:
                self._on_error(error)
            else:
                print(f"LoadingButton error: {error}")
        
        finally:
            # Reset button state
            self._is_loading = False
            self.disabled = False
            self.text = self._original_text
            self.icon = None
            self.update()


class ToggleButton(ft.Container):
    """Toggle button that switches between two states.
    
    Example:
        ```python
        toggle = ToggleButton(
            active_text="Following",
            inactive_text="Follow",
            active_icon=ft.Icons.NOTIFICATIONS_ACTIVE,
            inactive_icon=ft.Icons.NOTIFICATIONS_NONE,
            value=False,
            on_change=lambda value: print(f"Toggled: {value}")
        )
        ```
    """
    
    def __init__(
        self,
        active_text: str = "On",
        inactive_text: str = "Off",
        active_icon: Optional[Union[str, ft.Icons]] = None,
        inactive_icon: Optional[Union[str, ft.Icons]] = None,
        value: bool = False,
        variant: str = "primary",
        on_change: Optional[Callable[[bool], None]] = None,
        **kwargs
    ):
        self._active_text = active_text
        self._inactive_text = inactive_text
        self._active_icon = active_icon
        self._inactive_icon = inactive_icon
        self._value = value
        self._variant = variant
        self._on_change = on_change
        
        # Create button
        self._button = ThemedElevatedButton(
            text=active_text if value else inactive_text,
            icon=active_icon if value else inactive_icon,
            variant=variant if value else "secondary",
            on_click=self._handle_toggle
        )
        
        super().__init__(content=self._button, **kwargs)
    
    def _handle_toggle(self, e):
        """Handle toggle action."""
        self._value = not self._value
        self._update_button_state()
        
        if self._on_change:
            self._on_change(self._value)
    
    def _update_button_state(self):
        """Update button appearance based on state."""
        self._button.text = self._active_text if self._value else self._inactive_text
        self._button.icon = self._active_icon if self._value else self._inactive_icon
        self._button.update_variant(self._variant if self._value else "secondary")
        
        if hasattr(self._button, 'update'):
            self._button.update()
    
    @property
    def value(self) -> bool:
        """Get current toggle state."""
        return self._value
    
    @value.setter
    def value(self, value: bool):
        """Set toggle state."""
        if self._value != value:
            self._value = value
            self._update_button_state()


class SplitButton(ft.Container):
    """Button with dropdown menu for additional actions.
    
    Example:
        ```python
        split = SplitButton(
            text="Save",
            on_click=lambda e: save_file(),
            menu_items=[
                ("Save As...", lambda e: save_as()),
                ("Save Copy", lambda e: save_copy()),
                None,  # Separator
                ("Export", lambda e: export_file()),
            ]
        )
        ```
    """
    
    def __init__(
        self,
        text: str,
        on_click: Callable,
        menu_items: List[Union[tuple, None]],
        variant: str = "primary",
        **kwargs
    ):
        self._main_action = on_click
        self._menu_items = menu_items
        
        # Create main button
        self._main_button = ThemedElevatedButton(
            text=text,
            variant=variant,
            on_click=on_click
        )
        
        # Create dropdown button
        self._dropdown_button = ThemedElevatedButton(
            icon=ft.Icons.ARROW_DROP_DOWN,
            variant=variant,
            on_click=self._show_menu
        )
        
        # Container for both buttons
        content = ft.Row(
            controls=[self._main_button, self._dropdown_button],
            spacing=1
        )
        
        super().__init__(content=content, **kwargs)
    
    def _show_menu(self, e):
        """Show dropdown menu."""
        if not hasattr(self, 'page') or not self.page:
            return
        
        menu_items = []
        for item in self._menu_items:
            if item is None:
                # Separator
                menu_items.append(ft.PopupMenuItem(text="-"))
            else:
                text, handler = item
                menu_items.append(
                    ft.PopupMenuItem(
                        text=text,
                        on_click=handler
                    )
                )
        
        menu = ft.PopupMenuButton(
            items=menu_items,
            visible=True
        )
        
        # Position menu near button
        self.page.overlay.append(menu)
        self.page.update()


class ButtonGroup(ft.Row):
    """Group of related buttons with consistent spacing.
    
    Example:
        ```python
        group = ButtonGroup(
            buttons=[
                PrimaryButton("Save", on_click=save),
                SecondaryButton("Cancel", on_click=cancel),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.END
        )
        ```
    """
    
    def __init__(
        self,
        buttons: List[ft.Control],
        spacing: int = 8,
        alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.START,
        **kwargs
    ):
        super().__init__(
            controls=buttons,
            spacing=spacing,
            alignment=alignment,
            **kwargs
        )


class ActionButton(ThemedElevatedButton):
    """Button optimized for action bars and toolbars.
    
    Features compact sizing and icon-first design.
    
    Example:
        ```python
        action = ActionButton(
            icon=ft.Icons.EDIT,
            text="Edit",
            on_click=edit_handler,
            compact=True
        )
        ```
    """
    
    def __init__(
        self,
        text: Optional[str] = None,
        icon: Optional[Union[str, ft.Icons]] = None,
        compact: bool = True,
        **kwargs
    ):
        # Default to small size for actions
        kwargs.setdefault('size', 'small' if compact else 'medium')
        
        # Ensure icon is provided for icon-first design
        if not icon and not text:
            raise ValueError("ActionButton requires either icon or text")
        
        super().__init__(
            text=text,
            icon=icon,
            **kwargs
        )