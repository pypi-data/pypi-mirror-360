"""
Pagination components for essencia.

This module provides flexible pagination controls with support for:
- Multiple display modes (table, grid, list)
- Async data loading
- Custom data providers
- Theme-aware styling
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union
import math
import flet as ft

from .base import ThemedControl, ControlConfig, get_controls_config, DefaultTheme, DataProvider
from .buttons import ThemedIconButton, ThemedTextButton
from .inputs import ThemedDropdown
from .loading import LoadingIndicator


class PaginationMode(Enum):
    """Display modes for paginated data."""
    TABLE = "table"
    GRID = "grid"
    LIST = "list"
    CUSTOM = "custom"


@dataclass
class PaginationConfig:
    """Configuration for pagination behavior."""
    page_size: int = 10
    page_size_options: List[int] = None
    show_page_size_selector: bool = True
    show_info: bool = True
    show_first_last: bool = True
    show_prev_next: bool = True
    show_page_numbers: bool = True
    max_page_numbers: int = 5
    enable_keyboard_navigation: bool = True
    cache_pages: bool = True
    prefetch_pages: int = 1
    
    def __post_init__(self):
        if self.page_size_options is None:
            self.page_size_options = [10, 25, 50, 100]


class PaginationDataProvider(ABC):
    """Abstract base class for pagination data providers."""
    
    @abstractmethod
    async def get_items(self, 
                       page: int, 
                       page_size: int,
                       filters: Optional[Dict[str, Any]] = None,
                       sort: Optional[Dict[str, int]] = None) -> List[Any]:
        """Get items for a specific page."""
        pass
    
    @abstractmethod
    async def get_total_count(self,
                             filters: Optional[Dict[str, Any]] = None) -> int:
        """Get total number of items."""
        pass
    
    def get_page_count(self, total_count: int, page_size: int) -> int:
        """Calculate total number of pages."""
        return math.ceil(total_count / page_size)


class DefaultDataProvider(PaginationDataProvider):
    """Default data provider that works with the configured DataProvider."""
    
    def __init__(self, model_type: str, data_provider: Optional[DataProvider] = None):
        self.model_type = model_type
        self.data_provider = data_provider or get_controls_config().data_provider
    
    async def get_items(self, 
                       page: int, 
                       page_size: int,
                       filters: Optional[Dict[str, Any]] = None,
                       sort: Optional[Dict[str, int]] = None) -> List[Any]:
        """Get items using the configured data provider."""
        if not self.data_provider:
            return []
        
        skip = (page - 1) * page_size
        return await self.data_provider.get_items(
            model_type=self.model_type,
            filters=filters,
            skip=skip,
            limit=page_size,
            sort=sort
        )
    
    async def get_total_count(self,
                             filters: Optional[Dict[str, Any]] = None) -> int:
        """Get total count using the configured data provider."""
        if not self.data_provider:
            return 0
        
        return await self.data_provider.get_count(
            model_type=self.model_type,
            filters=filters
        )


class UnifiedPagination(ThemedControl):
    """Unified pagination component with multiple display modes."""
    
    def __init__(self,
                 data_provider: PaginationDataProvider,
                 display_mode: PaginationMode = PaginationMode.TABLE,
                 item_builder: Optional[Callable[[Any], ft.Control]] = None,
                 table_columns: Optional[List[ft.DataColumn]] = None,
                 table_row_builder: Optional[Callable[[Any], ft.DataRow]] = None,
                 grid_item_builder: Optional[Callable[[Any], ft.Control]] = None,
                 list_item_builder: Optional[Callable[[Any], ft.Control]] = None,
                 filters: Optional[Dict[str, Any]] = None,
                 sort: Optional[Dict[str, int]] = None,
                 on_page_change: Optional[Callable[[int], None]] = None,
                 on_page_size_change: Optional[Callable[[int], None]] = None,
                 on_item_click: Optional[Callable[[Any], None]] = None,
                 config: Optional[PaginationConfig] = None,
                 control_config: Optional[ControlConfig] = None):
        super().__init__(control_config)
        self.data_provider = data_provider
        self.display_mode = display_mode
        self.item_builder = item_builder
        self.table_columns = table_columns
        self.table_row_builder = table_row_builder
        self.grid_item_builder = grid_item_builder
        self.list_item_builder = list_item_builder
        self.filters = filters or {}
        self.sort = sort or {}
        self.on_page_change = on_page_change
        self.on_page_size_change = on_page_size_change
        self.on_item_click = on_item_click
        self.config = config or PaginationConfig()
        
        # State
        self.current_page = 1
        self.page_size = self.config.page_size
        self.total_count = 0
        self.page_count = 0
        self.items: List[Any] = []
        self.is_loading = False
        
        # Cache
        self._page_cache: Dict[int, List[Any]] = {}
        
        # Controls
        self._data_container: Optional[ft.Control] = None
        self._loading_overlay: Optional[ft.Control] = None
        self._info_text: Optional[ft.Text] = None
        self._pagination_controls: Optional[ft.Row] = None
    
    async def load_page(self, page: int) -> None:
        """Load data for a specific page."""
        if page < 1 or (self.page_count > 0 and page > self.page_count):
            return
        
        # Check cache
        if self.config.cache_pages and page in self._page_cache:
            self.items = self._page_cache[page]
            self.current_page = page
            self._update_display()
            return
        
        # Set loading state
        self.is_loading = True
        self._show_loading()
        
        try:
            # Get total count if not available
            if self.total_count == 0:
                self.total_count = await self.data_provider.get_total_count(self.filters)
                self.page_count = self.data_provider.get_page_count(self.total_count, self.page_size)
            
            # Load items
            self.items = await self.data_provider.get_items(
                page=page,
                page_size=self.page_size,
                filters=self.filters,
                sort=self.sort
            )
            
            # Cache page
            if self.config.cache_pages:
                self._page_cache[page] = self.items
            
            self.current_page = page
            
            # Prefetch adjacent pages
            if self.config.prefetch_pages > 0:
                await self._prefetch_pages()
            
            # Update display
            self._update_display()
            
            # Call user callback
            if self.on_page_change:
                self.on_page_change(page)
        
        finally:
            self.is_loading = False
            self._hide_loading()
    
    async def _prefetch_pages(self) -> None:
        """Prefetch adjacent pages for faster navigation."""
        prefetch_tasks = []
        
        for offset in range(1, self.config.prefetch_pages + 1):
            # Previous pages
            prev_page = self.current_page - offset
            if prev_page >= 1 and prev_page not in self._page_cache:
                prefetch_tasks.append(self._prefetch_page(prev_page))
            
            # Next pages
            next_page = self.current_page + offset
            if next_page <= self.page_count and next_page not in self._page_cache:
                prefetch_tasks.append(self._prefetch_page(next_page))
        
        # Run prefetch tasks concurrently
        if prefetch_tasks:
            import asyncio
            await asyncio.gather(*prefetch_tasks, return_exceptions=True)
    
    async def _prefetch_page(self, page: int) -> None:
        """Prefetch a single page."""
        try:
            items = await self.data_provider.get_items(
                page=page,
                page_size=self.page_size,
                filters=self.filters,
                sort=self.sort
            )
            self._page_cache[page] = items
        except Exception:
            pass  # Ignore prefetch errors
    
    def _show_loading(self) -> None:
        """Show loading indicator."""
        if self._loading_overlay:
            self._loading_overlay.visible = True
            self._loading_overlay.update()
    
    def _hide_loading(self) -> None:
        """Hide loading indicator."""
        if self._loading_overlay:
            self._loading_overlay.visible = False
            self._loading_overlay.update()
    
    def _update_display(self) -> None:
        """Update the data display based on current items."""
        if not self._data_container:
            return
        
        # Clear current content
        self._data_container.content = None
        
        # Build new content based on display mode
        if self.display_mode == PaginationMode.TABLE:
            self._data_container.content = self._build_table()
        elif self.display_mode == PaginationMode.GRID:
            self._data_container.content = self._build_grid()
        elif self.display_mode == PaginationMode.LIST:
            self._data_container.content = self._build_list()
        elif self.display_mode == PaginationMode.CUSTOM and self.item_builder:
            self._data_container.content = self._build_custom()
        
        # Update info text
        if self._info_text:
            start = (self.current_page - 1) * self.page_size + 1
            end = min(self.current_page * self.page_size, self.total_count)
            self._info_text.value = f"Mostrando {start}-{end} de {self.total_count}"
            self._info_text.update()
        
        # Update pagination controls
        self._update_pagination_controls()
        
        self._data_container.update()
    
    def _build_table(self) -> ft.Control:
        """Build table display."""
        if not self.table_columns:
            return ft.Text("No table columns defined")
        
        rows = []
        for item in self.items:
            if self.table_row_builder:
                row = self.table_row_builder(item)
            else:
                # Default row builder
                cells = []
                for col in self.table_columns:
                    value = getattr(item, col.label.lower(), "")
                    cells.append(ft.DataCell(ft.Text(str(value))))
                row = ft.DataRow(cells=cells)
            
            if self.on_item_click:
                row.on_select_changed = lambda e, item=item: self.on_item_click(item)
            
            rows.append(row)
        
        return ft.DataTable(
            columns=self.table_columns,
            rows=rows,
            border=ft.border.all(1, self.theme.outline if self.theme else DefaultTheme.outline),
            border_radius=get_controls_config().default_border_radius,
            heading_row_color=ft.colors.with_opacity(0.05, self.theme.primary if self.theme else DefaultTheme.primary),
        )
    
    def _build_grid(self) -> ft.Control:
        """Build grid display."""
        if not self.grid_item_builder:
            return ft.Text("No grid item builder defined")
        
        items = []
        for item in self.items:
            grid_item = self.grid_item_builder(item)
            if self.on_item_click:
                grid_item = ft.Container(
                    content=grid_item,
                    on_click=lambda e, item=item: self.on_item_click(item),
                )
            items.append(grid_item)
        
        return ft.GridView(
            controls=items,
            runs_count=3,  # Default to 3 columns
            spacing=get_controls_config().default_spacing,
            run_spacing=get_controls_config().default_spacing,
        )
    
    def _build_list(self) -> ft.Control:
        """Build list display."""
        if not self.list_item_builder:
            return ft.Text("No list item builder defined")
        
        items = []
        for item in self.items:
            list_item = self.list_item_builder(item)
            if self.on_item_click:
                list_item = ft.Container(
                    content=list_item,
                    on_click=lambda e, item=item: self.on_item_click(item),
                )
            items.append(list_item)
        
        return ft.Column(
            controls=items,
            spacing=get_controls_config().default_spacing,
            scroll=ft.ScrollMode.AUTO,
        )
    
    def _build_custom(self) -> ft.Control:
        """Build custom display using item_builder."""
        items = []
        for item in self.items:
            custom_item = self.item_builder(item)
            if self.on_item_click:
                custom_item = ft.Container(
                    content=custom_item,
                    on_click=lambda e, item=item: self.on_item_click(item),
                )
            items.append(custom_item)
        
        return ft.Column(
            controls=items,
            spacing=get_controls_config().default_spacing,
            scroll=ft.ScrollMode.AUTO,
        )
    
    def _update_pagination_controls(self) -> None:
        """Update pagination control states."""
        if not self._pagination_controls:
            return
        
        # Update button states
        for control in self._pagination_controls.controls:
            if hasattr(control, 'data'):
                if control.data == 'first' or control.data == 'prev':
                    control.disabled = self.current_page <= 1
                elif control.data == 'last' or control.data == 'next':
                    control.disabled = self.current_page >= self.page_count
                elif control.data == 'page_numbers':
                    # Update page number buttons
                    self._update_page_numbers(control)
        
        self._pagination_controls.update()
    
    def _update_page_numbers(self, container: ft.Container) -> None:
        """Update page number buttons."""
        if not self.config.show_page_numbers:
            return
        
        page_buttons = []
        
        # Calculate visible page range
        half_max = self.config.max_page_numbers // 2
        start_page = max(1, self.current_page - half_max)
        end_page = min(self.page_count, start_page + self.config.max_page_numbers - 1)
        
        # Adjust start if we're near the end
        if end_page - start_page + 1 < self.config.max_page_numbers:
            start_page = max(1, end_page - self.config.max_page_numbers + 1)
        
        # Add ellipsis at start
        if start_page > 1:
            page_buttons.append(ft.Text("...", color=self.theme.on_surface_variant if self.theme else DefaultTheme.on_surface_variant))
        
        # Add page number buttons
        for page in range(start_page, end_page + 1):
            btn = ThemedTextButton(
                text=str(page),
                on_click=lambda e, p=page: self._go_to_page(p),
            ).build()
            
            # Highlight current page
            if page == self.current_page:
                btn.style = ft.ButtonStyle(
                    bgcolor=self.theme.primary if self.theme else DefaultTheme.primary,
                    color=self.theme.on_primary if self.theme else DefaultTheme.on_primary,
                )
            
            page_buttons.append(btn)
        
        # Add ellipsis at end
        if end_page < self.page_count:
            page_buttons.append(ft.Text("...", color=self.theme.on_surface_variant if self.theme else DefaultTheme.on_surface_variant))
        
        container.content = ft.Row(
            controls=page_buttons,
            spacing=4,
        )
    
    def _go_to_page(self, page: int) -> None:
        """Navigate to a specific page."""
        if page != self.current_page and page >= 1 and page <= self.page_count:
            # Run async load in page's async context
            if hasattr(self._control, 'page') and self._control.page:
                self._control.page.run_task(self.load_page(page))
    
    def _change_page_size(self, e) -> None:
        """Handle page size change."""
        new_size = int(e.control.value)
        if new_size != self.page_size:
            self.page_size = new_size
            self.current_page = 1  # Reset to first page
            self._page_cache.clear()  # Clear cache
            
            # Recalculate page count
            if self.total_count > 0:
                self.page_count = self.data_provider.get_page_count(self.total_count, self.page_size)
            
            # Reload data
            if hasattr(self._control, 'page') and self._control.page:
                self._control.page.run_task(self.load_page(1))
            
            # Call user callback
            if self.on_page_size_change:
                self.on_page_size_change(new_size)
    
    def build(self) -> ft.Control:
        """Build the pagination component."""
        theme = self.theme or DefaultTheme()
        controls_config = get_controls_config()
        
        # Create data container
        self._data_container = ft.Container(
            expand=True,
            padding=controls_config.default_padding,
        )
        
        # Create loading overlay
        self._loading_overlay = ft.Container(
            content=LoadingIndicator().build(),
            alignment=ft.alignment.center,
            visible=False,
            expand=True,
            bgcolor=theme.surface + "CC",
        )
        
        # Create pagination controls
        pagination_controls = []
        
        # Page size selector
        if self.config.show_page_size_selector:
            page_size_dropdown = ThemedDropdown(
                label="Por página",
                value=str(self.page_size),
                options=[ft.dropdown.Option(str(size)) for size in self.config.page_size_options],
                on_change=self._change_page_size,
            ).build()
            page_size_dropdown.width = 100
            pagination_controls.append(page_size_dropdown)
        
        # Info text
        if self.config.show_info:
            self._info_text = ft.Text(
                "Carregando...",
                color=theme.on_surface_variant,
                size=14,
            )
            pagination_controls.append(self._info_text)
        
        # Navigation controls
        nav_controls = []
        
        # First button
        if self.config.show_first_last:
            first_btn = ThemedIconButton(
                icon=ft.Icons.FIRST_PAGE,
                on_click=lambda e: self._go_to_page(1),
                tooltip="Primeira página",
            ).build()
            first_btn.data = 'first'
            nav_controls.append(first_btn)
        
        # Previous button
        if self.config.show_prev_next:
            prev_btn = ThemedIconButton(
                icon=ft.Icons.CHEVRON_LEFT,
                on_click=lambda e: self._go_to_page(self.current_page - 1),
                tooltip="Página anterior",
            ).build()
            prev_btn.data = 'prev'
            nav_controls.append(prev_btn)
        
        # Page numbers container
        if self.config.show_page_numbers:
            page_numbers_container = ft.Container(data='page_numbers')
            nav_controls.append(page_numbers_container)
        
        # Next button
        if self.config.show_prev_next:
            next_btn = ThemedIconButton(
                icon=ft.Icons.CHEVRON_RIGHT,
                on_click=lambda e: self._go_to_page(self.current_page + 1),
                tooltip="Próxima página",
            ).build()
            next_btn.data = 'next'
            nav_controls.append(next_btn)
        
        # Last button
        if self.config.show_first_last:
            last_btn = ThemedIconButton(
                icon=ft.Icons.LAST_PAGE,
                on_click=lambda e: self._go_to_page(self.page_count),
                tooltip="Última página",
            ).build()
            last_btn.data = 'last'
            nav_controls.append(last_btn)
        
        pagination_controls.extend(nav_controls)
        
        self._pagination_controls = ft.Row(
            controls=pagination_controls,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=controls_config.default_spacing,
        )
        
        # Main container
        self._control = ft.Column(
            controls=[
                ft.Stack(
                    controls=[
                        self._data_container,
                        self._loading_overlay,
                    ],
                    expand=True,
                ),
                ft.Divider(color=theme.outline),
                self._pagination_controls,
            ],
            spacing=controls_config.default_spacing,
            expand=True,
            visible=self.config.visible,
            disabled=self.config.disabled,
        )
        
        # Set up keyboard navigation
        if self.config.enable_keyboard_navigation:
            self._setup_keyboard_navigation()
        
        return self._control
    
    def _setup_keyboard_navigation(self) -> None:
        """Set up keyboard navigation shortcuts."""
        # This would need to be implemented with page-level keyboard handlers
        pass


# Helper functions for creating common pagination configurations

def create_table_pagination(
    data_provider: Union[PaginationDataProvider, str],
    columns: List[ft.DataColumn],
    row_builder: Optional[Callable[[Any], ft.DataRow]] = None,
    **kwargs
) -> UnifiedPagination:
    """Create a table-based pagination component."""
    if isinstance(data_provider, str):
        data_provider = DefaultDataProvider(data_provider)
    
    return UnifiedPagination(
        data_provider=data_provider,
        display_mode=PaginationMode.TABLE,
        table_columns=columns,
        table_row_builder=row_builder,
        **kwargs
    )


def create_grid_pagination(
    data_provider: Union[PaginationDataProvider, str],
    item_builder: Callable[[Any], ft.Control],
    **kwargs
) -> UnifiedPagination:
    """Create a grid-based pagination component."""
    if isinstance(data_provider, str):
        data_provider = DefaultDataProvider(data_provider)
    
    return UnifiedPagination(
        data_provider=data_provider,
        display_mode=PaginationMode.GRID,
        grid_item_builder=item_builder,
        **kwargs
    )


def create_list_pagination(
    data_provider: Union[PaginationDataProvider, str],
    item_builder: Callable[[Any], ft.Control],
    **kwargs
) -> UnifiedPagination:
    """Create a list-based pagination component."""
    if isinstance(data_provider, str):
        data_provider = DefaultDataProvider(data_provider)
    
    return UnifiedPagination(
        data_provider=data_provider,
        display_mode=PaginationMode.LIST,
        list_item_builder=item_builder,
        **kwargs
    )