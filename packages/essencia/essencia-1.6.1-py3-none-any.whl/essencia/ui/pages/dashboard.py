"""Dashboard page component."""

import flet as ft

from essencia.ui.components import Header, UserCard


class DashboardPage(ft.Column):
    """Dashboard page component."""
    
    def __init__(self, page: ft.Page):
        """Initialize dashboard page.
        
        Args:
            page: Flet page instance
        """
        super().__init__(spacing=0, expand=True)
        self.page = page
        self.app = page.data.get("app")
        self.build()
        
    def build(self):
        """Build the dashboard page UI."""
        # Header with user menu
        header = Header(self.page, show_user_menu=True)
        
        # Dashboard content
        content = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        f"Welcome, {self.app.current_user.get('username', 'User')}!",
                        size=28,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=20),
                    ft.Row(
                        [
                            self._create_stat_card("Total Users", "1,234", ft.Icons.PEOPLE),
                            self._create_stat_card("Active Sessions", "89", ft.Icons.COMPUTER),
                            self._create_stat_card("API Calls", "45.2K", ft.Icons.API),
                            self._create_stat_card("Storage Used", "2.1 GB", ft.Icons.STORAGE)
                        ],
                        spacing=20,
                        wrap=True
                    ),
                    ft.Container(height=40),
                    ft.Text(
                        "Recent Activity",
                        size=24,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=10),
                    self._create_activity_list()
                ],
                scroll=ft.ScrollMode.AUTO
            ),
            padding=40,
            expand=True
        )
        
        # Add all components
        self.controls = [header, content]
        
    def _create_stat_card(self, title: str, value: str, icon: str) -> ft.Card:
        """Create a statistics card.
        
        Args:
            title: Card title
            value: Statistic value
            icon: Icon to display
            
        Returns:
            Statistics card component
        """
        return ft.Card(
            content=ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(icon, size=40, color=ft.Colors.BLUE_700),
                        ft.Column(
                            [
                                ft.Text(title, size=14, color=ft.Colors.GREY_700),
                                ft.Text(value, size=24, weight=ft.FontWeight.BOLD)
                            ],
                            spacing=5
                        )
                    ],
                    spacing=20
                ),
                padding=20,
                width=250
            )
        )
        
    def _create_activity_list(self) -> ft.Card:
        """Create activity list card.
        
        Returns:
            Activity list component
        """
        activities = [
            ("User john.doe logged in", "2 minutes ago", ft.Icons.LOGIN),
            ("New user registration: jane.smith", "15 minutes ago", ft.Icons.PERSON_ADD),
            ("Database backup completed", "1 hour ago", ft.Icons.BACKUP),
            ("API rate limit updated", "3 hours ago", ft.Icons.SETTINGS),
            ("System maintenance completed", "Yesterday", ft.Icons.BUILD)
        ]
        
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(icon, color=ft.Colors.BLUE_700),
                            title=ft.Text(title),
                            subtitle=ft.Text(time, size=12, color=ft.Colors.GREY_600)
                        )
                        for title, time, icon in activities
                    ],
                    spacing=0
                ),
                padding=10
            )
        )