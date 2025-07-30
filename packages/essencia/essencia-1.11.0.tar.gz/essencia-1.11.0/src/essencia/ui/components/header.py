"""Header component."""

import flet as ft


class Header(ft.Container):
    """Header component with navigation."""
    
    def __init__(self, page: ft.Page, show_user_menu: bool = False):
        """Initialize header.
        
        Args:
            page: Flet page instance
            show_user_menu: Whether to show user menu
        """
        super().__init__()
        self.page = page
        self.app = page.data.get("app")
        self.show_user_menu = show_user_menu
        self.build()
        
    def build(self):
        """Build the header UI."""
        # Logo/Title
        logo = ft.TextButton(
            "Essencia",
            on_click=lambda _: self.page.go("/"),
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE
                )
            )
        )
        
        # Navigation items
        nav_items = []
        
        if self.show_user_menu and self.app and self.app.current_user:
            # User menu
            user_menu = ft.PopupMenuButton(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.PERSON, color=ft.Colors.WHITE),
                        ft.Text(
                            self.app.current_user.get("username", "User"),
                            color=ft.Colors.WHITE
                        ),
                        ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=ft.Colors.WHITE)
                    ],
                    spacing=5
                ),
                items=[
                    ft.PopupMenuItem(
                        text="Profile",
                        icon=ft.Icons.PERSON
                    ),
                    ft.PopupMenuItem(
                        text="Settings",
                        icon=ft.Icons.SETTINGS
                    ),
                    ft.PopupMenuItem(),  # Divider
                    ft.PopupMenuItem(
                        text="Logout",
                        icon=ft.Icons.LOGOUT,
                        on_click=self.handle_logout
                    )
                ]
            )
            nav_items.append(user_menu)
        else:
            # Login button
            login_btn = ft.TextButton(
                "Login",
                on_click=lambda _: self.page.go("/login"),
                style=ft.ButtonStyle(
                    color=ft.Colors.WHITE
                )
            )
            nav_items.append(login_btn)
            
        # Configure container
        self.content = ft.Row(
            [
                logo,
                ft.Row(nav_items, spacing=20)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        self.bgcolor = ft.Colors.BLUE_900
        self.padding = ft.padding.symmetric(horizontal=40, vertical=15)
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=5,
            color=ft.Colors.GREY_400
        )
        
    def handle_logout(self, e):
        """Handle logout."""
        if self.app:
            self.app.current_user = None
        self.page.go("/")