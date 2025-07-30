"""
Unified Pagination System - Standardized pagination for all list views.

Provides consistent pagination experience across applications with
multiple display modes, responsive design, and async data loading.
"""

import logging
import math
from typing import Dict, List, Any, Optional, Callable, Union, TypeVar, Generic
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum

import flet as ft

from ..themes import ThemedComponent, get_theme_from_page
from ..feedback import LoadingIndicator, LoadingSize

logger = logging.getLogger(__name__)

T = TypeVar('T')


class PaginationMode(Enum):
    """Pagination display modes."""
    FULL = "full"  # Full pagination with all controls
    COMPACT = "compact"  # Compact pagination for mobile
    SIMPLE = "simple"  # Simple next/prev buttons only
    INFINITE = "infinite"  # Infinite scroll (integrates with lazy loading)


@dataclass
class PaginationConfig:
    """Configuration for pagination behavior."""
    page_size: int = 20  # Items per page
    max_visible_pages: int = 5  # Maximum page buttons to show
    mode: PaginationMode = PaginationMode.FULL
    show_size_selector: bool = True  # Allow user to change page size
    show_page_info: bool = True  # Show "Page X of Y" info
    show_total_count: bool = True  # Show total item count
    enable_jump_to_page: bool = True  # Allow direct page number input
    size_options: List[int] = field(default_factory=lambda: [10, 20, 50, 100])
    load_more_threshold: float = 0.8  # Scroll threshold for infinite mode (0.0-1.0)
    debounce_scroll: int = 300  # Debounce scroll events (ms)


class PaginationDataProvider(ABC, Generic[T]):
    """Abstract base class for pagination data providers."""
    
    @abstractmethod
    async def get_page_data(
        self,
        page: int,
        page_size: int,
        search_query: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """
        Get data for a specific page.
        
        Args:
            page: Page number (0-based)
            page_size: Number of items per page
            search_query: Optional search query
            filters: Optional filters
            sort_by: Optional sort field
            sort_order: Sort order ("asc" or "desc")
            
        Returns:
            Dictionary with:
            - 'items': List of data items
            - 'total_count': Total number of items available
            - 'page': Current page number
            - 'has_next': Whether there's a next page
            - 'has_previous': Whether there's a previous page
        """
        pass
    
    @abstractmethod
    def create_item_widget(self, item: T, index: int) -> ft.Control:
        """
        Create a widget for a data item.
        
        Args:
            item: The data item
            index: The item index in the current page
            
        Returns:
            Flet control representing the item
        """
        pass
    
    def create_empty_state(self) -> Optional[ft.Control]:
        """Create widget to show when no items are found."""
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.INBOX, size=48, color=ft.Colors.ON_SURFACE_VARIANT),
                ft.Text(
                    "No items found",
                    size=16,
                    color=ft.Colors.ON_SURFACE_VARIANT
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=40,
            alignment=ft.alignment.center
        )


class UnifiedPagination(ft.UserControl, ThemedComponent):
    """
    Unified pagination component that provides consistent pagination UX.
    
    Features:
    - Multiple display modes (full, compact, simple, infinite)
    - Configurable page sizes
    - Jump to page functionality
    - Integration with search and filters
    - Responsive design
    - Accessibility support
    - Theme awareness
    
    Example:
        ```python
        class UserDataProvider(PaginationDataProvider[User]):
            async def get_page_data(self, page, page_size, **kwargs):
                # Load users from API
                return await api.get_users(
                    offset=page * page_size,
                    limit=page_size,
                    **kwargs
                )
                
            def create_item_widget(self, user, index):
                return ft.ListTile(
                    leading=ft.CircleAvatar(content=ft.Text(user.initials)),
                    title=ft.Text(user.name),
                    subtitle=ft.Text(user.email)
                )
        
        pagination = UnifiedPagination(
            data_provider=UserDataProvider(),
            config=PaginationConfig(mode=PaginationMode.FULL),
            on_item_click=lambda user: show_user_details(user)
        )
        ```
    """
    
    def __init__(
        self,
        data_provider: PaginationDataProvider[T],
        config: Optional[PaginationConfig] = None,
        on_item_click: Optional[Callable[[T], None]] = None,
        on_page_change: Optional[Callable[[int, int, int], None]] = None,
        **kwargs
    ):
        ThemedComponent.__init__(self)
        super().__init__(**kwargs)
        
        self.data_provider = data_provider
        self.config = config or PaginationConfig()
        self.on_item_click = on_item_click
        self.on_page_change = on_page_change
        
        # State management
        self.current_page = 0
        self.total_count = 0
        self.total_pages = 0
        self.has_next = False
        self.has_previous = False
        self.items: List[T] = []
        self.loading = False
        self.error_message: Optional[str] = None
        self.search_query: Optional[str] = None
        self.filters: Dict[str, Any] = {}
        self.sort_by: Optional[str] = None
        self.sort_order: str = "asc"
        
        # UI Components
        self.items_container: Optional[ft.Control] = None
        self.pagination_controls: Optional[ft.Container] = None
        self.loading_indicator: Optional[ft.Row] = None
        self.error_container: Optional[ft.Container] = None
        self.empty_state: Optional[ft.Container] = None
        
        # Scroll handling for infinite mode
        self._scroll_timer = None
        self._last_scroll_time = 0
    
    def build(self):
        """Build the unified pagination UI."""
        # Create components
        self._create_components()
        
        controls = []
        
        # Main content area
        content_stack = ft.Stack([
            # Items container
            ft.Container(
                content=self.items_container,
                expand=True,
                visible=True
            ),
            
            # Loading overlay
            ft.Container(
                content=self.loading_indicator,
                bgcolor=ft.Colors.with_opacity(0.9, self.surface_color),
                visible=False,
                expand=True,
                alignment=ft.alignment.center
            ),
            
            # Error container
            ft.Container(
                content=self.error_container,
                visible=False,
                expand=True,
                alignment=ft.alignment.center
            ),
            
            # Empty state
            ft.Container(
                content=self.empty_state,
                visible=False,
                expand=True,
                alignment=ft.alignment.center
            )
        ], expand=True)
        
        controls.append(content_stack)
        
        # Pagination controls (except for infinite mode)
        if self.config.mode != PaginationMode.INFINITE:
            controls.append(self.pagination_controls)
        
        return ft.Column(controls, expand=True, spacing=0)
    
    def _create_components(self):
        """Create UI components."""
        # Items container
        if self.config.mode == PaginationMode.INFINITE:
            # Use ListView for infinite scroll
            self.items_container = ft.ListView(
                expand=True,
                spacing=0,
                padding=ft.padding.all(0),
                on_scroll=self._on_scroll
            )
        else:
            # Use Column for paginated display
            self.items_container = ft.Column(
                spacing=0,
                scroll=ft.ScrollMode.AUTO,
                expand=True
            )
        
        # Pagination controls
        self.pagination_controls = ft.Container(
            content=self._build_pagination_controls(),
            padding=ft.padding.symmetric(vertical=10, horizontal=15),
            bgcolor=self.surface_color,
            border=ft.border.only(top=ft.BorderSide(1, self.outline_color))
        )
        
        # Loading indicator
        self.loading_indicator = ft.Row([
            LoadingIndicator(size=LoadingSize.MEDIUM),
            ft.Text("Loading...", size=14, color=self.on_surface_variant_color)
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        # Error container
        self.error_container = ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR, size=48, color=self.error_color),
                ft.Text(
                    "Error loading data",
                    size=16,
                    color=self.error_color,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    "",  # Error message will be set dynamically
                    size=12,
                    color=self.on_surface_variant_color,
                    text_align=ft.TextAlign.CENTER
                ),
                ft.ElevatedButton(
                    "Retry",
                    on_click=lambda e: self.page.run_task(self.refresh)
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=ft.padding.all(40)
        )
        
        # Empty state
        self.empty_state = self.data_provider.create_empty_state() or ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.INBOX, size=48, color=self.on_surface_variant_color),
                ft.Text(
                    "No items found",
                    size=16,
                    color=self.on_surface_variant_color
                )
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=40
        )
    
    def _build_pagination_controls(self) -> ft.Control:
        """Build pagination controls based on mode."""
        if self.config.mode == PaginationMode.SIMPLE:
            return self._build_simple_controls()
        elif self.config.mode == PaginationMode.COMPACT:
            return self._build_compact_controls()
        else:  # FULL mode
            return self._build_full_controls()
    
    def _build_simple_controls(self) -> ft.Control:
        """Build simple next/prev controls."""
        return ft.Row([
            # Previous button
            ft.ElevatedButton(
                "Previous",
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda e: self.page.run_task(self._go_to_previous_page),
                disabled=not self.has_previous
            ),
            
            # Page info
            ft.Text(
                f"Page {self.current_page + 1} of {self.total_pages}",
                size=14,
                color=self.on_surface_variant_color
            ) if self.config.show_page_info else ft.Container(),
            
            # Next button
            ft.ElevatedButton(
                "Next",
                icon=ft.Icons.ARROW_FORWARD,
                on_click=lambda e: self.page.run_task(self._go_to_next_page),
                disabled=not self.has_next
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    
    def _build_compact_controls(self) -> ft.Control:
        """Build compact controls for mobile."""
        controls = []
        
        # Navigation row
        nav_controls = [
            ft.IconButton(
                icon=ft.Icons.FIRST_PAGE,
                tooltip="First page",
                on_click=lambda e: self.page.run_task(self._go_to_page(0)),
                disabled=not self.has_previous
            ),
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                tooltip="Previous page",
                on_click=lambda e: self.page.run_task(self._go_to_previous_page),
                disabled=not self.has_previous
            ),
            
            # Page display
            ft.Container(
                content=ft.Text(
                    f"{self.current_page + 1} / {self.total_pages}",
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color=self.on_surface_color
                ),
                padding=ft.padding.symmetric(horizontal=10)
            ),
            
            ft.IconButton(
                icon=ft.Icons.ARROW_FORWARD,
                tooltip="Next page",
                on_click=lambda e: self.page.run_task(self._go_to_next_page),
                disabled=not self.has_next
            ),
            ft.IconButton(
                icon=ft.Icons.LAST_PAGE,
                tooltip="Last page",
                on_click=lambda e: self.page.run_task(self._go_to_page(self.total_pages - 1)),
                disabled=not self.has_next
            )
        ]
        
        controls.append(ft.Row(
            nav_controls,
            alignment=ft.MainAxisAlignment.CENTER
        ))
        
        # Info row
        if self.config.show_total_count:
            controls.append(ft.Text(
                f"{self.total_count} items total",
                size=12,
                color=self.on_surface_variant_color,
                text_align=ft.TextAlign.CENTER
            ))
        
        return ft.Column(controls, spacing=5)
    
    def _build_full_controls(self) -> ft.Control:
        """Build full pagination controls."""
        controls = []
        
        # Top row: Page size selector and info
        if self.config.show_size_selector or self.config.show_total_count:
            top_controls = []
            
            # Page size selector
            if self.config.show_size_selector:
                top_controls.append(ft.Row([
                    ft.Text("Items per page:", size=12, color=self.on_surface_variant_color),
                    ft.Dropdown(
                        value=str(self.config.page_size),
                        options=[
                            ft.dropdown.Option(key=str(size), text=str(size))
                            for size in self.config.size_options
                        ],
                        width=80,
                        height=35,
                        text_size=12,
                        on_change=self._on_page_size_change
                    )
                ], spacing=10))
            
            # Total count info
            if self.config.show_total_count and self.total_count > 0:
                start_item = self.current_page * self.config.page_size + 1
                end_item = min((self.current_page + 1) * self.config.page_size, self.total_count)
                
                top_controls.append(ft.Text(
                    f"Showing {start_item}-{end_item} of {self.total_count} items",
                    size=12,
                    color=self.on_surface_variant_color
                ))
            
            controls.append(ft.Row(
                top_controls,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ))
        
        # Main pagination row
        pagination_controls = []
        
        # First page button
        pagination_controls.append(ft.IconButton(
            icon=ft.Icons.FIRST_PAGE,
            tooltip="First page",
            on_click=lambda e: self.page.run_task(self._go_to_page(0)),
            disabled=not self.has_previous
        ))
        
        # Previous button
        pagination_controls.append(ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            tooltip="Previous page",
            on_click=lambda e: self.page.run_task(self._go_to_previous_page),
            disabled=not self.has_previous
        ))
        
        # Page number buttons
        page_buttons = self._create_page_buttons()
        pagination_controls.extend(page_buttons)
        
        # Next button
        pagination_controls.append(ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD,
            tooltip="Next page",
            on_click=lambda e: self.page.run_task(self._go_to_next_page),
            disabled=not self.has_next
        ))
        
        # Last page button
        pagination_controls.append(ft.IconButton(
            icon=ft.Icons.LAST_PAGE,
            tooltip="Last page",
            on_click=lambda e: self.page.run_task(self._go_to_page(self.total_pages - 1)),
            disabled=not self.has_next
        ))
        
        # Jump to page (if enabled)
        if self.config.enable_jump_to_page and self.total_pages > self.config.max_visible_pages:
            pagination_controls.extend([
                ft.VerticalDivider(width=1),
                ft.Text("Go to:", size=12, color=self.on_surface_variant_color),
                ft.TextField(
                    hint_text="Page",
                    width=60,
                    height=35,
                    text_size=12,
                    on_submit=self._on_jump_to_page
                )
            ])
        
        controls.append(ft.Row(
            pagination_controls,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5
        ))
        
        return ft.Column(controls, spacing=10)
    
    def _create_page_buttons(self) -> List[ft.Control]:
        """Create page number buttons."""
        if self.total_pages <= 1:
            return []
        
        buttons = []
        max_visible = self.config.max_visible_pages
        
        # Calculate visible page range
        if self.total_pages <= max_visible:
            start_page = 0
            end_page = self.total_pages
        else:
            # Center the current page in the visible range
            half_visible = max_visible // 2
            start_page = max(0, self.current_page - half_visible)
            end_page = min(self.total_pages, start_page + max_visible)
            
            # Adjust if we're at the end
            if end_page - start_page < max_visible:
                start_page = max(0, end_page - max_visible)
        
        # Add ellipsis if needed (start)
        if start_page > 0:
            buttons.append(ft.TextButton(
                "1",
                on_click=lambda e: self.page.run_task(self._go_to_page(0))
            ))
            if start_page > 1:
                buttons.append(ft.Text("...", size=12, color=self.on_surface_variant_color))
        
        # Add page buttons
        for page in range(start_page, end_page):
            is_current = page == self.current_page
            buttons.append(ft.TextButton(
                str(page + 1),
                style=ft.ButtonStyle(
                    bgcolor=self.primary_color if is_current else None,
                    color=ft.Colors.ON_PRIMARY if is_current else self.on_surface_color
                ),
                on_click=lambda e, p=page: self.page.run_task(self._go_to_page(p))
            ))
        
        # Add ellipsis if needed (end)
        if end_page < self.total_pages:
            if end_page < self.total_pages - 1:
                buttons.append(ft.Text("...", size=12, color=self.on_surface_variant_color))
            buttons.append(ft.TextButton(
                str(self.total_pages),
                on_click=lambda e: self.page.run_task(self._go_to_page(self.total_pages - 1))
            ))
        
        return buttons
    
    def did_mount(self):
        """Initialize component when mounted."""
        super().did_mount()
        
        if self.page:
            self.page.run_task(self._load_initial_data)
    
    async def _load_initial_data(self):
        """Load initial page of data."""
        await self._load_page_data(0)
    
    async def _load_page_data(self, page: int):
        """Load data for a specific page."""
        if self.loading:
            return
        
        try:
            self.loading = True
            self._update_loading_state(True)
            
            # Load data from provider
            result = await self.data_provider.get_page_data(
                page=page,
                page_size=self.config.page_size,
                search_query=self.search_query,
                filters=self.filters,
                sort_by=self.sort_by,
                sort_order=self.sort_order
            )
            
            # Update state
            self.items = result.get('items', [])
            self.current_page = result.get('page', page)
            self.total_count = result.get('total_count', 0)
            self.total_pages = max(1, math.ceil(self.total_count / self.config.page_size)) if self.total_count > 0 else 1
            self.has_next = result.get('has_next', False)
            self.has_previous = result.get('has_previous', False)
            
            # Update UI
            self._update_items_display()
            self._update_pagination_controls()
            self._clear_error()
            self._update_empty_state()
            
            # Call page change callback
            if self.on_page_change:
                self.on_page_change(self.current_page, self.total_pages, self.total_count)
            
            logger.info(f"Loaded page {page + 1}/{self.total_pages} ({len(self.items)} items)")
            
        except Exception as e:
            logger.error(f"Error loading page data: {e}", exc_info=True)
            self._show_error(str(e))
        
        finally:
            self.loading = False
            self._update_loading_state(False)
    
    def _update_items_display(self):
        """Update the items display."""
        if not self.items_container:
            return
            
        if self.config.mode == PaginationMode.INFINITE:
            # For infinite scroll, append items
            for i, item in enumerate(self.items):
                item_widget = self.data_provider.create_item_widget(
                    item,
                    self.current_page * self.config.page_size + i
                )
                
                # Wrap in container for click handling
                if self.on_item_click:
                    container = ft.Container(
                        content=item_widget,
                        on_click=lambda e, item=item: self.on_item_click(item),
                        ink=True
                    )
                    self.items_container.controls.append(container)
                else:
                    self.items_container.controls.append(item_widget)
        else:
            # For paginated display, replace items
            self.items_container.controls.clear()
            
            for i, item in enumerate(self.items):
                item_widget = self.data_provider.create_item_widget(
                    item,
                    self.current_page * self.config.page_size + i
                )
                
                # Wrap in container for click handling
                if self.on_item_click:
                    container = ft.Container(
                        content=item_widget,
                        on_click=lambda e, item=item: self.on_item_click(item),
                        ink=True
                    )
                    self.items_container.controls.append(container)
                else:
                    self.items_container.controls.append(item_widget)
        
        self.update()
    
    def _update_pagination_controls(self):
        """Update pagination controls."""
        if self.config.mode != PaginationMode.INFINITE and self.pagination_controls:
            # Rebuild pagination controls with updated state
            self.pagination_controls.content = self._build_pagination_controls()
            self.update()
    
    def _update_loading_state(self, loading: bool):
        """Update loading indicator visibility."""
        # Find containers in stack
        if self.controls and len(self.controls) > 0:
            stack = self.controls[0]
            if isinstance(stack, ft.Stack) and len(stack.controls) >= 2:
                stack.controls[1].visible = loading  # Loading overlay
        self.update()
    
    def _show_error(self, message: str):
        """Show error state."""
        self.error_message = message
        if self.error_container and hasattr(self.error_container.content, 'controls'):
            controls = self.error_container.content.controls
            if len(controls) >= 3:
                controls[2].value = message
        
        # Update visibility
        if self.controls and len(self.controls) > 0:
            stack = self.controls[0]
            if isinstance(stack, ft.Stack) and len(stack.controls) >= 3:
                stack.controls[0].visible = False  # Items
                stack.controls[2].visible = True   # Error
        self.update()
    
    def _clear_error(self):
        """Clear error state."""
        self.error_message = None
        if self.controls and len(self.controls) > 0:
            stack = self.controls[0]
            if isinstance(stack, ft.Stack) and len(stack.controls) >= 3:
                stack.controls[0].visible = True   # Items
                stack.controls[2].visible = False  # Error
        self.update()
    
    def _update_empty_state(self):
        """Update empty state visibility."""
        is_empty = len(self.items) == 0 and not self.loading and not self.error_message
        
        if self.controls and len(self.controls) > 0:
            stack = self.controls[0]
            if isinstance(stack, ft.Stack) and len(stack.controls) >= 4:
                stack.controls[0].visible = not is_empty  # Items
                stack.controls[3].visible = is_empty      # Empty state
        self.update()
    
    # Event handlers
    
    async def _go_to_page(self, page: int):
        """Navigate to a specific page."""
        if 0 <= page < self.total_pages and page != self.current_page:
            await self._load_page_data(page)
    
    async def _go_to_next_page(self):
        """Navigate to next page."""
        if self.has_next:
            await self._go_to_page(self.current_page + 1)
    
    async def _go_to_previous_page(self):
        """Navigate to previous page."""
        if self.has_previous:
            await self._go_to_page(self.current_page - 1)
    
    def _on_page_size_change(self, e):
        """Handle page size change."""
        new_page_size = int(e.control.value)
        if new_page_size != self.config.page_size:
            self.config.page_size = new_page_size
            # Reset to first page when page size changes
            if self.page:
                self.page.run_task(self._load_page_data(0))
    
    def _on_jump_to_page(self, e):
        """Handle jump to page input."""
        try:
            page_num = int(e.control.value)
            if 1 <= page_num <= self.total_pages:
                if self.page:
                    self.page.run_task(self._go_to_page(page_num - 1))
                e.control.value = ""  # Clear input
                self.update()
        except ValueError:
            # Invalid input, ignore
            pass
    
    async def _on_scroll(self, e):
        """Handle infinite scroll events."""
        if self.config.mode == PaginationMode.INFINITE and not self.loading and self.has_next:
            # Debounce scroll events
            import time
            current_time = time.time() * 1000
            
            if current_time - self._last_scroll_time < self.config.debounce_scroll:
                return
                
            self._last_scroll_time = current_time
            
            # Check if we're near the bottom
            if hasattr(e.control, 'scroll_offset') and hasattr(e.control, 'max_scroll_extent'):
                if e.control.max_scroll_extent > 0:
                    scroll_ratio = e.control.scroll_offset / e.control.max_scroll_extent
                    
                    if scroll_ratio >= self.config.load_more_threshold:
                        await self._load_page_data(self.current_page + 1)
    
    # Public methods
    
    async def refresh(self):
        """Refresh current page data."""
        await self._load_page_data(self.current_page)
    
    async def search(self, query: str):
        """Perform search and reset to first page."""
        self.search_query = query.strip() if query else None
        self.current_page = 0
        
        # Clear items for infinite scroll
        if self.config.mode == PaginationMode.INFINITE and self.items_container:
            self.items_container.controls.clear()
            
        await self._load_page_data(0)
    
    async def set_filters(self, filters: Dict[str, Any]):
        """Set filters and reload data."""
        self.filters = filters
        self.current_page = 0
        
        # Clear items for infinite scroll
        if self.config.mode == PaginationMode.INFINITE and self.items_container:
            self.items_container.controls.clear()
            
        await self._load_page_data(0)
    
    async def sort(self, field: str, order: str = "asc"):
        """Set sorting and reload data."""
        self.sort_by = field
        self.sort_order = order
        await self._load_page_data(self.current_page)
    
    def get_current_state(self) -> Dict[str, Any]:
        """Get current pagination state."""
        return {
            'current_page': self.current_page,
            'page_size': self.config.page_size,
            'total_count': self.total_count,
            'total_pages': self.total_pages,
            'has_next': self.has_next,
            'has_previous': self.has_previous,
            'search_query': self.search_query,
            'filters': self.filters,
            'sort_by': self.sort_by,
            'sort_order': self.sort_order,
            'loading': self.loading
        }


# Helper functions for creating specific pagination views

def create_table_pagination(
    data_provider: PaginationDataProvider,
    mode: PaginationMode = PaginationMode.FULL,
    page_size: int = 20
) -> UnifiedPagination:
    """
    Create pagination for table views.
    
    Example:
        ```python
        pagination = create_table_pagination(
            data_provider=UserTableProvider(),
            mode=PaginationMode.FULL,
            page_size=25
        )
        ```
    """
    config = PaginationConfig(
        page_size=page_size,
        max_visible_pages=7,
        mode=mode,
        show_size_selector=True,
        show_total_count=True,
        enable_jump_to_page=True,
        size_options=[10, 25, 50, 100]
    )
    
    return UnifiedPagination(
        data_provider=data_provider,
        config=config
    )


def create_grid_pagination(
    data_provider: PaginationDataProvider,
    mode: PaginationMode = PaginationMode.FULL,
    items_per_row: int = 3,
    rows_per_page: int = 4
) -> UnifiedPagination:
    """
    Create pagination for grid views.
    
    Example:
        ```python
        pagination = create_grid_pagination(
            data_provider=ProductGridProvider(),
            items_per_row=4,
            rows_per_page=3
        )
        ```
    """
    config = PaginationConfig(
        page_size=items_per_row * rows_per_page,
        max_visible_pages=5,
        mode=mode,
        show_size_selector=True,
        show_total_count=True,
        size_options=[12, 24, 48, 96]
    )
    
    return UnifiedPagination(
        data_provider=data_provider,
        config=config
    )


def create_list_pagination(
    data_provider: PaginationDataProvider,
    mode: PaginationMode = PaginationMode.FULL,
    page_size: int = 15
) -> UnifiedPagination:
    """
    Create pagination for list views.
    
    Example:
        ```python
        pagination = create_list_pagination(
            data_provider=TaskListProvider(),
            mode=PaginationMode.SIMPLE,
            page_size=10
        )
        ```
    """
    config = PaginationConfig(
        page_size=page_size,
        max_visible_pages=5,
        mode=mode,
        show_size_selector=mode == PaginationMode.FULL,
        show_total_count=True,
        size_options=[5, 10, 15, 30, 50]
    )
    
    return UnifiedPagination(
        data_provider=data_provider,
        config=config
    )


def create_mobile_pagination(
    data_provider: PaginationDataProvider,
    infinite_scroll: bool = False
) -> UnifiedPagination:
    """
    Create mobile-optimized pagination.
    
    Example:
        ```python
        pagination = create_mobile_pagination(
            data_provider=MobileProvider(),
            infinite_scroll=True
        )
        ```
    """
    config = PaginationConfig(
        page_size=10,
        mode=PaginationMode.INFINITE if infinite_scroll else PaginationMode.COMPACT,
        show_size_selector=False,
        show_total_count=not infinite_scroll,
        enable_jump_to_page=False,
        load_more_threshold=0.75
    )
    
    return UnifiedPagination(
        data_provider=data_provider,
        config=config
    )