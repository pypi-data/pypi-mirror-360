"""
Date picker components with theme integration.
"""

from typing import Optional, Callable, Any, Tuple
from datetime import datetime, date, timedelta
import flet as ft
from .theme_helper import get_theme_mode


class ThemedDatePicker(ft.DatePicker):
    """DatePicker with theme-aware styling.
    
    Provides a date picker that adapts to the application theme
    with optimized visibility in both light and dark modes.
    
    Example:
        ```python
        date_picker = ThemedDatePicker(
            on_change=handle_date_change,
            first_date=datetime(2020, 1, 1),
            last_date=datetime(2030, 12, 31)
        )
        
        # Open the picker
        open_date_picker(page, date_picker)
        ```
    """
    
    def __init__(
        self,
        value: Optional[datetime] = None,
        first_date: Optional[datetime] = None,
        last_date: Optional[datetime] = None,
        on_change: Optional[Callable[[Any], None]] = None,
        date_picker_mode: ft.DatePickerMode = ft.DatePickerMode.DAY,
        **kwargs
    ):
        # Set reasonable defaults for date range if not provided
        if not first_date:
            first_date = datetime.now() - timedelta(days=365 * 10)  # 10 years ago
            
        if not last_date:
            last_date = datetime.now() + timedelta(days=365 * 10)  # 10 years ahead
            
        super().__init__(
            value=value,
            first_date=first_date,
            last_date=last_date,
            on_change=on_change,
            date_picker_mode=date_picker_mode,
            **kwargs
        )


def open_date_picker(page: ft.Page, picker: ThemedDatePicker, optimize_theme: bool = True):
    """Open a date picker with optimal theme settings.
    
    This function handles the date picker opening with optional theme
    optimization for better visibility.
    
    Args:
        page: The Flet page
        picker: The date picker to open
        optimize_theme: Whether to temporarily optimize theme for picker visibility
        
    Example:
        ```python
        picker = ThemedDatePicker(on_change=handle_date)
        open_date_picker(page, picker)
        ```
    """
    if not page:
        return
        
    # Add to overlay if not already there
    if picker not in page.overlay:
        page.overlay.append(picker)
        
    if optimize_theme:
        # Store original theme for restoration
        original_theme_mode = getattr(page, 'theme_mode', ft.ThemeMode.SYSTEM)
        original_theme = getattr(page, 'theme', None)
        
        def restore_theme():
            """Restore original theme after picker closes."""
            if page:
                page.theme_mode = original_theme_mode
                if original_theme:
                    page.theme = original_theme
                page.update()
        
        # Enhance the picker's on_change to restore theme
        original_on_change = picker.on_change
        
        def enhanced_on_change(e):
            if original_on_change:
                original_on_change(e)
            # Restore theme after selection
            import threading
            timer = threading.Timer(0.5, restore_theme)
            timer.daemon = True
            timer.start()
        
        picker.on_change = enhanced_on_change
        
        # Apply optimized theme based on current mode
        is_light = get_theme_mode(page) == 'light'
        
        if is_light:
            # Light mode optimization
            page.theme_mode = ft.ThemeMode.LIGHT
            page.theme = ft.Theme(
                color_scheme=ft.ColorScheme(
                    primary=ft.Colors.BLUE_600,
                    surface=ft.Colors.WHITE,
                    on_surface=ft.Colors.BLACK,
                    background=ft.Colors.GREY_100,
                    outline=ft.Colors.GREY_400
                ),
                use_material3=True
            )
        else:
            # Dark mode optimization
            page.theme_mode = ft.ThemeMode.DARK
            page.theme = ft.Theme(
                color_scheme=ft.ColorScheme(
                    primary=ft.Colors.ORANGE_400,
                    secondary=ft.Colors.ORANGE_300,
                    surface=ft.Colors.GREY_900,
                    on_surface=ft.Colors.WHITE,
                    background=ft.Colors.BLACK,
                    surface_variant=ft.Colors.GREY_800,
                    on_surface_variant=ft.Colors.GREY_300,
                    outline=ft.Colors.GREY_500,
                    primary_container=ft.Colors.ORANGE_800,
                    on_primary_container=ft.Colors.WHITE
                ),
                use_material3=True
            )
        
        page.update()
    
    # Open the picker
    picker.open = True
    page.update()
    page.open(picker)


class DateRangePicker(ft.Container):
    """Date range picker combining two date fields.
    
    Provides an easy way to select a date range with validation
    to ensure end date is after start date.
    
    Example:
        ```python
        range_picker = DateRangePicker(
            on_change=handle_range_change,
            start_label="Check-in",
            end_label="Check-out"
        )
        
        # Get selected range
        start, end = range_picker.get_range()
        ```
    """
    
    def __init__(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        start_label: str = "Start Date",
        end_label: str = "End Date",
        on_change: Optional[Callable[[Tuple[Optional[datetime], Optional[datetime]]], None]] = None,
        spacing: int = 10,
        **kwargs
    ):
        self._on_change = on_change
        self._start_date = start_date
        self._end_date = end_date
        
        # Create date pickers
        self.start_picker = ThemedDatePicker(
            value=start_date,
            on_change=self._handle_start_change
        )
        
        self.end_picker = ThemedDatePicker(
            value=end_date,
            first_date=start_date,  # End must be after start
            on_change=self._handle_end_change
        )
        
        # Create text fields that show selected dates
        self.start_field = ft.TextField(
            label=start_label,
            value=start_date.strftime("%Y-%m-%d") if start_date else "",
            read_only=True,
            suffix=ft.IconButton(
                icon=ft.Icons.CALENDAR_TODAY,
                on_click=lambda _: self._open_start_picker()
            )
        )
        
        self.end_field = ft.TextField(
            label=end_label,
            value=end_date.strftime("%Y-%m-%d") if end_date else "",
            read_only=True,
            suffix=ft.IconButton(
                icon=ft.Icons.CALENDAR_TODAY,
                on_click=lambda _: self._open_end_picker()
            )
        )
        
        # Layout
        content = ft.Row(
            controls=[self.start_field, self.end_field],
            spacing=spacing
        )
        
        super().__init__(content=content, **kwargs)
        
    def _handle_start_change(self, e):
        """Handle start date change."""
        self._start_date = e.control.value
        self.start_field.value = self._start_date.strftime("%Y-%m-%d")
        self.start_field.update()
        
        # Update end picker's first date
        self.end_picker.first_date = self._start_date
        
        # Clear end date if it's before start
        if self._end_date and self._end_date < self._start_date:
            self._end_date = None
            self.end_field.value = ""
            self.end_field.update()
            
        if self._on_change:
            self._on_change((self._start_date, self._end_date))
            
    def _handle_end_change(self, e):
        """Handle end date change."""
        self._end_date = e.control.value
        self.end_field.value = self._end_date.strftime("%Y-%m-%d")
        self.end_field.update()
        
        if self._on_change:
            self._on_change((self._start_date, self._end_date))
            
    def _open_start_picker(self):
        """Open start date picker."""
        if hasattr(self, 'page') and self.page:
            open_date_picker(self.page, self.start_picker)
            
    def _open_end_picker(self):
        """Open end date picker."""
        if hasattr(self, 'page') and self.page:
            open_date_picker(self.page, self.end_picker)
            
    def get_range(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Get the selected date range.
        
        Returns:
            Tuple of (start_date, end_date)
        """
        return (self._start_date, self._end_date)
        
    def set_range(self, start_date: Optional[datetime], end_date: Optional[datetime]):
        """Set the date range programmatically.
        
        Args:
            start_date: Start date
            end_date: End date (must be after start_date)
        """
        if start_date:
            self._start_date = start_date
            self.start_field.value = start_date.strftime("%Y-%m-%d")
            self.start_picker.value = start_date
            
        if end_date and (not start_date or end_date >= start_date):
            self._end_date = end_date
            self.end_field.value = end_date.strftime("%Y-%m-%d")
            self.end_picker.value = end_date
            self.end_picker.first_date = start_date
            
        self.update()