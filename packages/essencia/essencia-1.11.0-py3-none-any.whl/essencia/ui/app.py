"""Main Flet application class."""

import flet as ft

from essencia.core.config import Config
from essencia.database import MongoDB, RedisClient
from typing import Optional

from essencia.core.exceptions import DatabaseConnectionError
from essencia.ui.pages import HomePage, LoginPage, DashboardPage


class EssenciaApp:
    """Main application class."""
    
    def __init__(self, config: Config):
        """Initialize application.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.mongodb: Optional[MongoDB] = None
        self.redis: Optional[RedisClient] = None
        self.current_user = None
        
    async def initialize_databases(self):
        """Initialize database connections."""
        try:
            self.mongodb = MongoDB(
                self.config.database.mongodb_url,
                self.config.database.mongodb_database
            )
            self.redis = RedisClient(
                self.config.database.redis_url,
                self.config.database.redis_db
            )
            
            # Check connections
            if not await self.mongodb.health_check():
                print("Warning: Failed to connect to MongoDB. Running in demo mode.")
                self.mongodb = None
                
            if not await self.redis.health_check():
                print("Warning: Failed to connect to Redis. Running in demo mode.")
                self.redis = None
        except Exception as e:
            print(f"Warning: Database initialization failed: {e}. Running in demo mode.")
            self.mongodb = None
            self.redis = None
            
    async def main(self, page: ft.Page):
        """Main application entry point.
        
        Args:
            page: Flet page instance
        """
        # Configure page
        page.title = self.config.app.app_name
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        page.bgcolor = ft.Colors.GREY_100
        
        # Initialize databases
        await self.initialize_databases()
        
        # Store app instance in page data
        page.data = {"app": self}
        
        # Define routes
        def route_change(e):
            page.views.clear()
            
            if page.route == "/":
                page.views.append(
                    ft.View(
                        "/",
                        [HomePage(page)],
                        padding=0
                    )
                )
            elif page.route == "/login":
                page.views.append(
                    ft.View(
                        "/login",
                        [LoginPage(page)],
                        padding=0
                    )
                )
            elif page.route == "/dashboard":
                if not self.current_user:
                    page.go("/login")
                    return
                    
                page.views.append(
                    ft.View(
                        "/dashboard",
                        [DashboardPage(page)],
                        padding=0
                    )
                )
                
            page.update()
            
        def view_pop(e):
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
            
        page.on_route_change = route_change
        page.on_view_pop = view_pop
        
        # Navigate to home
        page.go("/")
        
    def run(self):
        """Run the application."""
        ft.app(
            target=self.main,
            port=self.config.app.port,
            view=ft.AppView.WEB_BROWSER if self.config.app.host != "localhost" else None
        )