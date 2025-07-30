"""
Simple pagination components for lightweight use cases.

Provides simplified pagination variants that are easy to use
for basic pagination needs.
"""

from typing import Optional, Callable, List, Any
import flet as ft

from .unified import UnifiedPagination, PaginationConfig, PaginationMode, PaginationDataProvider


class SimplePagination(ft.Row):
    """
    Simple pagination with just prev/next buttons.
    
    Example:
        ```python
        pagination = SimplePagination(
            total_pages=10,
            on_change=lambda page: load_page(page)
        )
        ```
    """
    
    def __init__(
        self,
        total_pages: int,
        current_page: int = 0,
        on_change: Optional[Callable[[int], None]] = None,
        show_page_info: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.total_pages = total_pages
        self.current_page = current_page
        self.on_change = on_change
        self.show_page_info = show_page_info
        
        # Create controls
        self.prev_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            on_click=self._go_prev,
            disabled=current_page <= 0
        )
        
        self.next_button = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD,
            on_click=self._go_next,
            disabled=current_page >= total_pages - 1
        )
        
        self.page_text = ft.Text(
            f"Page {current_page + 1} of {total_pages}",
            size=14
        )
        
        # Build layout
        self.controls = [self.prev_button]
        
        if show_page_info:
            self.controls.append(self.page_text)
            
        self.controls.append(self.next_button)
        
        self.alignment = ft.MainAxisAlignment.CENTER
        self.spacing = 10
    
    def _go_prev(self, e):
        """Go to previous page."""
        if self.current_page > 0:
            self.set_page(self.current_page - 1)
    
    def _go_next(self, e):
        """Go to next page."""
        if self.current_page < self.total_pages - 1:
            self.set_page(self.current_page + 1)
    
    def set_page(self, page: int):
        """Set current page."""
        if 0 <= page < self.total_pages:
            self.current_page = page
            
            # Update controls
            self.prev_button.disabled = page <= 0
            self.next_button.disabled = page >= self.total_pages - 1
            
            if self.show_page_info:
                self.page_text.value = f"Page {page + 1} of {self.total_pages}"
            
            self.update()
            
            # Call callback
            if self.on_change:
                self.on_change(page)
    
    def set_total_pages(self, total: int):
        """Update total pages."""
        self.total_pages = total
        
        # Adjust current page if needed
        if self.current_page >= total:
            self.current_page = max(0, total - 1)
            
        # Update controls
        self.set_page(self.current_page)


class CompactPagination(ft.Container):
    """
    Compact pagination for mobile/tight spaces.
    
    Example:
        ```python
        pagination = CompactPagination(
            total_items=100,
            page_size=10,
            on_change=lambda page: load_page(page)
        )
        ```
    """
    
    def __init__(
        self,
        total_items: int,
        page_size: int = 10,
        current_page: int = 0,
        on_change: Optional[Callable[[int], None]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.total_items = total_items
        self.page_size = page_size
        self.current_page = current_page
        self.total_pages = max(1, (total_items + page_size - 1) // page_size)
        self.on_change = on_change
        
        # Create page selector dropdown
        self.page_selector = ft.Dropdown(
            value=str(current_page + 1),
            options=[
                ft.dropdown.Option(str(i + 1))
                for i in range(self.total_pages)
            ],
            width=80,
            height=40,
            text_size=14,
            on_change=self._on_page_select
        )
        
        # Create info text
        start = current_page * page_size + 1
        end = min((current_page + 1) * page_size, total_items)
        self.info_text = ft.Text(
            f"{start}-{end} of {total_items}",
            size=12,
            color=ft.Colors.ON_SURFACE_VARIANT
        )
        
        # Build layout
        self.content = ft.Row([
            self.page_selector,
            self.info_text
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER)
        
        self.padding = 10
    
    def _on_page_select(self, e):
        """Handle page selection."""
        page = int(e.control.value) - 1
        self.set_page(page)
    
    def set_page(self, page: int):
        """Set current page."""
        if 0 <= page < self.total_pages:
            self.current_page = page
            
            # Update selector
            self.page_selector.value = str(page + 1)
            
            # Update info
            start = page * self.page_size + 1
            end = min((page + 1) * self.page_size, self.total_items)
            self.info_text.value = f"{start}-{end} of {self.total_items}"
            
            self.update()
            
            # Call callback
            if self.on_change:
                self.on_change(page)
    
    def update_total(self, total_items: int):
        """Update total items."""
        self.total_items = total_items
        self.total_pages = max(1, (total_items + self.page_size - 1) // self.page_size)
        
        # Update dropdown options
        self.page_selector.options = [
            ft.dropdown.Option(str(i + 1))
            for i in range(self.total_pages)
        ]
        
        # Adjust current page if needed
        if self.current_page >= self.total_pages:
            self.set_page(self.total_pages - 1)
        else:
            self.set_page(self.current_page)


class InfiniteScroll(ft.ListView):
    """
    Infinite scroll container for continuous loading.
    
    Example:
        ```python
        scroll = InfiniteScroll(
            initial_items=first_page_items,
            load_more=lambda: load_next_page(),
            item_builder=lambda item: ft.ListTile(title=ft.Text(item.name))
        )
        ```
    """
    
    def __init__(
        self,
        initial_items: List[Any] = None,
        load_more: Optional[Callable[[], List[Any]]] = None,
        item_builder: Optional[Callable[[Any], ft.Control]] = None,
        threshold: float = 0.8,
        show_loading: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.items = initial_items or []
        self.load_more = load_more
        self.item_builder = item_builder or self._default_item_builder
        self.threshold = threshold
        self.show_loading = show_loading
        self.is_loading = False
        self.has_more = True
        
        # Configure ListView
        self.spacing = 0
        self.padding = ft.padding.all(0)
        self.on_scroll = self._on_scroll
        
        # Loading indicator
        self.loading_indicator = ft.Container(
            content=ft.Row([
                ft.ProgressRing(width=20, height=20, stroke_width=2),
                ft.Text("Loading more...", size=14)
            ], alignment=ft.MainAxisAlignment.CENTER),
            padding=20,
            visible=False
        )
        
        # Build initial items
        self._build_items()
    
    def _default_item_builder(self, item: Any) -> ft.Control:
        """Default item builder."""
        return ft.Container(
            content=ft.Text(str(item)),
            padding=10,
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT))
        )
    
    def _build_items(self):
        """Build item widgets."""
        self.controls.clear()
        
        # Add items
        for item in self.items:
            self.controls.append(self.item_builder(item))
        
        # Add loading indicator
        if self.show_loading:
            self.controls.append(self.loading_indicator)
    
    async def _on_scroll(self, e):
        """Handle scroll events."""
        if not self.has_more or self.is_loading or not self.load_more:
            return
        
        # Check if near bottom
        if hasattr(e.control, 'scroll_offset') and hasattr(e.control, 'max_scroll_extent'):
            if e.control.max_scroll_extent > 0:
                scroll_ratio = e.control.scroll_offset / e.control.max_scroll_extent
                
                if scroll_ratio >= self.threshold:
                    await self._load_more_items()
    
    async def _load_more_items(self):
        """Load more items."""
        if self.is_loading:
            return
            
        self.is_loading = True
        
        # Show loading
        if self.show_loading:
            self.loading_indicator.visible = True
            self.update()
        
        try:
            # Load items
            if asyncio.iscoroutinefunction(self.load_more):
                new_items = await self.load_more()
            else:
                new_items = self.load_more()
            
            if new_items:
                # Add new items
                self.items.extend(new_items)
                
                # Add widgets (before loading indicator)
                insert_index = len(self.controls) - 1 if self.show_loading else len(self.controls)
                
                for item in new_items:
                    widget = self.item_builder(item)
                    self.controls.insert(insert_index, widget)
                    insert_index += 1
                
                self.update()
            else:
                # No more items
                self.has_more = False
                
        finally:
            self.is_loading = False
            
            # Hide loading
            if self.show_loading:
                self.loading_indicator.visible = False
                self.update()
    
    def add_items(self, items: List[Any]):
        """Add items programmatically."""
        self.items.extend(items)
        
        # Add widgets
        insert_index = len(self.controls) - 1 if self.show_loading else len(self.controls)
        
        for item in items:
            widget = self.item_builder(item)
            self.controls.insert(insert_index, widget)
            insert_index += 1
        
        self.update()
    
    def clear(self):
        """Clear all items."""
        self.items.clear()
        self._build_items()
        self.has_more = True
        self.update()
    
    def reset(self, items: List[Any] = None):
        """Reset with new items."""
        self.items = items or []
        self._build_items()
        self.has_more = True
        self.update()


# Import asyncio for async support
import asyncio