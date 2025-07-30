"""
Mobile app screens.
"""
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime, date
import flet as ft

from .components import (
    MobileHeader,
    MobileCard,
    MobileList,
    MobileForm,
    MobileButton,
    MobileButtonStyle,
    MobileSearchBar
)


class BaseScreen(ft.Column):
    """Base class for mobile screens."""
    
    def __init__(
        self,
        user_data: Optional[Dict[str, Any]] = None,
        navigator: Optional[Any] = None,
        config: Optional[Any] = None,
        **kwargs
    ):
        self.user_data = user_data or {}
        self.navigator = navigator
        self.config = config
        
        super().__init__(
            spacing=0,
            expand=True,
            **kwargs
        )
        
        # Build screen
        self.controls = self.build()
    
    def build(self) -> List[ft.Control]:
        """Build screen controls. Override in subclasses."""
        return []
    
    def refresh(self):
        """Refresh screen data."""
        self.controls.clear()
        self.controls.extend(self.build())
        if self.page:
            self.page.update()


class LoginScreen(BaseScreen):
    """Login screen."""
    
    def __init__(self, on_login_success: Optional[Callable] = None, **kwargs):
        self.on_login_success = on_login_success
        super().__init__(**kwargs)
    
    def build(self) -> List[ft.Control]:
        # Form fields
        self.email_field = ft.TextField(
            label="Email",
            hint_text="seu@email.com",
            keyboard_type=ft.KeyboardType.EMAIL,
            autofocus=True
        )
        
        self.password_field = ft.TextField(
            label="Senha",
            password=True,
            can_reveal_password=True
        )
        
        # Login form
        login_form = MobileForm(
            fields=[
                self.email_field,
                self.password_field,
                ft.Row(
                    controls=[
                        ft.Checkbox(label="Lembrar-me"),
                        ft.TextButton(
                            "Esqueceu a senha?",
                            on_click=self._forgot_password
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                )
            ],
            on_submit=self._handle_login,
            submit_text="Entrar"
        )
        
        return [
            ft.Container(expand=True),  # Top spacer
            
            # Logo and title
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(
                            ft.icons.MEDICAL_SERVICES,
                            size=64,
                            color=ft.colors.PRIMARY
                        ),
                        ft.Text(
                            "Essencia Health",
                            size=28,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            "Sistema Médico Integrado",
                            size=16,
                            color=ft.colors.ON_SURFACE_VARIANT
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8
                ),
                padding=ft.padding.only(bottom=48),
                alignment=ft.alignment.center
            ),
            
            # Login form
            ft.Container(
                content=login_form,
                padding=ft.padding.symmetric(horizontal=24)
            ),
            
            # Alternative login options
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    bgcolor=ft.colors.ON_SURFACE_VARIANT,
                                    height=1,
                                    expand=True
                                ),
                                ft.Text("ou", color=ft.colors.ON_SURFACE_VARIANT),
                                ft.Container(
                                    bgcolor=ft.colors.ON_SURFACE_VARIANT,
                                    height=1,
                                    expand=True
                                )
                            ],
                            spacing=16,
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                        
                        MobileButton(
                            text="Entrar com Biometria",
                            icon=ft.icons.FINGERPRINT,
                            style=MobileButtonStyle.SECONDARY,
                            on_click=self._biometric_login,
                            width=float("inf")
                        )
                    ],
                    spacing=16
                ),
                padding=24
            ),
            
            ft.Container(expand=True),  # Bottom spacer
            
            # Footer
            ft.Container(
                content=ft.Text(
                    "© 2024 Essencia Health",
                    size=12,
                    color=ft.colors.ON_SURFACE_VARIANT,
                    text_align=ft.TextAlign.CENTER
                ),
                padding=ft.padding.only(bottom=16),
                alignment=ft.alignment.center
            )
        ]
    
    def _handle_login(self, data: Dict[str, Any]):
        """Handle login form submission."""
        # Validate fields
        if not data.get("Email") or not data.get("Senha"):
            self._show_error("Por favor, preencha todos os campos")
            return
        
        # Simulate API call
        # In production, this would call the actual API
        user_data = {
            "access_token": "fake_token_123",
            "user": {
                "id": "123",
                "email": data["Email"],
                "name": "Dr. João Silva",
                "role": "doctor"
            }
        }
        
        if self.on_login_success:
            self.on_login_success(user_data)
    
    def _biometric_login(self, e):
        """Handle biometric login."""
        # In production, this would trigger biometric authentication
        self._show_error("Biometria não disponível no simulador")
    
    def _forgot_password(self, e):
        """Handle forgot password."""
        # Navigate to forgot password screen
        if self.navigator:
            self.navigator.navigate("/forgot-password")
    
    def _show_error(self, message: str):
        """Show error message."""
        if self.page:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(message),
                    bgcolor=ft.colors.ERROR
                )
            )


class HomeScreen(BaseScreen):
    """Home/Dashboard screen."""
    
    def build(self) -> List[ft.Control]:
        user_name = self.user_data.get("user", {}).get("name", "Usuário")
        
        # Quick stats
        stats = [
            {"label": "Pacientes Hoje", "value": "12", "icon": ft.icons.PEOPLE},
            {"label": "Consultas", "value": "8", "icon": ft.icons.CALENDAR_TODAY},
            {"label": "Pendências", "value": "3", "icon": ft.icons.PENDING_ACTIONS},
            {"label": "Mensagens", "value": "5", "icon": ft.icons.MESSAGE}
        ]
        
        # Recent activities
        activities = [
            {
                "time": "10:30",
                "patient": "Maria Silva",
                "action": "Consulta realizada",
                "icon": ft.icons.CHECK_CIRCLE,
                "color": ft.colors.GREEN
            },
            {
                "time": "11:15",
                "patient": "João Santos",
                "action": "Exames solicitados",
                "icon": ft.icons.ASSIGNMENT,
                "color": ft.colors.BLUE
            },
            {
                "time": "14:00",
                "patient": "Ana Costa",
                "action": "Consulta agendada",
                "icon": ft.icons.SCHEDULE,
                "color": ft.colors.ORANGE
            }
        ]
        
        return [
            # Header
            MobileHeader(
                title=f"Olá, {user_name.split()[0]}",
                subtitle=datetime.now().strftime("%d de %B de %Y"),
                actions=[
                    ft.IconButton(
                        icon=ft.icons.NOTIFICATIONS_OUTLINED,
                        on_click=lambda e: self.navigator.navigate("/notifications")
                    )
                ]
            ),
            
            # Content
            ft.Container(
                content=ft.ListView(
                    controls=[
                        # Quick stats grid
                        ft.Container(
                            content=ft.GridView(
                                controls=[
                                    MobileCard(
                                        content=ft.Column(
                                            controls=[
                                                ft.Icon(
                                                    stat["icon"],
                                                    size=32,
                                                    color=ft.colors.PRIMARY
                                                ),
                                                ft.Text(
                                                    stat["value"],
                                                    size=24,
                                                    weight=ft.FontWeight.BOLD
                                                ),
                                                ft.Text(
                                                    stat["label"],
                                                    size=12,
                                                    color=ft.colors.ON_SURFACE_VARIANT
                                                )
                                            ],
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            spacing=4
                                        ),
                                        on_click=lambda e, s=stat: self._handle_stat_click(s)
                                    )
                                    for stat in stats
                                ],
                                max_extent=150,
                                child_aspect_ratio=1.2,
                                spacing=12,
                                run_spacing=12
                            ),
                            padding=ft.padding.symmetric(horizontal=16, vertical=8)
                        ),
                        
                        # Section title
                        ft.Container(
                            content=ft.Text(
                                "Atividades Recentes",
                                size=18,
                                weight=ft.FontWeight.W_500
                            ),
                            padding=ft.padding.only(left=16, right=16, top=24, bottom=8)
                        ),
                        
                        # Recent activities
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    MobileCard(
                                        leading=ft.Container(
                                            content=ft.Icon(
                                                activity["icon"],
                                                color=activity["color"],
                                                size=20
                                            ),
                                            bgcolor=activity["color"].with_opacity(0.1),
                                            border_radius=20,
                                            padding=8
                                        ),
                                        title=activity["patient"],
                                        subtitle=activity["action"],
                                        trailing=ft.Text(
                                            activity["time"],
                                            size=12,
                                            color=ft.colors.ON_SURFACE_VARIANT
                                        ),
                                        on_click=lambda e, a=activity: self._handle_activity_click(a)
                                    )
                                    for activity in activities
                                ],
                                spacing=8
                            ),
                            padding=ft.padding.symmetric(horizontal=16)
                        ),
                        
                        # Quick actions
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "Ações Rápidas",
                                        size=18,
                                        weight=ft.FontWeight.W_500
                                    ),
                                    ft.Row(
                                        controls=[
                                            MobileButton(
                                                text="Nova Consulta",
                                                icon=ft.icons.ADD,
                                                style=MobileButtonStyle.PRIMARY,
                                                on_click=lambda e: self.navigator.navigate("/appointments/new"),
                                                expand=True
                                            ),
                                            ft.Container(width=12),
                                            MobileButton(
                                                text="Buscar Paciente",
                                                icon=ft.icons.SEARCH,
                                                style=MobileButtonStyle.SECONDARY,
                                                on_click=lambda e: self.navigator.navigate("/patients"),
                                                expand=True
                                            )
                                        ]
                                    )
                                ],
                                spacing=12
                            ),
                            padding=ft.padding.all(16)
                        )
                    ],
                    spacing=0,
                    padding=ft.padding.only(bottom=80)  # Space for bottom nav
                ),
                expand=True
            )
        ]
    
    def _handle_stat_click(self, stat: Dict[str, Any]):
        """Handle stat card click."""
        # Navigate based on stat type
        if "Pacientes" in stat["label"]:
            self.navigator.navigate("/patients")
        elif "Consultas" in stat["label"]:
            self.navigator.navigate("/appointments")
    
    def _handle_activity_click(self, activity: Dict[str, Any]):
        """Handle activity click."""
        # Navigate to patient or appointment details
        pass


class PatientScreen(BaseScreen):
    """Patient list/search screen."""
    
    def build(self) -> List[ft.Control]:
        # Sample patients
        self.patients = [
            {
                "id": "1",
                "name": "Maria Silva",
                "age": 45,
                "last_visit": "15/01/2024",
                "conditions": ["Hipertensão", "Diabetes"],
                "photo": ft.icons.PERSON
            },
            {
                "id": "2",
                "name": "João Santos",
                "age": 62,
                "last_visit": "10/01/2024",
                "conditions": ["Artrite"],
                "photo": ft.icons.PERSON
            },
            {
                "id": "3",
                "name": "Ana Costa",
                "age": 28,
                "last_visit": "08/01/2024",
                "conditions": [],
                "photo": ft.icons.PERSON
            }
        ]
        
        self.filtered_patients = self.patients.copy()
        
        return [
            # Header with search
            ft.Container(
                content=ft.Column(
                    controls=[
                        MobileHeader(
                            title="Pacientes",
                            actions=[
                                ft.IconButton(
                                    icon=ft.icons.ADD,
                                    on_click=lambda e: self._add_patient()
                                )
                            ]
                        ),
                        MobileSearchBar(
                            hint_text="Buscar paciente...",
                            on_search=self._search_patients,
                            on_clear=self._clear_search
                        )
                    ],
                    spacing=8
                ),
                padding=ft.padding.only(bottom=8)
            ),
            
            # Patient list
            ft.Container(
                content=MobileList(
                    data=self.filtered_patients,
                    item_builder=self._build_patient_item,
                    on_item_click=self._handle_patient_click,
                    empty_message="Nenhum paciente encontrado"
                ),
                expand=True
            )
        ]
    
    def _build_patient_item(self, patient: Dict[str, Any]) -> ft.Control:
        """Build patient list item."""
        return MobileCard(
            leading=ft.Container(
                content=ft.Icon(patient["photo"], size=40),
                bgcolor=ft.colors.PRIMARY_CONTAINER,
                border_radius=20,
                padding=8
            ),
            title=patient["name"],
            subtitle=f"{patient['age']} anos • Última visita: {patient['last_visit']}",
            trailing=ft.Icon(ft.icons.CHEVRON_RIGHT),
            content=ft.Row(
                controls=[
                    ft.Chip(
                        label=ft.Text(condition, size=12),
                        bgcolor=ft.colors.ERROR_CONTAINER if condition == "Diabetes" else ft.colors.SECONDARY_CONTAINER
                    )
                    for condition in patient["conditions"][:2]
                ],
                spacing=4
            ) if patient["conditions"] else None
        )
    
    def _search_patients(self, query: str):
        """Search patients."""
        if query:
            self.filtered_patients = [
                p for p in self.patients
                if query.lower() in p["name"].lower()
            ]
        else:
            self.filtered_patients = self.patients.copy()
        
        self.refresh()
    
    def _clear_search(self):
        """Clear search."""
        self.filtered_patients = self.patients.copy()
        self.refresh()
    
    def _handle_patient_click(self, patient: Dict[str, Any]):
        """Handle patient selection."""
        # Navigate to patient details
        if self.navigator:
            self.navigator.navigate(f"/patients/{patient['id']}")
    
    def _add_patient(self):
        """Add new patient."""
        if self.navigator:
            self.navigator.navigate("/patients/new")


class AppointmentScreen(BaseScreen):
    """Appointment management screen."""
    
    def build(self) -> List[ft.Control]:
        # Sample appointments
        appointments = [
            {
                "time": "09:00",
                "patient": "Maria Silva", 
                "type": "Consulta",
                "status": "confirmed"
            },
            {
                "time": "10:00",
                "patient": "João Santos",
                "type": "Retorno",
                "status": "waiting"
            },
            {
                "time": "11:00",
                "patient": "Ana Costa",
                "type": "Consulta",
                "status": "scheduled"
            },
            {
                "time": "14:00",
                "patient": "Pedro Lima",
                "type": "Exame",
                "status": "scheduled"
            }
        ]
        
        return [
            # Header
            MobileHeader(
                title="Consultas",
                subtitle=datetime.now().strftime("%d/%m/%Y"),
                actions=[
                    ft.IconButton(
                        icon=ft.icons.CALENDAR_MONTH,
                        on_click=lambda e: self._show_calendar()
                    ),
                    ft.IconButton(
                        icon=ft.icons.ADD,
                        on_click=lambda e: self._add_appointment()
                    )
                ]
            ),
            
            # Appointment list
            ft.Container(
                content=MobileList(
                    data=appointments,
                    item_builder=self._build_appointment_item,
                    on_item_click=self._handle_appointment_click
                ),
                expand=True
            )
        ]
    
    def _build_appointment_item(self, appointment: Dict[str, Any]) -> ft.Control:
        """Build appointment list item."""
        status_colors = {
            "confirmed": ft.colors.GREEN,
            "waiting": ft.colors.ORANGE,
            "scheduled": ft.colors.BLUE
        }
        
        status_labels = {
            "confirmed": "Confirmado",
            "waiting": "Aguardando",
            "scheduled": "Agendado"
        }
        
        return MobileCard(
            leading=ft.Container(
                content=ft.Text(
                    appointment["time"],
                    size=16,
                    weight=ft.FontWeight.BOLD
                ),
                padding=8
            ),
            title=appointment["patient"],
            subtitle=appointment["type"],
            trailing=ft.Container(
                content=ft.Text(
                    status_labels[appointment["status"]],
                    size=12,
                    color=ft.colors.WHITE
                ),
                bgcolor=status_colors[appointment["status"]],
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=8, vertical=4)
            )
        )
    
    def _handle_appointment_click(self, appointment: Dict[str, Any]):
        """Handle appointment click."""
        # Show appointment details
        pass
    
    def _show_calendar(self):
        """Show calendar view."""
        pass
    
    def _add_appointment(self):
        """Add new appointment."""
        if self.navigator:
            self.navigator.navigate("/appointments/new")


class MedicationScreen(BaseScreen):
    """Medication management screen."""
    
    def build(self) -> List[ft.Control]:
        return [
            MobileHeader(
                title="Medicações",
                actions=[
                    ft.IconButton(
                        icon=ft.icons.ADD,
                        on_click=lambda e: self._add_medication()
                    )
                ]
            ),
            
            ft.Container(
                content=ft.Text("Medication management screen"),
                expand=True,
                alignment=ft.alignment.center
            )
        ]
    
    def _add_medication(self):
        """Add new medication."""
        pass


class ProfileScreen(BaseScreen):
    """User profile screen."""
    
    def build(self) -> List[ft.Control]:
        user = self.user_data.get("user", {})
        
        profile_items = [
            {
                "icon": ft.icons.PERSON,
                "title": "Informações Pessoais",
                "subtitle": "Nome, email, telefone",
                "action": lambda: self.navigator.navigate("/profile/edit")
            },
            {
                "icon": ft.icons.LOCK,
                "title": "Segurança",
                "subtitle": "Senha, autenticação",
                "action": lambda: self.navigator.navigate("/profile/security")
            },
            {
                "icon": ft.icons.NOTIFICATIONS,
                "title": "Notificações",
                "subtitle": "Configurar alertas",
                "action": lambda: self.navigator.navigate("/profile/notifications")
            },
            {
                "icon": ft.icons.HELP,
                "title": "Ajuda",
                "subtitle": "FAQ, suporte",
                "action": lambda: self.navigator.navigate("/help")
            },
            {
                "icon": ft.icons.INFO,
                "title": "Sobre",
                "subtitle": "Versão, termos",
                "action": lambda: self._show_about()
            }
        ]
        
        return [
            # Header
            MobileHeader(title="Perfil"),
            
            # Profile info
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.icons.PERSON, size=80),
                            bgcolor=ft.colors.PRIMARY_CONTAINER,
                            border_radius=40,
                            padding=16,
                            alignment=ft.alignment.center
                        ),
                        ft.Text(
                            user.get("name", "Usuário"),
                            size=24,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            user.get("email", ""),
                            size=16,
                            color=ft.colors.ON_SURFACE_VARIANT
                        ),
                        ft.Text(
                            user.get("role", "").title(),
                            size=14,
                            color=ft.colors.PRIMARY
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8
                ),
                padding=24
            ),
            
            # Menu items
            ft.Container(
                content=ft.Column(
                    controls=[
                        MobileCard(
                            leading=ft.Icon(item["icon"]),
                            title=item["title"],
                            subtitle=item["subtitle"],
                            trailing=ft.Icon(ft.icons.CHEVRON_RIGHT),
                            on_click=lambda e, action=item["action"]: action()
                        )
                        for item in profile_items
                    ],
                    spacing=8
                ),
                padding=ft.padding.symmetric(horizontal=16),
                expand=True
            ),
            
            # Logout button
            ft.Container(
                content=MobileButton(
                    text="Sair",
                    icon=ft.icons.LOGOUT,
                    style=MobileButtonStyle.DANGER,
                    on_click=lambda e: self._logout(),
                    width=float("inf")
                ),
                padding=16
            )
        ]
    
    def _show_about(self):
        """Show about dialog."""
        if self.page:
            dialog = ft.AlertDialog(
                title=ft.Text("Sobre"),
                content=ft.Column(
                    controls=[
                        ft.Text("Essencia Health"),
                        ft.Text("Versão 1.0.0"),
                        ft.Text("© 2024 Essencia"),
                    ],
                    spacing=8
                ),
                actions=[
                    ft.TextButton("Fechar", on_click=lambda e: self._close_dialog(dialog))
                ]
            )
            self.page.dialog = dialog
            dialog.open = True
            self.page.update()
    
    def _close_dialog(self, dialog):
        """Close dialog."""
        dialog.open = False
        self.page.update()
    
    def _logout(self):
        """Logout user."""
        # Call app logout method
        if hasattr(self.page, "app"):
            self.page.app.logout()