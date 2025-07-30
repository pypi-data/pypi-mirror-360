"""
Examples of using Essencia's Flet integration.

This module demonstrates how to use the security features
provided by the Flet integration.
"""

import flet as ft
from essencia.integrations.flet import (
    # Middleware
    apply_security_to_page,
    setup_page_security,
    
    # Decorators
    flet_rate_limit,
    flet_audit,
    flet_authorized,
    flet_session_required,
    audit_login,
    rate_limit_form,
    
    # Components
    SecureButton,
    SecureTextField,
    SecureContainer,
    RateLimitedButton,
    AuthorizedView,
    AuditedForm
)


def main(page: ft.Page):
    """Example Flet application with Essencia security features."""
    
    # Apply security to the page
    apply_security_to_page(page)
    
    # Example 1: Secure login form
    def create_login_form():
        username_field = SecureTextField(
            label="Usuário",
            max_length=50,
            sanitize=True,
            audit_changes=True
        )
        
        password_field = SecureTextField(
            label="Senha",
            password=True,
            max_length=100,
            sanitize=True
        )
        
        @audit_login
        @rate_limit_form
        def handle_login(e):
            # Your login logic here
            username = username_field.value
            password = password_field.value
            
            # Example: Create session on successful login
            if username and password:  # Add real authentication
                page._security['session_manager'].create_session(page, {
                    'id': '123',
                    'email': f'{username}@example.com',
                    'role': 'admin'
                })
                page.go('/dashboard')
        
        login_button = SecureButton(
            text="Entrar",
            on_click=handle_login,
            audit_action="LOGIN_ATTEMPT"
        )
        
        return ft.Column([
            ft.Text("Login", size=24),
            username_field,
            password_field,
            login_button
        ])
    
    # Example 2: Authorized dashboard
    @setup_page_security(
        require_auth=True,
        required_permissions=['view_dashboard'],
        rate_limit_config={'action': 'page_view', 'limit': 100, 'window': 60}
    )
    def dashboard_view(page: ft.Page):
        # Admin-only section
        admin_section = SecureContainer(
            content=ft.Column([
                ft.Text("Seção Administrativa", size=20),
                ft.Text("Apenas administradores podem ver isto")
            ]),
            required_role="admin",
            bgcolor=ft.colors.BLUE_GREY_100,
            padding=20
        )
        
        # Rate-limited action button
        @flet_authorized(permission='delete_records')
        @flet_audit('DELETE_RECORDS', include_args=True)
        def handle_delete(e):
            # Your delete logic here
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Registros deletados com sucesso"),
                bgcolor=ft.colors.GREEN
            )
            page.snack_bar.open = True
            page.update()
        
        delete_button = RateLimitedButton(
            text="Deletar Registros",
            on_click=handle_delete,
            action="delete_records",
            limit=3,
            window=300,  # 3 deletes per 5 minutes
            bgcolor=ft.colors.RED,
            color=ft.colors.WHITE
        )
        
        return ft.Column([
            ft.Text("Dashboard", size=24),
            admin_section,
            delete_button
        ])
    
    # Example 3: Audited data form
    def create_patient_form():
        @flet_session_required()
        def handle_patient_submit(e, form_data):
            # Your form submission logic
            print(f"Form submitted with data: {form_data}")
            
            page.snack_bar = ft.SnackBar(
                content=ft.Text("Paciente cadastrado com sucesso"),
                bgcolor=ft.colors.GREEN
            )
            page.snack_bar.open = True
            page.update()
        
        form = AuditedForm(
            form_name="patient_registration",
            on_submit=handle_patient_submit,
            controls=[
                SecureTextField(
                    label="Nome Completo",
                    max_length=100,
                    pattern=r"^[a-zA-ZÀ-ÿ\s]+$"
                ),
                SecureTextField(
                    label="CPF",
                    max_length=14,
                    pattern=r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"
                ),
                SecureTextField(
                    label="Email",
                    max_length=100,
                    pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                ),
                SecureTextField(
                    label="Telefone",
                    max_length=15,
                    pattern=r"^\(\d{2}\) \d{4,5}-\d{4}$"
                )
            ]
        )
        
        return form
    
    # Example 4: Different views based on authorization
    def create_views():
        # Public view
        public_view = ft.View(
            route="/",
            controls=[create_login_form()]
        )
        
        # Admin dashboard (requires admin role)
        admin_view = AuthorizedView(
            route="/admin",
            required_role="admin",
            controls=[
                ft.Text("Admin Dashboard", size=24),
                ft.Text("Apenas administradores têm acesso")
            ]
        )
        
        # Doctor view (requires medical permission)
        doctor_view = AuthorizedView(
            route="/doctor",
            required_permission="medical_access",
            controls=[
                ft.Text("Área Médica", size=24),
                create_patient_form()
            ]
        )
        
        return [public_view, admin_view, doctor_view]
    
    # Route change handler
    def route_change(route):
        page.views.clear()
        
        if page.route == "/":
            page.views.append(
                ft.View(
                    "/",
                    [create_login_form()],
                    vertical_alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        elif page.route == "/dashboard":
            dashboard_view(page)
            page.views.append(
                ft.View(
                    "/dashboard",
                    [
                        ft.AppBar(title=ft.Text("Dashboard")),
                        ft.Container(
                            content=dashboard_view(page),
                            padding=20
                        )
                    ]
                )
            )
        elif page.route == "/patient":
            page.views.append(
                ft.View(
                    "/patient",
                    [
                        ft.AppBar(title=ft.Text("Cadastro de Paciente")),
                        ft.Container(
                            content=create_patient_form(),
                            padding=20
                        )
                    ]
                )
            )
        
        page.update()
    
    # Setup routing
    page.on_route_change = route_change
    page.go(page.route)


if __name__ == "__main__":
    # Run the example app
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)