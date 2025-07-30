"""
Time picker component with theme integration.
"""

from typing import Optional, Callable, Any
from datetime import time, datetime
import flet as ft
from .theme_helper import apply_input_theme


class ThemedTimePicker(ft.Container):
    """Time picker with theme-aware styling.
    
    Provides a time selection interface with hour/minute inputs
    and optional AM/PM selection.
    
    Example:
        ```python
        time_picker = ThemedTimePicker(
            label="Appointment Time",
            value=time(14, 30),
            on_change=handle_time_change,
            use_24_hour=False
        )
        ```
    """
    
    def __init__(
        self,
        label: Optional[str] = None,
        value: Optional[time] = None,
        on_change: Optional[Callable[[time], None]] = None,
        use_24_hour: bool = True,
        show_seconds: bool = False,
        minute_increment: int = 1,
        **kwargs
    ):
        self._on_change = on_change
        self._use_24_hour = use_24_hour
        self._show_seconds = show_seconds
        self._minute_increment = minute_increment
        
        # Initialize time value
        if value is None:
            value = datetime.now().time()
        self._value = value
        
        # Create controls
        controls = []
        
        # Label
        if label:
            self._label_text = ft.Text(label, size=14, weight=ft.FontWeight.W_500)
            controls.append(self._label_text)
            
        # Time input row
        time_row = ft.Row(spacing=5, alignment=ft.MainAxisAlignment.START)
        
        # Hour input
        from .text_field import ThemedTextField
        max_hour = 23 if use_24_hour else 12
        self._hour_input = ThemedTextField(
            value=str(self._format_hour(value.hour)),
            width=60,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._handle_hour_change,
            input_filter=ft.NumbersOnlyInputFilter(),
            max_length=2
        )
        time_row.controls.append(self._hour_input)
        
        # Separator
        time_row.controls.append(ft.Text(":", size=20, weight=ft.FontWeight.BOLD))
        
        # Minute input
        self._minute_input = ThemedTextField(
            value=f"{value.minute:02d}",
            width=60,
            text_align=ft.TextAlign.CENTER,
            keyboard_type=ft.KeyboardType.NUMBER,
            on_change=self._handle_minute_change,
            input_filter=ft.NumbersOnlyInputFilter(),
            max_length=2
        )
        time_row.controls.append(self._minute_input)
        
        # Seconds input (if enabled)
        if show_seconds:
            time_row.controls.append(ft.Text(":", size=20, weight=ft.FontWeight.BOLD))
            self._second_input = ThemedTextField(
                value=f"{value.second:02d}",
                width=60,
                text_align=ft.TextAlign.CENTER,
                keyboard_type=ft.KeyboardType.NUMBER,
                on_change=self._handle_second_change,
                input_filter=ft.NumbersOnlyInputFilter(),
                max_length=2
            )
            time_row.controls.append(self._second_input)
            
        # AM/PM selector for 12-hour format
        if not use_24_hour:
            self._am_pm_dropdown = ft.Dropdown(
                value="AM" if value.hour < 12 else "PM",
                options=[
                    ft.dropdown.Option("AM"),
                    ft.dropdown.Option("PM")
                ],
                width=80,
                on_change=self._handle_am_pm_change
            )
            time_row.controls.append(self._am_pm_dropdown)
            
        controls.append(time_row)
        
        # Quick time buttons (optional)
        quick_times = ft.Row(spacing=5)
        for hour in [9, 12, 15, 18]:
            quick_btn = ft.TextButton(
                text=self._format_display_time(time(hour, 0)),
                on_click=lambda e, h=hour: self._set_time(time(h, 0))
            )
            quick_times.controls.append(quick_btn)
            
        if len(quick_times.controls) > 0:
            controls.append(ft.Container(
                content=quick_times,
                margin=ft.margin.only(top=5)
            ))
            
        # Set content
        content = ft.Column(controls=controls, spacing=10)
        
        super().__init__(content=content, **kwargs)
        
    def _format_hour(self, hour: int) -> int:
        """Format hour for display based on 12/24 hour format."""
        if self._use_24_hour:
            return hour
        else:
            if hour == 0:
                return 12
            elif hour > 12:
                return hour - 12
            else:
                return hour
                
    def _format_display_time(self, t: time) -> str:
        """Format time for display."""
        if self._use_24_hour:
            if self._show_seconds:
                return f"{t.hour:02d}:{t.minute:02d}:{t.second:02d}"
            else:
                return f"{t.hour:02d}:{t.minute:02d}"
        else:
            hour = self._format_hour(t.hour)
            am_pm = "AM" if t.hour < 12 else "PM"
            if self._show_seconds:
                return f"{hour}:{t.minute:02d}:{t.second:02d} {am_pm}"
            else:
                return f"{hour}:{t.minute:02d} {am_pm}"
                
    def _handle_hour_change(self, e):
        """Handle hour input change."""
        try:
            hour = int(e.control.value) if e.control.value else 0
            
            # Validate hour
            if self._use_24_hour:
                hour = min(23, max(0, hour))
            else:
                hour = min(12, max(1, hour))
                # Convert to 24-hour format
                if hasattr(self, '_am_pm_dropdown'):
                    if self._am_pm_dropdown.value == "PM" and hour != 12:
                        hour += 12
                    elif self._am_pm_dropdown.value == "AM" and hour == 12:
                        hour = 0
                        
            # Update value
            self._value = time(
                hour,
                self._value.minute,
                self._value.second if self._show_seconds else 0
            )
            
            if self._on_change:
                self._on_change(self._value)
                
        except ValueError:
            pass
            
    def _handle_minute_change(self, e):
        """Handle minute input change."""
        try:
            minute = int(e.control.value) if e.control.value else 0
            minute = min(59, max(0, minute))
            
            # Round to increment if specified
            if self._minute_increment > 1:
                minute = round(minute / self._minute_increment) * self._minute_increment
                e.control.value = f"{minute:02d}"
                e.control.update()
                
            # Update value
            self._value = time(
                self._value.hour,
                minute,
                self._value.second if self._show_seconds else 0
            )
            
            if self._on_change:
                self._on_change(self._value)
                
        except ValueError:
            pass
            
    def _handle_second_change(self, e):
        """Handle second input change."""
        try:
            second = int(e.control.value) if e.control.value else 0
            second = min(59, max(0, second))
            
            # Update value
            self._value = time(
                self._value.hour,
                self._value.minute,
                second
            )
            
            if self._on_change:
                self._on_change(self._value)
                
        except ValueError:
            pass
            
    def _handle_am_pm_change(self, e):
        """Handle AM/PM selection change."""
        hour = self._value.hour
        
        if e.control.value == "PM" and hour < 12:
            hour += 12
        elif e.control.value == "AM" and hour >= 12:
            hour -= 12
            
        self._value = time(
            hour,
            self._value.minute,
            self._value.second if self._show_seconds else 0
        )
        
        if self._on_change:
            self._on_change(self._value)
            
    def _set_time(self, t: time):
        """Set time from quick selection."""
        self._value = t
        
        # Update inputs
        self._hour_input.value = str(self._format_hour(t.hour))
        self._minute_input.value = f"{t.minute:02d}"
        
        if self._show_seconds:
            self._second_input.value = f"{t.second:02d}"
            
        if not self._use_24_hour:
            self._am_pm_dropdown.value = "AM" if t.hour < 12 else "PM"
            
        self.update()
        
        if self._on_change:
            self._on_change(t)
            
    def did_mount(self):
        """Apply theme styling after control is mounted."""
        super().did_mount()
        
        # Apply theme to AM/PM dropdown if exists
        if hasattr(self, '_am_pm_dropdown'):
            apply_input_theme(
                self._am_pm_dropdown,
                self.page if hasattr(self, 'page') else None
            )
            
        if hasattr(self, 'update'):
            self.update()
            
    @property
    def value(self) -> time:
        """Get current time value."""
        return self._value
        
    @value.setter  
    def value(self, t: time):
        """Set time value."""
        self._set_time(t)