"""Login page component."""

import flet as ft

from essencia.ui.components import Header


class LoginPage(ft.Column):
    """Login page component."""
    
    def __init__(self, page: ft.Page):
        """Initialize login page.
        
        Args:
            page: Flet page instance
        """
        super().__init__(spacing=0, expand=True)
        self.page = page
        self.app = page.data.get("app")
        self.build()
        
    def build(self):
        """Build the login page UI."""
        # Header
        header = Header(self.page)
        
        # Login form
        self.username_field = ft.TextField(
            label="Username",
            width=300,
            autofocus=True
        )
        
        self.password_field = ft.TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            width=300
        )
        
        self.error_text = ft.Text(
            "",
            color=ft.Colors.RED,
            size=14,
            visible=False
        )
        
        login_form = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Login",
                        size=32,
                        weight=ft.FontWeight.BOLD
                    ),
                    ft.Container(height=20),
                    self.username_field,
                    self.password_field,
                    self.error_text,
                    ft.Container(height=20),
                    ft.ElevatedButton(
                        "Login",
                        width=300,
                        on_click=self.handle_login,
                        style=ft.ButtonStyle(
                            padding=ft.padding.all(15)
                        )
                    ),
                    ft.Container(height=10),
                    ft.Row(
                        [
                            ft.Text("Don't have an account?"),
                            ft.TextButton(
                                "Sign up",
                                on_click=lambda _: self.show_signup_dialog()
                            )
                        ],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=50,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.GREY_300
            )
        )
        
        # Center the login form
        login_container = ft.Container(
            content=login_form,
            alignment=ft.Alignment.center,
            expand=True,
            bgcolor=ft.Colors.GREY_100
        )
        
        # Add all components
        self.controls = [header, login_container]
        
    def handle_login(self, e):
        """Handle login button click."""
        username = self.username_field.value
        password = self.password_field.value
        
        # Validate inputs
        if not username or not password:
            self.error_text.value = "Please enter username and password"
            self.error_text.visible = True
            self.page.update()
            return
            
        # Demo mode login (when database is not available)
        if not self.app.mongodb:
            if username == "admin" and password == "password":
                self.app.current_user = {"username": username}
                self.page.go("/dashboard")
            else:
                self.error_text.value = "Demo mode: Use admin/password to login"
                self.error_text.visible = True
                self.page.update()
        else:
            # TODO: Implement actual authentication with database
            self.error_text.value = "Database authentication not yet implemented"
            self.error_text.visible = True
            self.page.update()
            
    def show_signup_dialog(self):
        """Show signup dialog."""
        dialog = ft.AlertDialog(
            title=ft.Text("Sign Up"),
            content=ft.Text("Sign up functionality coming soon!"),
            actions=[
                ft.TextButton("OK", on_click=lambda _: self.page.close_dialog())
            ]
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()