"""
Mobile app framework for Essencia using Flet.
"""
from typing import Optional, Dict, Any, List, Callable
import flet as ft
from dataclasses import dataclass

from essencia.integrations.flet import apply_security_to_page
from .navigation import MobileNavigator, MobileRoute, BottomNavigation
from .screens import LoginScreen, HomeScreen


@dataclass
class MobileConfig:
    """Mobile app configuration."""
    app_name: str = "Essencia Mobile"
    theme_mode: ft.ThemeMode = ft.ThemeMode.LIGHT
    primary_color: str = ft.colors.BLUE
    on_boarding: bool = True
    offline_mode: bool = True
    push_notifications: bool = True
    biometric_auth: bool = True
    
    # API configuration
    api_base_url: str = "http://localhost:8000/api/v1"
    websocket_url: str = "ws://localhost:8000/ws"
    
    # Storage
    local_storage: bool = True
    cache_size_mb: int = 50


class MobileApp:
    """Mobile application class for Essencia."""
    
    def __init__(self, config: Optional[MobileConfig] = None):
        self.config = config or MobileConfig()
        self.navigator: Optional[MobileNavigator] = None
        self.user_data: Dict[str, Any] = {}
        self.offline_queue: List[Dict[str, Any]] = []
        
    def create_app(self, page: ft.Page):
        """Create and configure the mobile app."""
        # Configure page
        page.title = self.config.app_name
        page.theme_mode = self.config.theme_mode
        page.theme = ft.Theme(color_scheme_seed=self.config.primary_color)
        
        # Mobile-specific settings
        page.window_width = 400  # Mobile width
        page.window_height = 800  # Mobile height
        page.window_resizable = False
        
        # Apply security
        apply_security_to_page(page)
        
        # Initialize navigator
        self.navigator = MobileNavigator(page)
        
        # Set up routes
        self._setup_routes()
        
        # Handle back button
        page.on_route_change = self._route_change
        page.on_view_pop = self._view_pop
        
        # Check authentication
        if self._is_authenticated():
            self.navigator.navigate("/home")
        else:
            self.navigator.navigate("/login")
    
    def _setup_routes(self):
        """Set up application routes."""
        # Define routes
        routes = [
            MobileRoute(
                path="/login",
                builder=lambda: LoginScreen(
                    on_login_success=self._handle_login_success
                ),
                auth_required=False
            ),
            MobileRoute(
                path="/home",
                builder=lambda: HomeScreen(
                    user_data=self.user_data,
                    navigator=self.navigator
                ),
                auth_required=True
            ),
            MobileRoute(
                path="/patients",
                builder=lambda: self._lazy_import_screen("PatientScreen"),
                auth_required=True
            ),
            MobileRoute(
                path="/appointments",
                builder=lambda: self._lazy_import_screen("AppointmentScreen"),
                auth_required=True
            ),
            MobileRoute(
                path="/medications",
                builder=lambda: self._lazy_import_screen("MedicationScreen"),
                auth_required=True
            ),
            MobileRoute(
                path="/profile",
                builder=lambda: self._lazy_import_screen("ProfileScreen"),
                auth_required=True
            )
        ]
        
        # Register routes
        for route in routes:
            self.navigator.register_route(route)
        
        # Set up bottom navigation for authenticated routes
        self.navigator.set_bottom_navigation(
            BottomNavigation(
                items=[
                    ft.NavigationDestination(
                        icon=ft.icons.HOME_OUTLINED,
                        selected_icon=ft.icons.HOME,
                        label="Início"
                    ),
                    ft.NavigationDestination(
                        icon=ft.icons.PEOPLE_OUTLINE,
                        selected_icon=ft.icons.PEOPLE,
                        label="Pacientes"
                    ),
                    ft.NavigationDestination(
                        icon=ft.icons.CALENDAR_TODAY_OUTLINED,
                        selected_icon=ft.icons.CALENDAR_TODAY,
                        label="Consultas"
                    ),
                    ft.NavigationDestination(
                        icon=ft.icons.MEDICATION_OUTLINED,
                        selected_icon=ft.icons.MEDICATION,
                        label="Medicações"
                    ),
                    ft.NavigationDestination(
                        icon=ft.icons.PERSON_OUTLINE,
                        selected_icon=ft.icons.PERSON,
                        label="Perfil"
                    )
                ],
                on_change=self._handle_bottom_nav_change
            )
        )
    
    def _lazy_import_screen(self, screen_name: str):
        """Lazy import screen to improve startup time."""
        from . import screens
        screen_class = getattr(screens, screen_name)
        return screen_class(
            user_data=self.user_data,
            navigator=self.navigator,
            config=self.config
        )
    
    def _route_change(self, e: ft.RouteChangeEvent):
        """Handle route changes."""
        self.navigator.handle_route_change(e.route)
    
    def _view_pop(self, e: ft.ViewPopEvent):
        """Handle back button."""
        self.navigator.go_back()
    
    def _handle_bottom_nav_change(self, index: int):
        """Handle bottom navigation changes."""
        routes = ["/home", "/patients", "/appointments", "/medications", "/profile"]
        if 0 <= index < len(routes):
            self.navigator.navigate(routes[index])
    
    def _is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        # Check local storage for token
        if self.navigator and self.navigator.page.client_storage:
            token = self.navigator.page.client_storage.get("access_token")
            return token is not None
        return False
    
    def _handle_login_success(self, user_data: Dict[str, Any]):
        """Handle successful login."""
        self.user_data = user_data
        
        # Store token
        if self.navigator and self.navigator.page.client_storage:
            self.navigator.page.client_storage.set(
                "access_token",
                user_data.get("access_token")
            )
        
        # Navigate to home
        self.navigator.navigate("/home")
    
    # Public methods
    def logout(self):
        """Logout user."""
        self.user_data = {}
        
        # Clear storage
        if self.navigator and self.navigator.page.client_storage:
            self.navigator.page.client_storage.remove("access_token")
        
        # Navigate to login
        self.navigator.navigate("/login")
    
    def sync_offline_data(self):
        """Sync offline data when connection is restored."""
        if not self.offline_queue:
            return
        
        # Process offline queue
        for item in self.offline_queue:
            # Send to API
            pass
        
        self.offline_queue.clear()
    
    def show_notification(self, title: str, message: str, action: Optional[Callable] = None):
        """Show in-app notification."""
        if self.navigator:
            snack_bar = ft.SnackBar(
                content=ft.Text(f"{title}: {message}"),
                action="Ver" if action else None,
                on_action=action
            )
            self.navigator.page.show_snack_bar(snack_bar)


def create_mobile_app(config: Optional[MobileConfig] = None) -> MobileApp:
    """Create a mobile app instance."""
    return MobileApp(config)


# Example usage
if __name__ == "__main__":
    # Create mobile app
    app = create_mobile_app(
        MobileConfig(
            app_name="Essencia Health",
            theme_mode=ft.ThemeMode.LIGHT,
            primary_color=ft.colors.TEAL
        )
    )
    
    # Run app
    ft.app(
        target=app.create_app,
        view=ft.AppView.FLET_APP,  # For mobile
        port=8550
    )