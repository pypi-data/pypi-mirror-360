"""Footer component."""

import flet as ft
from datetime import datetime


class Footer(ft.Container):
    """Footer component."""
    
    def __init__(self):
        """Initialize footer."""
        super().__init__()
        self.build()
        
    def build(self):
        """Build the footer UI."""
        current_year = datetime.now().year
        
        self.content = ft.Row(
            [
                ft.Text(
                    f"© {current_year} Essencia. All rights reserved.",
                    color=ft.Colors.GREY_700,
                    size=14
                ),
                ft.Row(
                    [
                        ft.TextButton(
                            "Privacy Policy",
                            style=ft.ButtonStyle(
                                color=ft.Colors.GREY_700,
                                text_style=ft.TextStyle(size=14)
                            )
                        ),
                        ft.Text("|", color=ft.Colors.GREY_400),
                        ft.TextButton(
                            "Terms of Service",
                            style=ft.ButtonStyle(
                                color=ft.Colors.GREY_700,
                                text_style=ft.TextStyle(size=14)
                            )
                        ),
                        ft.Text("|", color=ft.Colors.GREY_400),
                        ft.TextButton(
                            "Contact",
                            style=ft.ButtonStyle(
                                color=ft.Colors.GREY_700,
                                text_style=ft.TextStyle(size=14)
                            )
                        )
                    ],
                    spacing=10
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        
        self.bgcolor = ft.Colors.GREY_200
        self.padding = ft.padding.symmetric(horizontal=40, vertical=20)