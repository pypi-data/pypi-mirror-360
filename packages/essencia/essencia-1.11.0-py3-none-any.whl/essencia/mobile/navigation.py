"""
Mobile navigation components and patterns.
"""
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
import flet as ft


@dataclass
class MobileRoute:
    """Mobile route definition."""
    path: str
    builder: Callable
    auth_required: bool = True
    title: Optional[str] = None
    icon: Optional[str] = None


class MobileNavigator:
    """Mobile navigation manager."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.routes: Dict[str, MobileRoute] = {}
        self.history: List[str] = []
        self.bottom_nav: Optional[BottomNavigation] = None
        self.current_route: Optional[str] = None
    
    def register_route(self, route: MobileRoute):
        """Register a route."""
        self.routes[route.path] = route
    
    def navigate(self, path: str, params: Optional[Dict[str, Any]] = None):
        """Navigate to a route."""
        if path not in self.routes:
            print(f"Route not found: {path}")
            return
        
        route = self.routes[path]
        
        # Check authentication
        if route.auth_required and not self._is_authenticated():
            self.navigate("/login")
            return
        
        # Add to history
        if self.current_route and self.current_route != path:
            self.history.append(self.current_route)
        
        self.current_route = path
        
        # Build screen
        screen = route.builder()
        
        # Create view
        view = ft.View(
            route=path,
            controls=[screen],
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=0,
            padding=0
        )
        
        # Add bottom navigation if set and route requires auth
        if self.bottom_nav and route.auth_required:
            view.controls.append(self.bottom_nav)
        
        # Clear and add view
        self.page.views.clear()
        self.page.views.append(view)
        self.page.update()
    
    def go_back(self):
        """Navigate back."""
        if self.history:
            previous_route = self.history.pop()
            self.navigate(previous_route)
        else:
            # Default to home or login
            if self._is_authenticated():
                self.navigate("/home")
            else:
                self.navigate("/login")
    
    def handle_route_change(self, route: str):
        """Handle route change event."""
        self.navigate(route)
    
    def set_bottom_navigation(self, bottom_nav: 'BottomNavigation'):
        """Set bottom navigation."""
        self.bottom_nav = bottom_nav
    
    def _is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        if self.page.client_storage:
            token = self.page.client_storage.get("access_token")
            return token is not None
        return False


class BottomNavigation(ft.NavigationBar):
    """Mobile bottom navigation bar."""
    
    def __init__(
        self,
        items: List[ft.NavigationDestination],
        on_change: Optional[Callable[[int], None]] = None,
        **kwargs
    ):
        super().__init__(
            destinations=items,
            on_change=lambda e: on_change(e.control.selected_index) if on_change else None,
            **kwargs
        )
        
        # Mobile-optimized styling
        self.height = 65
        self.bgcolor = ft.colors.SURFACE_VARIANT


class TabNavigation(ft.Tabs):
    """Tab navigation for sub-sections."""
    
    def __init__(
        self,
        tabs: List[ft.Tab],
        on_change: Optional[Callable[[int], None]] = None,
        **kwargs
    ):
        super().__init__(
            tabs=tabs,
            on_change=lambda e: on_change(e.control.selected_index) if on_change else None,
            scrollable=True,
            **kwargs
        )
        
        # Mobile-optimized styling
        self.height = 48


class NavigationDrawer(ft.NavigationDrawer):
    """Side navigation drawer for mobile."""
    
    def __init__(
        self,
        items: List[ft.NavigationDrawerDestination],
        on_change: Optional[Callable[[int], None]] = None,
        header: Optional[ft.Control] = None,
        **kwargs
    ):
        # Add header if provided
        controls = []
        if header:
            controls.append(header)
            controls.append(ft.Divider(thickness=1))
        
        controls.extend(items)
        
        super().__init__(
            controls=controls,
            on_change=lambda e: on_change(e.control.selected_index) if on_change else None,
            **kwargs
        )


class PageTransition:
    """Page transition animations."""
    
    @staticmethod
    def slide_in_right(page: ft.Page, view: ft.View):
        """Slide in from right animation."""
        # Flet handles this automatically with View transitions
        pass
    
    @staticmethod
    def slide_in_left(page: ft.Page, view: ft.View):
        """Slide in from left animation."""
        pass
    
    @staticmethod
    def fade_in(page: ft.Page, view: ft.View):
        """Fade in animation."""
        pass


class NavigationHeader(ft.AppBar):
    """Mobile navigation header/app bar."""
    
    def __init__(
        self,
        title: str,
        back_button: bool = True,
        on_back: Optional[Callable] = None,
        actions: Optional[List[ft.Control]] = None,
        **kwargs
    ):
        leading = None
        if back_button and on_back:
            leading = ft.IconButton(
                icon=ft.icons.ARROW_BACK,
                on_click=lambda e: on_back()
            )
        
        super().__init__(
            leading=leading,
            title=ft.Text(title),
            actions=actions or [],
            **kwargs
        )
        
        # Mobile-optimized styling
        self.toolbar_height = 56
        self.center_title = True