"""Home page component."""

import flet as ft

from essencia.ui.components import Header, Footer


class HomePage(ft.Column):
    """Home page component."""
    
    def __init__(self, page: ft.Page):
        """Initialize home page.
        
        Args:
            page: Flet page instance
        """
        super().__init__(spacing=0, expand=True)
        self.page = page
        self.build()
        
    def build(self):
        """Build the home page UI."""
        # Header
        header = Header(self.page)
        
        # Hero section
        hero = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Welcome to Essencia",
                        size=48,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    ),
                    ft.Text(
                        "A modern Python application framework",
                        size=20,
                        color=ft.Colors.WHITE70
                    ),
                    ft.Container(height=20),
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Get Started",
                                on_click=lambda _: self.page.go("/login"),
                                style=ft.ButtonStyle(
                                    padding=ft.padding.symmetric(horizontal=30, vertical=15),
                                    text_style=ft.TextStyle(size=16)
                                )
                            ),
                            ft.OutlinedButton(
                                "Learn More",
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    side=ft.BorderSide(width=1, color=ft.Colors.WHITE),
                                    padding=ft.padding.symmetric(horizontal=30, vertical=15),
                                    text_style=ft.TextStyle(size=16)
                                )
                            )
                        ],
                        spacing=20
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER
            ),
            bgcolor=ft.Colors.BLUE_900,
            padding=100,
            expand=True
        )
        
        # Features section
        features = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Features",
                        size=36,
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Container(height=40),
                    ft.Row(
                        [
                            self._create_feature_card(
                                ft.Icons.SPEED,
                                "Fast & Scalable",
                                "Built with async/await for maximum performance"
                            ),
                            self._create_feature_card(
                                ft.Icons.STORAGE,
                                "Modern Storage",
                                "MongoDB and Redis for flexible data management"
                            ),
                            self._create_feature_card(
                                ft.Icons.BRUSH,
                                "Beautiful UI",
                                "Flet framework for cross-platform applications"
                            )
                        ],
                        spacing=30,
                        alignment=ft.MainAxisAlignment.CENTER,
                        wrap=True
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=60,
            bgcolor=ft.Colors.WHITE
        )
        
        # Footer
        footer = Footer()
        
        # Add all components
        self.controls = [
            header,
            ft.Column(
                [hero, features],
                spacing=0,
                expand=True,
                scroll=ft.ScrollMode.AUTO
            ),
            footer
        ]
        
    def _create_feature_card(self, icon: str, title: str, description: str) -> ft.Card:
        """Create a feature card.
        
        Args:
            icon: Icon to display
            title: Card title
            description: Card description
            
        Returns:
            Feature card component
        """
        return ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(icon, size=48, color=ft.Colors.BLUE_700),
                        ft.Text(
                            title,
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            description,
                            size=14,
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.GREY_700
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                padding=30,
                width=300
            )
        )