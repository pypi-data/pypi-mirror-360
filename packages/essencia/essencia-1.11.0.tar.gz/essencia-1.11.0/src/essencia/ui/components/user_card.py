"""User card component."""

import flet as ft
from typing import Optional


class UserCard(ft.Card):
    """User card component for displaying user information."""
    
    def __init__(
        self,
        username: str,
        email: str,
        full_name: Optional[str] = None,
        is_active: bool = True,
        is_admin: bool = False,
        on_click=None
    ):
        """Initialize user card.
        
        Args:
            username: User's username
            email: User's email
            full_name: User's full name
            is_active: Whether user is active
            is_admin: Whether user is admin
            on_click: Click handler
        """
        super().__init__()
        self.username = username
        self.email = email
        self.full_name = full_name
        self.is_active = is_active
        self.is_admin = is_admin
        self.on_click = on_click
        self.build()
        
    def build(self):
        """Build the user card UI."""
        # Status indicator
        status_color = ft.Colors.GREEN if self.is_active else ft.Colors.GREY
        status_text = "Active" if self.is_active else "Inactive"
        
        # Role badge
        role_badge = None
        if self.is_admin:
            role_badge = ft.Container(
                content=ft.Text("Admin", size=12, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.ORANGE,
                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                border_radius=12
            )
            
        # Build content
        self.content = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.CircleAvatar(
                                content=ft.Text(
                                    self.username[0].upper(),
                                    size=20,
                                    weight=ft.FontWeight.BOLD
                                ),
                                bgcolor=ft.Colors.BLUE_700,
                                color=ft.Colors.WHITE
                            ),
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(
                                                self.full_name or self.username,
                                                weight=ft.FontWeight.BOLD,
                                                size=16
                                            ),
                                            role_badge
                                        ] if role_badge else [
                                            ft.Text(
                                                self.full_name or self.username,
                                                weight=ft.FontWeight.BOLD,
                                                size=16
                                            )
                                        ],
                                        spacing=10
                                    ),
                                    ft.Text(
                                        self.email,
                                        size=14,
                                        color=ft.Colors.GREY_700
                                    )
                                ],
                                spacing=2
                            )
                        ],
                        spacing=15
                    ),
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.CIRCLE,
                                size=12,
                                color=status_color
                            ),
                            ft.Text(
                                status_text,
                                size=14,
                                color=ft.Colors.GREY_700
                            )
                        ],
                        spacing=5
                    )
                ],
                spacing=10
            ),
            padding=20,
            on_click=self.on_click
        )
        
        # Card properties
        self.elevation = 2
        if self.on_click:
            self.elevation_on_hover = 8