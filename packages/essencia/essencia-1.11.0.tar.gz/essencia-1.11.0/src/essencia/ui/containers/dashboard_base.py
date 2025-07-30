"""
Base Dashboard Components - Unified dashboard architecture.

Provides flexible, reusable dashboard components with support for
both synchronous and asynchronous data loading, caching, and
responsive layouts.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Union, TypeVar
from dataclasses import dataclass, field

import flet as ft

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class DashboardConfig:
    """Configuration for dashboard behavior and appearance.
    
    Example:
        ```python
        config = DashboardConfig(
            title="Sales Dashboard",
            async_mode=True,
            auto_refresh=True,
            refresh_interval=60
        )
        ```
    """
    title: str
    async_mode: bool = False
    enable_cache: bool = True
    cache_ttl: int = 300  # seconds
    auto_refresh: bool = False
    refresh_interval: int = 30  # seconds
    show_loading: bool = True
    responsive: bool = True
    enable_stats: bool = True
    error_retry: bool = True
    max_retries: int = 3


@dataclass 
class StatCard:
    """Configuration for dashboard statistics cards.
    
    Example:
        ```python
        card = StatCard(
            title="Total Sales",
            value="$12,345",
            icon=ft.Icons.ATTACH_MONEY,
            color=ft.Colors.GREEN,
            trend="up",
            subtitle="15% increase"
        )
        ```
    """
    title: str
    value: Union[str, int, float]
    icon: str
    color: Optional[str] = None
    subtitle: Optional[str] = None
    trend: Optional[str] = None  # "up", "down", "neutral"
    on_click: Optional[Callable] = None
    tooltip: Optional[str] = None
    format_value: Optional[Callable[[Any], str]] = None


@dataclass
class QuickAction:
    """Configuration for quick action buttons.
    
    Example:
        ```python
        action = QuickAction(
            title="Add New",
            icon=ft.Icons.ADD,
            on_click=lambda e: page.go("/new"),
            color=ft.Colors.BLUE
        )
        ```
    """
    title: str
    icon: str
    on_click: Callable
    color: Optional[str] = None
    tooltip: Optional[str] = None
    enabled: bool = True
    badge: Optional[str] = None


class BaseDashboard(ft.UserControl, ABC):
    """
    Base class for all dashboard implementations.
    
    Provides common functionality:
    - Loading states management
    - Statistics cards rendering
    - Quick actions handling
    - Responsive layout
    - Error handling
    - Caching support
    - Both sync and async data loading
    
    Example:
        ```python
        class MyDashboard(BaseDashboard):
            def load_data(self):
                # Load dashboard data
                self.stats = [
                    StatCard("Users", 150, ft.Icons.PEOPLE),
                    StatCard("Revenue", "$5,000", ft.Icons.ATTACH_MONEY)
                ]
                self.content_widgets = [
                    ft.Text("Dashboard Content")
                ]
        ```
    """
    
    def __init__(self, config: DashboardConfig, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        
        # State management
        self.loading = False
        self.error_message = None
        self.stats: List[StatCard] = []
        self.quick_actions: List[QuickAction] = []
        self.content_widgets: List[ft.Control] = []
        self._retry_count = 0
        self._last_refresh = None
        
        # UI Components
        self.title_widget = None
        self.stats_container = None
        self.actions_container = None
        self.content_container = None
        self.loading_overlay = None
        self.error_container = None
        
        # Auto-refresh timer
        self._refresh_timer = None
        
        # Cache
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        
    def build(self):
        """Build the complete dashboard UI."""
        main_content = ft.Column(
            [
                self._build_header(),
                self._build_stats_section(),
                self._build_actions_section(),
                self._build_content_section(),
                self._build_error_section()
            ],
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=20
        )
        
        # Wrap in stack for loading overlay
        return ft.Stack([
            main_content,
            self._build_loading_overlay()
        ])
    
    def _build_header(self) -> ft.Control:
        """Build dashboard header with title and controls."""
        self.title_widget = ft.Text(
            self.config.title,
            size=28,
            weight=ft.FontWeight.BOLD
        )
        
        header_controls = [self.title_widget]
        
        # Add refresh button
        if self.config.auto_refresh or self.config.enable_cache:
            refresh_btn = ft.IconButton(
                icon=ft.Icons.REFRESH,
                on_click=lambda e: self.refresh(force=True),
                tooltip="Refresh data"
            )
            header_controls.append(refresh_btn)
            
        # Add last update time
        if self._last_refresh:
            time_text = ft.Text(
                f"Updated: {self._last_refresh.strftime('%H:%M')}",
                size=12,
                color=ft.Colors.ON_SURFACE_VARIANT
            )
            header_controls.append(time_text)
        
        return ft.Row(
            header_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
    
    def _build_stats_section(self) -> ft.Control:
        """Build statistics cards section."""
        if not self.config.enable_stats:
            return ft.Container()
            
        self.stats_container = ft.Row(
            wrap=True,
            spacing=15,
            run_spacing=15,
            alignment=ft.MainAxisAlignment.START
        )
        
        return ft.Container(
            content=self.stats_container,
            padding=ft.padding.symmetric(vertical=10)
        )
    
    def _build_actions_section(self) -> ft.Control:
        """Build quick actions section."""
        self.actions_container = ft.Row(
            wrap=True,
            spacing=10,
            run_spacing=10,
            alignment=ft.MainAxisAlignment.START
        )
        
        return ft.Container(
            content=self.actions_container,
            padding=ft.padding.symmetric(vertical=10),
            visible=False  # Hidden by default
        )
    
    def _build_content_section(self) -> ft.Control:
        """Build main content section."""
        self.content_container = ft.Column(
            expand=True,
            spacing=15
        )
        
        return ft.Container(
            content=self.content_container,
            expand=True
        )
    
    def _build_error_section(self) -> ft.Control:
        """Build error display section."""
        self.error_container = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ERROR, color=ft.Colors.ERROR),
                ft.Text("", color=ft.Colors.ERROR, expand=True),
                ft.TextButton(
                    "Retry",
                    on_click=lambda e: self.refresh(force=True)
                )
            ]),
            visible=False,
            bgcolor=ft.Colors.ERROR_CONTAINER,
            padding=ft.padding.all(10),
            border_radius=ft.border_radius.all(5)
        )
        
        return self.error_container
    
    def _build_loading_overlay(self) -> ft.Control:
        """Build loading overlay."""
        from ..feedback import LoadingIndicator, LoadingSize
        
        self.loading_overlay = ft.Container(
            content=ft.Column([
                LoadingIndicator(size=LoadingSize.LARGE),
                ft.Text("Loading...", size=16)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=ft.Colors.with_opacity(0.8, ft.Colors.BACKGROUND),
            visible=False,
            expand=True,
            alignment=ft.alignment.center
        )
        
        return self.loading_overlay
    
    def build_stat_card(self, stat: StatCard) -> ft.Control:
        """Build a standardized statistics card."""
        # Determine card color
        card_color = stat.color or ft.Colors.PRIMARY_CONTAINER
        
        # Format value
        display_value = stat.value
        if stat.format_value:
            display_value = stat.format_value(stat.value)
        
        # Build trend indicator
        trend_row = []
        if stat.icon:
            trend_row.append(ft.Icon(stat.icon, size=24))
            
        if stat.trend:
            if stat.trend == "up":
                trend_row.append(ft.Icon(ft.Icons.TRENDING_UP, color=ft.Colors.GREEN, size=16))
            elif stat.trend == "down":
                trend_row.append(ft.Icon(ft.Icons.TRENDING_DOWN, color=ft.Colors.RED, size=16))
            else:
                trend_row.append(ft.Icon(ft.Icons.TRENDING_FLAT, color=ft.Colors.GREY, size=16))
        
        # Build card content
        content_column = ft.Column([
            ft.Row(trend_row, alignment=ft.MainAxisAlignment.SPACE_BETWEEN) if trend_row else ft.Container(),
            ft.Text(
                str(display_value),
                size=28,
                weight=ft.FontWeight.BOLD
            ),
            ft.Text(
                stat.title,
                size=14,
                opacity=0.8
            )
        ], 
        spacing=5,
        tight=True)
        
        # Add subtitle if provided
        if stat.subtitle:
            content_column.controls.append(
                ft.Text(
                    stat.subtitle,
                    size=12,
                    opacity=0.6
                )
            )
        
        # Create card
        card = ft.Container(
            content=content_column,
            padding=ft.padding.all(20),
            bgcolor=card_color,
            border_radius=ft.border_radius.all(10),
            width=200 if self.config.responsive else None,
            on_click=stat.on_click,
            tooltip=stat.tooltip,
            ink=bool(stat.on_click)
        )
        
        return card
    
    def build_action_button(self, action: QuickAction) -> ft.Control:
        """Build a quick action button."""
        from ..buttons import PrimaryButton
        
        button = PrimaryButton(
            text=action.title,
            icon=action.icon,
            on_click=action.on_click,
            disabled=not action.enabled,
            tooltip=action.tooltip
        )
        
        # Add badge if provided
        if action.badge:
            return ft.Stack([
                button,
                ft.Container(
                    content=ft.Text(action.badge, size=10, color=ft.Colors.ON_ERROR),
                    bgcolor=ft.Colors.ERROR,
                    border_radius=ft.border_radius.all(10),
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    right=0,
                    top=0
                )
            ])
        
        return button
    
    def show_loading(self, message: str = "Loading..."):
        """Show loading state."""
        self.loading = True
        if self.loading_overlay:
            self.loading_overlay.visible = True
            # Update loading message
            if isinstance(self.loading_overlay.content, ft.Column):
                self.loading_overlay.content.controls[1].value = message
        self.update()
    
    def hide_loading(self):
        """Hide loading state."""
        self.loading = False
        if self.loading_overlay:
            self.loading_overlay.visible = False
        self.update()
    
    def show_error(self, message: str):
        """Show error message."""
        self.error_message = message
        if self.error_container:
            self.error_container.visible = True
            # Update error text
            if isinstance(self.error_container.content, ft.Row):
                self.error_container.content.controls[1].value = message
        self.update()
    
    def hide_error(self):
        """Hide error message."""
        self.error_message = None
        if self.error_container:
            self.error_container.visible = False
        self.update()
    
    def update_stats(self):
        """Update statistics cards display."""
        if not self.stats_container:
            return
            
        self.stats_container.controls.clear()
        for stat in self.stats:
            self.stats_container.controls.append(self.build_stat_card(stat))
        
        if hasattr(self.stats_container, 'update'):
            self.stats_container.update()
    
    def update_actions(self):
        """Update quick actions display."""
        if not self.actions_container:
            return
            
        self.actions_container.controls.clear()
        
        if self.quick_actions:
            for action in self.quick_actions:
                self.actions_container.controls.append(self.build_action_button(action))
            self.actions_container.visible = True
        else:
            self.actions_container.visible = False
            
        if hasattr(self.actions_container, 'update'):
            self.actions_container.update()
    
    def update_content(self):
        """Update main content display."""
        if not self.content_container:
            return
            
        self.content_container.controls.clear()
        self.content_container.controls.extend(self.content_widgets)
        
        if hasattr(self.content_container, 'update'):
            self.content_container.update()
    
    def refresh(self, force: bool = False):
        """Refresh dashboard data."""
        if self.config.async_mode:
            asyncio.create_task(self._async_refresh(force))
        else:
            self._sync_refresh(force)
    
    def _sync_refresh(self, force: bool = False):
        """Synchronous refresh implementation."""
        try:
            # Check cache
            if not force and self.config.enable_cache and self._is_cache_valid():
                self._load_from_cache()
                return
                
            self.show_loading()
            self.hide_error()
            
            # Load data
            self.load_data()
            
            # Update cache
            if self.config.enable_cache:
                self._update_cache()
                
            # Update UI
            self.update_stats()
            self.update_actions()
            self.update_content()
            
            self._last_refresh = datetime.now()
            self._retry_count = 0
            
        except Exception as e:
            logger.error(f"Dashboard refresh error: {e}")
            self._handle_error(e)
        finally:
            self.hide_loading()
    
    async def _async_refresh(self, force: bool = False):
        """Asynchronous refresh implementation."""
        try:
            # Check cache
            if not force and self.config.enable_cache and self._is_cache_valid():
                self._load_from_cache()
                return
                
            self.show_loading()
            self.hide_error()
            
            # Load data
            await self.load_data_async()
            
            # Update cache
            if self.config.enable_cache:
                self._update_cache()
                
            # Update UI
            self.update_stats()
            self.update_actions()
            self.update_content()
            
            self._last_refresh = datetime.now()
            self._retry_count = 0
            
        except Exception as e:
            logger.error(f"Dashboard async refresh error: {e}")
            self._handle_error(e)
        finally:
            self.hide_loading()
    
    def _handle_error(self, error: Exception):
        """Handle refresh errors with retry logic."""
        self._retry_count += 1
        
        if self.config.error_retry and self._retry_count < self.config.max_retries:
            # Schedule retry
            retry_delay = min(2 ** self._retry_count, 30)  # Exponential backoff
            asyncio.create_task(self._retry_after_delay(retry_delay))
            self.show_error(f"Error loading data. Retrying in {retry_delay}s...")
        else:
            self.show_error(f"Error loading data: {str(error)}")
    
    async def _retry_after_delay(self, delay: int):
        """Retry refresh after delay."""
        await asyncio.sleep(delay)
        self.refresh(force=True)
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid."""
        if not self._cache_timestamps:
            return False
            
        oldest_timestamp = min(self._cache_timestamps.values())
        age = (datetime.now() - oldest_timestamp).total_seconds()
        return age < self.config.cache_ttl
    
    def _load_from_cache(self):
        """Load data from cache."""
        # Subclasses should override to restore state from self._cache
        pass
    
    def _update_cache(self):
        """Update cache with current data."""
        # Subclasses should override to save state to self._cache
        self._cache_timestamps['last_update'] = datetime.now()
    
    def did_mount(self):
        """Called when dashboard is mounted."""
        # Initial data load
        self.refresh()
        
        # Setup auto-refresh
        if self.config.auto_refresh:
            self._start_auto_refresh()
    
    def will_unmount(self):
        """Called when dashboard is being unmounted."""
        self._stop_auto_refresh()
    
    def _start_auto_refresh(self):
        """Start auto-refresh timer."""
        if self._refresh_timer:
            self._refresh_timer.cancel()
            
        async def auto_refresh():
            while True:
                await asyncio.sleep(self.config.refresh_interval)
                if self.page:  # Still mounted
                    self.refresh()
                else:
                    break
                    
        self._refresh_timer = asyncio.create_task(auto_refresh())
    
    def _stop_auto_refresh(self):
        """Stop auto-refresh timer."""
        if self._refresh_timer:
            self._refresh_timer.cancel()
            self._refresh_timer = None
    
    @abstractmethod
    def load_data(self):
        """Load dashboard data (sync mode).
        
        Subclasses must implement this to load:
        - self.stats: List of StatCard objects
        - self.quick_actions: List of QuickAction objects
        - self.content_widgets: List of Flet controls
        """
        pass
    
    async def load_data_async(self):
        """Load dashboard data (async mode).
        
        Default implementation calls sync version.
        Override for true async loading.
        """
        self.load_data()


class SyncDashboard(BaseDashboard):
    """Synchronous dashboard implementation.
    
    Example:
        ```python
        class MySyncDashboard(SyncDashboard):
            def load_data(self):
                # Load from database
                users = db.get_user_count()
                revenue = db.get_total_revenue()
                
                self.stats = [
                    StatCard("Users", users, ft.Icons.PEOPLE),
                    StatCard("Revenue", f"${revenue}", ft.Icons.ATTACH_MONEY)
                ]
        ```
    """
    
    def __init__(self, config: DashboardConfig, **kwargs):
        config.async_mode = False
        super().__init__(config, **kwargs)


class AsyncDashboard(BaseDashboard):
    """Asynchronous dashboard implementation.
    
    Example:
        ```python
        class MyAsyncDashboard(AsyncDashboard):
            async def load_data_async(self):
                # Load from async API
                users = await api.get_user_count()
                revenue = await api.get_total_revenue()
                
                self.stats = [
                    StatCard("Users", users, ft.Icons.PEOPLE),
                    StatCard("Revenue", f"${revenue}", ft.Icons.ATTACH_MONEY)
                ]
        ```
    """
    
    def __init__(self, config: DashboardConfig, **kwargs):
        config.async_mode = True
        super().__init__(config, **kwargs)


def create_stats_dashboard(
    title: str,
    stats: List[StatCard],
    actions: Optional[List[QuickAction]] = None,
    content: Optional[List[ft.Control]] = None,
    **config_kwargs
) -> BaseDashboard:
    """Create a simple statistics dashboard.
    
    Args:
        title: Dashboard title
        stats: List of statistics cards
        actions: Optional quick actions
        content: Optional content widgets
        **config_kwargs: Additional config options
        
    Returns:
        Configured dashboard instance
        
    Example:
        ```python
        dashboard = create_stats_dashboard(
            "Sales Overview",
            stats=[
                StatCard("Orders", 42, ft.Icons.SHOPPING_CART),
                StatCard("Revenue", "$1,234", ft.Icons.ATTACH_MONEY)
            ],
            auto_refresh=True
        )
        ```
    """
    class SimpleDashboard(SyncDashboard):
        def load_data(self):
            self.stats = stats
            self.quick_actions = actions or []
            self.content_widgets = content or []
    
    config = DashboardConfig(title=title, **config_kwargs)
    return SimpleDashboard(config)


def create_admin_dashboard(page: ft.Page) -> BaseDashboard:
    """Create a pre-configured admin dashboard.
    
    Example dashboard with common admin statistics and actions.
    """
    stats = [
        StatCard(
            title="Total Users",
            value=1234,
            icon=ft.Icons.PEOPLE,
            trend="up",
            subtitle="12% increase"
        ),
        StatCard(
            title="Active Sessions", 
            value=89,
            icon=ft.Icons.COMPUTER,
            color=ft.Colors.GREEN_200
        ),
        StatCard(
            title="API Calls",
            value="15.2k",
            icon=ft.Icons.API,
            color=ft.Colors.BLUE_200
        ),
        StatCard(
            title="Errors",
            value=3,
            icon=ft.Icons.ERROR,
            color=ft.Colors.RED_200,
            trend="down"
        )
    ]
    
    actions = [
        QuickAction(
            title="Add User",
            icon=ft.Icons.PERSON_ADD,
            on_click=lambda e: page.go("/admin/users/new")
        ),
        QuickAction(
            title="View Logs",
            icon=ft.Icons.DESCRIPTION,
            on_click=lambda e: page.go("/admin/logs")
        ),
        QuickAction(
            title="Settings",
            icon=ft.Icons.SETTINGS,
            on_click=lambda e: page.go("/admin/settings")
        )
    ]
    
    return create_stats_dashboard(
        "Admin Dashboard",
        stats=stats,
        actions=actions,
        auto_refresh=True,
        refresh_interval=60
    )