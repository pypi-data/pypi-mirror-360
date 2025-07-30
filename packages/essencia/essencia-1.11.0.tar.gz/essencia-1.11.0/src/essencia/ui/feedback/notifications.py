"""
Notification components for user feedback.

Provides toast messages, snackbars, and alerts for
user notifications in Flet applications.
"""

import asyncio
from typing import Optional, Callable, Union
from enum import Enum

import flet as ft

from ..themes import ThemedComponent


class NotificationType(Enum):
    """Notification severity types."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationPosition(Enum):
    """Notification display positions."""
    TOP = "top"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM = "bottom"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"


class Toast(ft.Container, ThemedComponent):
    """
    Toast notification that appears temporarily.
    
    Example:
        ```python
        toast = Toast(
            message="Operation completed successfully!",
            type=NotificationType.SUCCESS,
            duration=3000
        )
        
        # Show toast
        page.overlay.append(toast)
        page.update()
        ```
    """
    
    def __init__(
        self,
        message: str,
        type: NotificationType = NotificationType.INFO,
        duration: int = 3000,  # milliseconds
        action_text: Optional[str] = None,
        on_action: Optional[Callable] = None,
        position: NotificationPosition = NotificationPosition.TOP,
        **kwargs
    ):
        ThemedComponent.__init__(self)
        
        self.message = message
        self.type = type
        self.duration = duration
        self.action_text = action_text
        self.on_action = on_action
        self.position = position
        
        # Placeholder content
        super().__init__(
            content=self._build_content(),
            **kwargs
        )
    
    def _build_content(self) -> ft.Control:
        """Build toast content."""
        # This is a placeholder implementation
        # Full implementation would include styling based on type,
        # animations, and positioning
        return ft.Text(self.message)


class Snackbar(ft.SnackBar):
    """
    Enhanced snackbar with theme support.
    
    Example:
        ```python
        snackbar = Snackbar(
            content="File saved successfully",
            action="Undo",
            on_action=lambda e: undo_save()
        )
        
        page.show_snack_bar(snackbar)
        ```
    """
    
    def __init__(
        self,
        content: Union[str, ft.Control],
        action: Optional[str] = None,
        on_action: Optional[Callable] = None,
        duration: int = 4000,
        **kwargs
    ):
        # Create content
        if isinstance(content, str):
            content = ft.Text(content)
            
        super().__init__(
            content=content,
            action=action,
            on_action=on_action,
            duration=duration,
            **kwargs
        )


class Alert(ft.AlertDialog):
    """
    Enhanced alert dialog with theme support.
    
    Example:
        ```python
        alert = Alert(
            title="Confirm Delete",
            content="Are you sure you want to delete this item?",
            actions=[
                ("Cancel", None),
                ("Delete", lambda: delete_item())
            ]
        )
        
        page.dialog = alert
        alert.open = True
        page.update()
        ```
    """
    
    def __init__(
        self,
        title: str,
        content: Union[str, ft.Control],
        actions: Optional[list] = None,
        type: NotificationType = NotificationType.INFO,
        **kwargs
    ):
        # Create content
        if isinstance(content, str):
            content = ft.Text(content)
            
        # Create action buttons
        action_controls = []
        if actions:
            for action in actions:
                if isinstance(action, tuple):
                    text, handler = action
                    action_controls.append(
                        ft.TextButton(text, on_click=handler)
                    )
                else:
                    action_controls.append(action)
                    
        super().__init__(
            title=ft.Text(title),
            content=content,
            actions=action_controls,
            **kwargs
        )


# Helper functions for showing notifications

def show_toast(
    page: ft.Page,
    message: str,
    type: NotificationType = NotificationType.INFO,
    duration: int = 3000,
    position: NotificationPosition = NotificationPosition.TOP
) -> Toast:
    """
    Show a toast notification.
    
    Example:
        ```python
        show_toast(
            page,
            "Settings saved!",
            type=NotificationType.SUCCESS
        )
        ```
    """
    toast = Toast(
        message=message,
        type=type,
        duration=duration,
        position=position
    )
    
    # Add to overlay
    page.overlay.append(toast)
    page.update()
    
    # Auto-remove after duration
    async def remove_toast():
        await asyncio.sleep(duration / 1000)
        if toast in page.overlay:
            page.overlay.remove(toast)
            page.update()
            
    page.run_task(remove_toast)
    
    return toast


def show_snackbar(
    page: ft.Page,
    message: str,
    action: Optional[str] = None,
    on_action: Optional[Callable] = None,
    duration: int = 4000
) -> Snackbar:
    """
    Show a snackbar notification.
    
    Example:
        ```python
        show_snackbar(
            page,
            "Item deleted",
            action="Undo",
            on_action=lambda e: restore_item()
        )
        ```
    """
    snackbar = Snackbar(
        content=message,
        action=action,
        on_action=on_action,
        duration=duration
    )
    
    page.show_snack_bar(snackbar)
    return snackbar


def show_alert(
    page: ft.Page,
    title: str,
    content: Union[str, ft.Control],
    actions: Optional[list] = None,
    type: NotificationType = NotificationType.INFO
) -> Alert:
    """
    Show an alert dialog.
    
    Example:
        ```python
        show_alert(
            page,
            "Confirm",
            "Are you sure?",
            actions=[
                ("Cancel", lambda e: close_alert()),
                ("Confirm", lambda e: confirm_action())
            ]
        )
        ```
    """
    alert = Alert(
        title=title,
        content=content,
        actions=actions,
        type=type
    )
    
    page.dialog = alert
    alert.open = True
    page.update()
    
    return alert