"""
Dashboard components for essencia.

This module provides base dashboard classes and builders for creating
consistent, feature-rich dashboards.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union
import asyncio
import flet as ft

from .base import ThemedControl, ControlConfig, get_controls_config, DefaultTheme
from .layout import Panel, Section, Grid
from .lazy import LazyStatsWidget, AsyncDataProvider
from .buttons import ThemedIconButton


@dataclass
class StatCard:
    """Configuration for a statistics card."""
    title: str
    data_provider: AsyncDataProvider
    icon: Optional[str] = None
    color: Optional[str] = None
    formatter: Optional[Callable[[Any], str]] = None
    on_click: Optional[Callable[[], None]] = None
    tooltip: Optional[str] = None


@dataclass
class QuickAction:
    """Configuration for a quick action button."""
    label: str
    icon: str
    on_click: Callable[[], None]
    color: Optional[str] = None
    tooltip: Optional[str] = None
    badge: Optional[Union[str, int]] = None


@dataclass
class DashboardConfig:
    """Configuration for dashboard layout and behavior."""
    title: str = ""
    subtitle: Optional[str] = None
    columns: int = 3
    spacing: int = 20
    padding: int = 20
    show_header: bool = True
    show_refresh: bool = True
    auto_refresh_interval: Optional[int] = None  # seconds
    
    # Sections
    show_stats: bool = True
    show_quick_actions: bool = True
    show_recent_items: bool = True
    show_charts: bool = True
    
    # Responsive breakpoints
    mobile_columns: int = 1
    tablet_columns: int = 2
    desktop_columns: int = 3
    mobile_breakpoint: int = 600
    tablet_breakpoint: int = 1024


class BaseDashboard(ThemedControl, ABC):
    """Abstract base class for dashboards."""
    
    def __init__(self,
                 config: Optional[DashboardConfig] = None,
                 control_config: Optional[ControlConfig] = None):
        super().__init__(control_config)
        self.config = config or DashboardConfig()
        
        # Dashboard components
        self.stat_cards: List[StatCard] = []
        self.quick_actions: List[QuickAction] = []
        self.sections: List[Section] = []
        
        # State
        self._refresh_task: Optional[asyncio.Task] = None
        self._is_refreshing = False
        
        # Controls
        self._header_container: Optional[ft.Container] = None
        self._stats_container: Optional[ft.Container] = None
        self._actions_container: Optional[ft.Container] = None
        self._content_container: Optional[ft.Container] = None
    
    @abstractmethod
    async def load_dashboard_data(self) -> None:
        """Load dashboard data (to be implemented by subclasses)."""
        pass
    
    def add_stat_card(self, stat_card: StatCard) -> 'BaseDashboard':
        """Add a statistics card to the dashboard."""
        self.stat_cards.append(stat_card)
        return self
    
    def add_quick_action(self, action: QuickAction) -> 'BaseDashboard':
        """Add a quick action to the dashboard."""
        self.quick_actions.append(action)
        return self
    
    def add_section(self, section: Section) -> 'BaseDashboard':
        """Add a custom section to the dashboard."""
        self.sections.append(section)
        return self
    
    def _build_header(self) -> Optional[ft.Control]:
        """Build dashboard header."""
        if not self.config.show_header or not self.config.title:
            return None
        
        theme = self.theme or DefaultTheme()
        
        header_controls = []
        
        # Title and subtitle
        title_controls = [
            ft.Text(
                self.config.title,
                size=24,
                weight=ft.FontWeight.BOLD,
                color=theme.on_surface,
            )
        ]
        
        if self.config.subtitle:
            title_controls.append(
                ft.Text(
                    self.config.subtitle,
                    size=14,
                    color=theme.on_surface_variant,
                )
            )
        
        header_controls.append(
            ft.Column(
                controls=title_controls,
                spacing=4,
            )
        )
        
        # Refresh button
        if self.config.show_refresh:
            refresh_button = ThemedIconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Atualizar dashboard",
                on_click=lambda e: self._refresh_dashboard(),
            ).build()
            
            # Add spinning animation when refreshing
            if self._is_refreshing:
                refresh_button.icon = ft.Icons.AUTORENEW
                refresh_button.rotate = ft.transform.Rotate(
                    angle=0,
                    animate=ft.Animation(1000, ft.AnimationCurve.LINEAR),
                )
            
            header_controls.append(refresh_button)
        
        return ft.Row(
            controls=header_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )
    
    def _build_stats(self) -> Optional[ft.Control]:
        """Build statistics cards section."""
        if not self.config.show_stats or not self.stat_cards:
            return None
        
        stat_widgets = []
        
        for stat in self.stat_cards:
            stat_widget = LazyStatsWidget(
                title=stat.title,
                data_provider=stat.data_provider,
                stat_formatter=stat.formatter,
                icon=stat.icon,
                color=stat.color,
                show_refresh_button=False,
            ).build()
            
            # Wrap in panel
            panel = Panel(
                content=stat_widget,
                padding=self.config.padding,
                expand=True,
            ).build()
            
            # Add click handler if provided
            if stat.on_click:
                panel.on_click = lambda e, fn=stat.on_click: fn()
                panel.tooltip = stat.tooltip
            
            stat_widgets.append(panel)
        
        return Grid(
            controls=stat_widgets,
            columns=self._get_responsive_columns(),
            spacing=self.config.spacing,
        ).build()
    
    def _build_quick_actions(self) -> Optional[ft.Control]:
        """Build quick actions section."""
        if not self.config.show_quick_actions or not self.quick_actions:
            return None
        
        theme = self.theme or DefaultTheme()
        action_controls = []
        
        for action in self.quick_actions:
            # Create button with icon and label
            button_content = ft.Column(
                controls=[
                    ft.Icon(
                        action.icon,
                        size=32,
                        color=action.color or theme.primary,
                    ),
                    ft.Text(
                        action.label,
                        size=12,
                        color=theme.on_surface,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            )
            
            # Add badge if provided
            if action.badge is not None:
                button_with_badge = ft.Stack(
                    controls=[
                        button_content,
                        ft.Container(
                            content=ft.Text(
                                str(action.badge),
                                size=10,
                                color=theme.on_error,
                                weight=ft.FontWeight.BOLD,
                            ),
                            bgcolor=theme.error,
                            border_radius=10,
                            padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            alignment=ft.alignment.center,
                            right=0,
                            top=0,
                        ),
                    ],
                )
                button_content = button_with_badge
            
            button = ft.Container(
                content=button_content,
                padding=self.config.padding,
                border_radius=get_controls_config().default_border_radius,
                bgcolor=theme.surface,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=4,
                    color=theme.shadow + "20",
                    offset=ft.Offset(0, 2),
                ),
                on_click=lambda e, fn=action.on_click: fn(),
                tooltip=action.tooltip,
                width=120,
                height=100,
            )
            
            # Add hover effect
            def on_hover(e, btn=button):
                if e.data == "true":
                    btn.shadow = ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=8,
                        color=theme.shadow + "30",
                        offset=ft.Offset(0, 4),
                    )
                else:
                    btn.shadow = ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=4,
                        color=theme.shadow + "20",
                        offset=ft.Offset(0, 2),
                    )
                btn.update()
            
            button.on_hover = on_hover
            action_controls.append(button)
        
        return Section(
            title="Ações Rápidas",
            content=ft.Row(
                controls=action_controls,
                wrap=True,
                spacing=self.config.spacing,
                run_spacing=self.config.spacing,
            ),
        ).build()
    
    def _get_responsive_columns(self) -> int:
        """Get number of columns based on screen size."""
        # This is a simplified version - in real app would check actual screen size
        return self.config.desktop_columns
    
    def _refresh_dashboard(self) -> None:
        """Refresh dashboard data."""
        if self._control and self._control.page:
            self._control.page.run_task(self._async_refresh())
    
    async def _async_refresh(self) -> None:
        """Async refresh implementation."""
        if self._is_refreshing:
            return
        
        self._is_refreshing = True
        
        # Update refresh button animation
        if self._header_container:
            self._header_container.content = self._build_header()
            self._header_container.update()
        
        try:
            # Reload dashboard data
            await self.load_dashboard_data()
            
            # Refresh all stat cards
            for stat in self.stat_cards:
                if hasattr(stat.data_provider, 'refresh_data'):
                    await stat.data_provider.refresh_data()
            
            # Rebuild sections
            self._update_sections()
        
        finally:
            self._is_refreshing = False
            
            # Update refresh button back to normal
            if self._header_container:
                self._header_container.content = self._build_header()
                self._header_container.update()
    
    def _update_sections(self) -> None:
        """Update dashboard sections."""
        if self._stats_container and self.config.show_stats:
            self._stats_container.content = self._build_stats()
            self._stats_container.update()
        
        if self._actions_container and self.config.show_quick_actions:
            self._actions_container.content = self._build_quick_actions()
            self._actions_container.update()
    
    def _schedule_auto_refresh(self) -> None:
        """Schedule automatic refresh if configured."""
        if self.config.auto_refresh_interval and self.config.auto_refresh_interval > 0:
            async def auto_refresh():
                while True:
                    await asyncio.sleep(self.config.auto_refresh_interval)
                    await self._async_refresh()
            
            if self._control and self._control.page:
                self._refresh_task = asyncio.create_task(auto_refresh())
    
    def build(self) -> ft.Control:
        """Build the dashboard."""
        theme = self.theme or DefaultTheme()
        dashboard_sections = []
        
        # Header
        if self.config.show_header:
            self._header_container = ft.Container(
                content=self._build_header(),
            )
            dashboard_sections.append(self._header_container)
            dashboard_sections.append(ft.Divider(color=theme.outline))
        
        # Stats section
        if self.config.show_stats:
            self._stats_container = ft.Container(
                content=self._build_stats(),
            )
            dashboard_sections.append(self._stats_container)
        
        # Quick actions section
        if self.config.show_quick_actions:
            self._actions_container = ft.Container(
                content=self._build_quick_actions(),
            )
            dashboard_sections.append(self._actions_container)
        
        # Custom sections
        for section in self.sections:
            dashboard_sections.append(section.build())
        
        # Main container
        self._control = ft.Container(
            content=ft.Column(
                controls=dashboard_sections,
                spacing=self.config.spacing * 2,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            padding=self.config.padding,
            expand=True,
            visible=self.config.visible,
            disabled=self.config.disabled,
        )
        
        return self._control
    
    def on_mount(self) -> None:
        """Called when dashboard is mounted."""
        # Load initial data
        if self._control and self._control.page:
            self._control.page.run_task(self.load_dashboard_data())
        
        # Set up auto refresh
        self._schedule_auto_refresh()
    
    def on_unmount(self) -> None:
        """Called when dashboard is unmounted."""
        # Cancel refresh task
        if self._refresh_task:
            self._refresh_task.cancel()


class SyncDashboard(BaseDashboard):
    """Synchronous dashboard implementation."""
    
    async def load_dashboard_data(self) -> None:
        """Default implementation - override in subclasses."""
        pass


class AsyncDashboard(BaseDashboard):
    """Asynchronous dashboard implementation with better concurrency."""
    
    async def load_dashboard_data(self) -> None:
        """Load all dashboard data concurrently."""
        tasks = []
        
        # Load stat data
        for stat in self.stat_cards:
            if hasattr(stat.data_provider, 'load_data'):
                tasks.append(stat.data_provider.load_data())
        
        # Run all tasks concurrently
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


# Helper functions for creating dashboards

def create_stats_dashboard(
    title: str,
    stats: List[StatCard],
    config: Optional[DashboardConfig] = None,
    **kwargs
) -> SyncDashboard:
    """Create a simple statistics dashboard."""
    if not config:
        config = DashboardConfig(title=title, show_quick_actions=False)
    
    dashboard = SyncDashboard(config=config)
    
    for stat in stats:
        dashboard.add_stat_card(stat)
    
    return dashboard


def create_admin_dashboard(
    title: str = "Dashboard Administrativo",
    stats: Optional[List[StatCard]] = None,
    actions: Optional[List[QuickAction]] = None,
    sections: Optional[List[Section]] = None,
    config: Optional[DashboardConfig] = None,
    **kwargs
) -> AsyncDashboard:
    """Create a full-featured admin dashboard."""
    if not config:
        config = DashboardConfig(
            title=title,
            show_refresh=True,
            auto_refresh_interval=300,  # 5 minutes
        )
    
    dashboard = AsyncDashboard(config=config)
    
    if stats:
        for stat in stats:
            dashboard.add_stat_card(stat)
    
    if actions:
        for action in actions:
            dashboard.add_quick_action(action)
    
    if sections:
        for section in sections:
            dashboard.add_section(section)
    
    return dashboard