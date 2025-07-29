"""
Lazy loading components for essencia.

This module provides components that load data asynchronously
and display loading states while fetching.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union
import asyncio
import flet as ft

from .base import ThemedControl, ControlConfig, get_controls_config, DefaultTheme, DataProvider
from .loading import LoadingIndicator, SkeletonLoader
from .layout import Panel


class AsyncDataProvider(ABC):
    """Abstract base class for async data providers."""
    
    @abstractmethod
    async def load_data(self) -> Any:
        """Load data asynchronously."""
        pass
    
    async def refresh_data(self) -> Any:
        """Refresh data (by default calls load_data)."""
        return await self.load_data()


class LazyLoadWidget(ThemedControl):
    """Base class for lazy loading widgets."""
    
    def __init__(self,
                 data_provider: Optional[AsyncDataProvider] = None,
                 on_error: Optional[Callable[[Exception], None]] = None,
                 error_message: str = "Erro ao carregar dados",
                 retry_message: str = "Tentar novamente",
                 show_refresh_button: bool = True,
                 auto_refresh_interval: Optional[int] = None,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.data_provider = data_provider
        self.on_error = on_error
        self.error_message = error_message
        self.retry_message = retry_message
        self.show_refresh_button = show_refresh_button
        self.auto_refresh_interval = auto_refresh_interval
        
        # State
        self.is_loading = True
        self.has_error = False
        self.error: Optional[Exception] = None
        self.data: Any = None
        
        # Controls
        self._container: Optional[ft.Container] = None
        self._refresh_task: Optional[asyncio.Task] = None
    
    async def load_data(self) -> None:
        """Load data from the provider."""
        if not self.data_provider:
            return
        
        self.is_loading = True
        self.has_error = False
        self._update_display()
        
        try:
            self.data = await self.data_provider.load_data()
            self.is_loading = False
            self._update_display()
            
            # Schedule auto refresh if enabled
            if self.auto_refresh_interval and self.auto_refresh_interval > 0:
                self._schedule_refresh()
        
        except Exception as e:
            self.is_loading = False
            self.has_error = True
            self.error = e
            self._update_display()
            
            if self.on_error:
                self.on_error(e)
    
    async def refresh(self) -> None:
        """Refresh the data."""
        await self.load_data()
    
    def _schedule_refresh(self) -> None:
        """Schedule automatic refresh."""
        if self._refresh_task:
            self._refresh_task.cancel()
        
        async def auto_refresh():
            await asyncio.sleep(self.auto_refresh_interval)
            if self._container and self._container.page:
                await self.refresh()
        
        if self._container and self._container.page:
            self._refresh_task = asyncio.create_task(auto_refresh())
    
    def _update_display(self) -> None:
        """Update the display based on current state."""
        if not self._container:
            return
        
        if self.is_loading:
            self._container.content = self._build_loading()
        elif self.has_error:
            self._container.content = self._build_error()
        else:
            self._container.content = self._build_content()
        
        self._container.update()
    
    def _build_loading(self) -> ft.Control:
        """Build loading state display."""
        return ft.Column(
            controls=[LoadingIndicator().build()],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True,
        )
    
    def _build_error(self) -> ft.Control:
        """Build error state display."""
        theme = self.theme or DefaultTheme()
        
        controls = [
            ft.Icon(
                ft.Icons.ERROR_OUTLINE,
                size=48,
                color=theme.error,
            ),
            ft.Text(
                self.error_message,
                size=16,
                color=theme.on_surface,
                text_align=ft.TextAlign.CENTER,
            ),
        ]
        
        if self.error:
            controls.append(
                ft.Text(
                    str(self.error),
                    size=12,
                    color=theme.on_surface_variant,
                    text_align=ft.TextAlign.CENTER,
                )
            )
        
        controls.append(
            ft.TextButton(
                text=self.retry_message,
                on_click=lambda e: self._retry(),
            )
        )
        
        return ft.Column(
            controls=controls,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=get_controls_config().default_spacing,
            expand=True,
        )
    
    def _retry(self) -> None:
        """Retry loading data."""
        if self._container and self._container.page:
            self._container.page.run_task(self.load_data())
    
    def _build_content(self) -> ft.Control:
        """Build content display (to be overridden by subclasses)."""
        return ft.Text("No content builder defined")
    
    def build(self) -> ft.Control:
        """Build the lazy load widget."""
        self._container = ft.Container(
            expand=True,
            visible=self.config.visible,
            disabled=self.config.disabled,
        )
        
        # Add refresh button if enabled
        if self.show_refresh_button:
            refresh_button = ft.IconButton(
                icon=ft.Icons.REFRESH,
                tooltip="Atualizar",
                on_click=lambda e: self._retry(),
            )
            
            self._control = ft.Stack(
                controls=[
                    self._container,
                    ft.Container(
                        content=refresh_button,
                        alignment=ft.alignment.top_right,
                        padding=get_controls_config().default_padding,
                    ),
                ],
                expand=True,
            )
        else:
            self._control = self._container
        
        # Set up initial loading
        self._container.content = self._build_loading()
        
        return self._control
    
    def on_mount(self) -> None:
        """Called when the widget is mounted to the page."""
        if self._container and self._container.page:
            self._container.page.run_task(self.load_data())


class LazyDataWidget(LazyLoadWidget):
    """Generic lazy loading widget with custom content builder."""
    
    def __init__(self,
                 data_provider: AsyncDataProvider,
                 content_builder: Callable[[Any], ft.Control],
                 **kwargs):
        super().__init__(data_provider=data_provider, **kwargs)
        self.content_builder = content_builder
    
    def _build_content(self) -> ft.Control:
        """Build content using the provided builder."""
        if self.data is not None:
            return self.content_builder(self.data)
        return ft.Text("Nenhum dado disponível")


class LazyStatsWidget(LazyLoadWidget):
    """Lazy loading widget for displaying statistics."""
    
    def __init__(self,
                 title: str,
                 data_provider: AsyncDataProvider,
                 stat_formatter: Optional[Callable[[Any], str]] = None,
                 icon: Optional[str] = None,
                 color: Optional[str] = None,
                 **kwargs):
        super().__init__(data_provider=data_provider, **kwargs)
        self.title = title
        self.stat_formatter = stat_formatter or str
        self.icon = icon
        self.color = color
    
    def _build_loading(self) -> ft.Control:
        """Build loading state with skeleton."""
        return ft.Column(
            controls=[
                SkeletonLoader(width=100, height=16).build(),
                ft.Container(height=8),
                SkeletonLoader(width=60, height=32).build(),
            ],
            spacing=4,
        )
    
    def _build_content(self) -> ft.Control:
        """Build statistics display."""
        theme = self.theme or DefaultTheme()
        
        controls = []
        
        if self.icon:
            controls.append(
                ft.Icon(
                    self.icon,
                    size=24,
                    color=self.color or theme.primary,
                )
            )
        
        controls.extend([
            ft.Text(
                self.title,
                size=14,
                color=theme.on_surface_variant,
            ),
            ft.Text(
                self.stat_formatter(self.data),
                size=24,
                weight=ft.FontWeight.BOLD,
                color=self.color or theme.on_surface,
            ),
        ])
        
        return ft.Column(
            controls=controls,
            spacing=get_controls_config().default_spacing // 2,
        )


class LazyListWidget(LazyLoadWidget):
    """Lazy loading widget for displaying lists."""
    
    def __init__(self,
                 title: str,
                 data_provider: AsyncDataProvider,
                 item_builder: Callable[[Any], ft.Control],
                 empty_message: str = "Nenhum item encontrado",
                 max_items: Optional[int] = None,
                 **kwargs):
        super().__init__(data_provider=data_provider, **kwargs)
        self.title = title
        self.item_builder = item_builder
        self.empty_message = empty_message
        self.max_items = max_items
    
    def _build_loading(self) -> ft.Control:
        """Build loading state with skeleton list."""
        skeletons = []
        for _ in range(3):  # Show 3 skeleton items
            skeletons.append(SkeletonLoader(height=60).build())
        
        return ft.Column(
            controls=skeletons,
            spacing=get_controls_config().default_spacing,
        )
    
    def _build_content(self) -> ft.Control:
        """Build list display."""
        theme = self.theme or DefaultTheme()
        
        if not self.data or len(self.data) == 0:
            return ft.Container(
                content=ft.Text(
                    self.empty_message,
                    color=theme.on_surface_variant,
                    text_align=ft.TextAlign.CENTER,
                ),
                alignment=ft.alignment.center,
                padding=get_controls_config().default_padding * 2,
            )
        
        # Build list items
        items = []
        data_to_show = self.data[:self.max_items] if self.max_items else self.data
        
        for item in data_to_show:
            items.append(self.item_builder(item))
        
        # Add "show more" if truncated
        if self.max_items and len(self.data) > self.max_items:
            items.append(
                ft.TextButton(
                    text=f"Ver todos ({len(self.data)} itens)",
                    on_click=lambda e: None,  # To be implemented
                )
            )
        
        return ft.Column(
            controls=items,
            spacing=get_controls_config().default_spacing,
            scroll=ft.ScrollMode.AUTO,
        )


class LazyGridWidget(LazyLoadWidget):
    """Lazy loading widget for displaying grids."""
    
    def __init__(self,
                 data_provider: AsyncDataProvider,
                 item_builder: Callable[[Any], ft.Control],
                 columns: int = 3,
                 empty_message: str = "Nenhum item encontrado",
                 **kwargs):
        super().__init__(data_provider=data_provider, **kwargs)
        self.item_builder = item_builder
        self.columns = columns
        self.empty_message = empty_message
    
    def _build_loading(self) -> ft.Control:
        """Build loading state with skeleton grid."""
        skeletons = []
        for _ in range(6):  # Show 6 skeleton items
            skeletons.append(
                SkeletonLoader(
                    height=120,
                    border_radius=get_controls_config().default_border_radius,
                ).build()
            )
        
        return ft.GridView(
            controls=skeletons,
            runs_count=self.columns,
            spacing=get_controls_config().default_spacing,
            run_spacing=get_controls_config().default_spacing,
        )
    
    def _build_content(self) -> ft.Control:
        """Build grid display."""
        theme = self.theme or DefaultTheme()
        
        if not self.data or len(self.data) == 0:
            return ft.Container(
                content=ft.Text(
                    self.empty_message,
                    color=theme.on_surface_variant,
                    text_align=ft.TextAlign.CENTER,
                ),
                alignment=ft.alignment.center,
                padding=get_controls_config().default_padding * 2,
            )
        
        # Build grid items
        items = []
        for item in self.data:
            items.append(self.item_builder(item))
        
        return ft.GridView(
            controls=items,
            runs_count=self.columns,
            spacing=get_controls_config().default_spacing,
            run_spacing=get_controls_config().default_spacing,
            expand=True,
        )