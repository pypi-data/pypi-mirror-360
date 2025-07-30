"""
Async loading utilities for UI components.

Provides base classes and utilities for building components
that load data asynchronously with proper loading states.
"""

import asyncio
import logging
from typing import Callable, Optional, Any, List, Dict, TypeVar, Generic
from abc import ABC, abstractmethod

import flet as ft

from ..themes import ThemedComponent, get_theme_from_page
from ..feedback import LoadingIndicator, LoadingSize

logger = logging.getLogger(__name__)

T = TypeVar('T')


class AsyncLoader(ft.Stack, ThemedComponent, Generic[T]):
    """
    Base class for components that load data asynchronously.
    
    Provides:
    - Loading state management
    - Error handling
    - Data caching
    - Automatic refresh
    
    Example:
        ```python
        class MyAsyncComponent(AsyncLoader[List[User]]):
            async def load_data(self) -> List[User]:
                # Load users from API
                return await api.get_users()
                
            def build_content(self):
                # Build UI based on self.data
                return ft.Column([
                    ft.Text(f"Found {len(self.data)} users")
                    for user in self.data
                ])
        ```
    """
    
    def __init__(
        self,
        auto_load: bool = True,
        cache_enabled: bool = False,
        cache_ttl: int = 300,  # seconds
        **kwargs
    ):
        ThemedComponent.__init__(self)
        super().__init__(**kwargs)
        
        self.auto_load = auto_load
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl
        
        # State
        self.loading = False
        self.error_message: Optional[str] = None
        self.data: Optional[T] = None
        self._loading_overlay: Optional[ft.Container] = None
        self._content_container: Optional[ft.Container] = None
        self._initialized = False
        self._last_load_time: Optional[float] = None
        
        # Set expand by default
        self.expand = kwargs.get('expand', True)
        
        # Initialize with placeholder controls
        self.controls = [
            ft.Container(expand=True),  # Placeholder for content
            ft.Container(expand=True)   # Placeholder for loading overlay
        ]
    
    def _initialize_structure(self):
        """Initialize the structure after component is ready."""
        if self._initialized:
            return
            
        # Build content container
        self._content_container = ft.Container(
            content=self.build_content(),
            expand=True
        )
        
        # Build loading overlay
        self._loading_overlay = ft.Container(
            content=ft.Column(
                [
                    LoadingIndicator(size=LoadingSize.LARGE),
                    ft.Text("Loading...", size=16)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            bgcolor=ft.Colors.with_opacity(0.8, self.surface_variant_color),
            visible=False,
            expand=True,
            alignment=ft.alignment.center
        )
        
        # Replace placeholder controls
        self.controls.clear()
        self.controls.extend([
            self._content_container,
            self._loading_overlay
        ])
        
        self._initialized = True
    
    def did_mount(self):
        """Called when control is mounted."""
        super().did_mount()
        
        try:
            self._initialize_structure()
            
            # Auto-load data if enabled
            if self.auto_load and self.page:
                self.page.run_task(self.refresh)
                
        except Exception as e:
            logger.error(f"Error in AsyncLoader.did_mount: {e}")
    
    @abstractmethod
    def build_content(self) -> ft.Control:
        """Build the content UI. Override in subclasses."""
        pass
    
    @abstractmethod
    async def load_data(self) -> T:
        """Load data asynchronously. Override in subclasses."""
        pass
    
    async def refresh(self, force: bool = False):
        """Refresh the component by reloading data."""
        # Check cache if enabled
        if not force and self.cache_enabled and self._is_cache_valid():
            return
            
        await self.show_loading()
        
        try:
            self.data = await self.load_data()
            self._last_load_time = asyncio.get_event_loop().time()
            self.error_message = None
            await self.on_data_loaded()
            
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.error_message = str(e)
            await self.show_error(str(e))
            
        finally:
            await self.hide_loading()
    
    def _is_cache_valid(self) -> bool:
        """Check if cached data is still valid."""
        if not self._last_load_time or not self.data:
            return False
            
        elapsed = asyncio.get_event_loop().time() - self._last_load_time
        return elapsed < self.cache_ttl
    
    async def show_loading(self, message: str = "Loading..."):
        """Show loading indicator."""
        try:
            self.loading = True
            if self._loading_overlay:
                self._loading_overlay.visible = True
                
                # Update loading message
                if isinstance(self._loading_overlay.content, ft.Column):
                    controls = self._loading_overlay.content.controls
                    if len(controls) > 1 and isinstance(controls[1], ft.Text):
                        controls[1].value = message
                        
                self.update()
        except Exception as e:
            logger.warning(f"Error showing loading indicator: {e}")
    
    async def hide_loading(self):
        """Hide loading indicator."""
        try:
            self.loading = False
            if self._loading_overlay:
                self._loading_overlay.visible = False
                self.update()
        except Exception as e:
            logger.warning(f"Error hiding loading indicator: {e}")
    
    async def show_error(self, message: str):
        """Show error message."""
        # Default implementation shows snackbar
        if self.page:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"Error: {message}"),
                    bgcolor=self.error_color
                )
            )
    
    async def on_data_loaded(self):
        """Called when data is successfully loaded."""
        await self.update_content()
    
    async def update_content(self):
        """Update the content with loaded data."""
        if self._content_container:
            self._content_container.content = self.build_content()
            self.update()
    
    def update(self):
        """Safe update method."""
        try:
            if self.page and hasattr(self, 'parent') and self.parent is not None:
                super().update()
        except Exception as e:
            logger.debug(f"Update skipped: {e}")


class AsyncDataTable(AsyncLoader[Dict[str, Any]]):
    """
    Async loading data table component.
    
    Example:
        ```python
        async def load_users(query: str, page: int, page_size: int):
            return await api.get_users(
                search=query,
                offset=(page - 1) * page_size,
                limit=page_size
            )
            
        def build_user_row(user):
            return ft.DataRow(cells=[
                ft.DataCell(ft.Text(user.name)),
                ft.DataCell(ft.Text(user.email))
            ])
            
        table = AsyncDataTable(
            columns=["Name", "Email"],
            load_func=load_users,
            row_builder=build_user_row
        )
        ```
    """
    
    def __init__(
        self,
        columns: List[str],
        load_func: Callable,
        row_builder: Callable,
        page_size: int = 20,
        searchable: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.columns = columns
        self.load_func = load_func
        self.row_builder = row_builder
        self.page_size = page_size
        self.searchable = searchable
        
        # Table state
        self.table: Optional[ft.DataTable] = None
        self.search_field: Optional[ft.TextField] = None
        self.current_page = 1
        self.total_pages = 1
        self.search_query = ""
        
        # Pagination controls
        self.prev_button: Optional[ft.IconButton] = None
        self.next_button: Optional[ft.IconButton] = None
        self.page_text: Optional[ft.Text] = None
    
    def build_content(self) -> ft.Control:
        """Build table with search and pagination."""
        controls = []
        
        # Search field
        if self.searchable:
            self.search_field = ft.TextField(
                label="Search",
                prefix_icon=ft.Icons.SEARCH,
                on_submit=self.on_search,
                expand=True
            )
            controls.append(ft.Row([self.search_field], expand=True))
        
        # Data table
        self.table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(col)) for col in self.columns
            ],
            rows=[],
            expand=True
        )
        
        controls.append(
            ft.Container(
                content=self.table,
                expand=True,
                border=ft.border.all(1, self.outline_color),
                border_radius=10,
                padding=10
            )
        )
        
        # Pagination
        self.prev_button = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            on_click=self.prev_page,
            disabled=True
        )
        
        self.page_text = ft.Text(f"Page {self.current_page}")
        
        self.next_button = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            on_click=self.next_page,
            disabled=True
        )
        
        controls.append(
            ft.Row(
                [self.prev_button, self.page_text, self.next_button],
                alignment=ft.MainAxisAlignment.CENTER
            )
        )
        
        return ft.Column(
            controls,
            expand=True,
            spacing=10
        )
    
    async def load_data(self) -> Dict[str, Any]:
        """Load table data."""
        return await self.load_func(
            query=self.search_query,
            page=self.current_page,
            page_size=self.page_size
        )
    
    async def update_content(self):
        """Update table with loaded data."""
        if not self.data or not self.table:
            return
        
        # Update rows
        self.table.rows = [
            self.row_builder(item) for item in self.data.get('results', [])
        ]
        
        # Update pagination
        metadata = self.data.get('metadata', {})
        total_items = metadata.get('total', 0)
        self.total_pages = max(1, (total_items + self.page_size - 1) // self.page_size)
        
        # Update pagination controls
        if self.prev_button:
            self.prev_button.disabled = self.current_page <= 1
            
        if self.page_text:
            self.page_text.value = f"Page {self.current_page} of {self.total_pages}"
            
        if self.next_button:
            self.next_button.disabled = self.current_page >= self.total_pages
        
        self.update()
    
    async def on_search(self, e):
        """Handle search."""
        self.search_query = self.search_field.value if self.search_field else ""
        self.current_page = 1
        await self.refresh()
    
    async def prev_page(self, e):
        """Go to previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            await self.refresh()
    
    async def next_page(self, e):
        """Go to next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            await self.refresh()


class AsyncTaskRunner:
    """
    Utility class for running async tasks with loading states.
    
    Example:
        ```python
        # Run single task with loading dialog
        result = await AsyncTaskRunner.run_with_loading(
            page,
            lambda: api.save_data(data),
            "Saving..."
        )
        
        # Run multiple tasks concurrently
        results = await AsyncTaskRunner.run_concurrent(
            api.load_users(),
            api.load_settings(),
            api.load_stats()
        )
        ```
    """
    
    @staticmethod
    async def run_with_loading(
        page: ft.Page,
        task: Callable,
        loading_text: str = "Processing...",
        show_dialog: bool = True
    ) -> Any:
        """
        Run an async task with loading indicator.
        
        Args:
            page: Flet page
            task: Async function to run
            loading_text: Loading message
            show_dialog: Whether to show modal dialog
            
        Returns:
            Result of the task
        """
        if show_dialog:
            # Create loading dialog
            loading_dialog = ft.AlertDialog(
                modal=True,
                content=ft.Column(
                    [
                        LoadingIndicator(size=LoadingSize.MEDIUM),
                        ft.Text(loading_text)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                    width=200,
                    height=150
                )
            )
            
            # Show dialog
            page.dialog = loading_dialog
            loading_dialog.open = True
            page.update()
            
            try:
                # Run task
                if asyncio.iscoroutinefunction(task):
                    result = await task()
                else:
                    result = await asyncio.create_task(task())
                return result
                
            finally:
                # Hide dialog
                loading_dialog.open = False
                page.update()
        else:
            # Just run the task without UI
            if asyncio.iscoroutinefunction(task):
                return await task()
            else:
                return await asyncio.create_task(task())
    
    @staticmethod
    async def run_concurrent(*tasks, return_exceptions: bool = False):
        """
        Run multiple tasks concurrently.
        
        Args:
            *tasks: Async functions to run
            return_exceptions: Whether to return exceptions or raise
            
        Returns:
            List of results
        """
        return await asyncio.gather(*tasks, return_exceptions=return_exceptions)
    
    @staticmethod
    async def run_sequential(*tasks):
        """
        Run multiple tasks sequentially.
        
        Args:
            *tasks: Async functions to run
            
        Returns:
            List of results
        """
        results = []
        for task in tasks:
            if asyncio.iscoroutinefunction(task):
                result = await task()
            else:
                result = await asyncio.create_task(task())
            results.append(result)
        return results


def async_handler(
    loading_text: str = "Processing...",
    show_loading: bool = True,
    disable_on_run: bool = True,
    error_handler: Optional[Callable] = None
):
    """
    Decorator for async event handlers with loading state.
    
    Args:
        loading_text: Loading message to show
        show_loading: Whether to show loading dialog
        disable_on_run: Whether to disable the control during execution
        error_handler: Custom error handler function
        
    Example:
        ```python
        @async_handler("Saving data...")
        async def save_button_click(self, e):
            await self.save_data()
            
        @async_handler(show_loading=False)
        async def quick_action(self, e):
            await self.perform_action()
        ```
    """
    def decorator(func):
        async def wrapper(self, e):
            page = getattr(self, 'page', None)
            if not page:
                # Try to get page from event
                page = getattr(e, 'page', None)
                
            if not page:
                # No page available, just run the function
                return await func(self, e)
            
            control = getattr(e, 'control', None)
            original_disabled = None
            
            try:
                # Disable control if requested
                if disable_on_run and control and hasattr(control, 'disabled'):
                    original_disabled = control.disabled
                    control.disabled = True
                    page.update()
                
                # Run with or without loading dialog
                if show_loading:
                    result = await AsyncTaskRunner.run_with_loading(
                        page,
                        lambda: func(self, e),
                        loading_text
                    )
                else:
                    result = await func(self, e)
                    
                return result
                
            except Exception as error:
                logger.error(f"Error in async handler: {error}")
                
                # Use custom error handler if provided
                if error_handler:
                    await error_handler(error, page)
                else:
                    # Default error handling
                    page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text(f"Error: {str(error)}"),
                            bgcolor=ft.Colors.ERROR
                        )
                    )
                    
            finally:
                # Re-enable control
                if disable_on_run and control and hasattr(control, 'disabled') and original_disabled is not None:
                    control.disabled = original_disabled
                    page.update()
        
        # Preserve original function metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        
        return wrapper
    return decorator