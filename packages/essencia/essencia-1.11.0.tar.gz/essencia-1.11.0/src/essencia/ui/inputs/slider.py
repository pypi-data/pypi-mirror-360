"""
Slider components with theme integration.
"""

from typing import Optional, Callable, Any, Tuple
import flet as ft
from .theme_helper import get_theme_mode


class ThemedSlider(ft.Slider):
    """Slider with automatic theme-aware styling.
    
    A slider control for selecting numeric values within a range,
    with theme-aware styling and optional value display.
    
    Example:
        ```python
        volume_slider = ThemedSlider(
            label="Volume",
            min=0,
            max=100,
            value=50,
            divisions=10,
            show_value=True,
            on_change=handle_volume_change
        )
        ```
    """
    
    def __init__(
        self,
        min: float = 0,
        max: float = 100,
        value: float = 0,
        divisions: Optional[int] = None,
        label: Optional[str] = None,
        show_value: bool = False,
        value_format: str = "{:.0f}",
        on_change: Optional[Callable[[Any], None]] = None,
        on_change_start: Optional[Callable[[Any], None]] = None,
        on_change_end: Optional[Callable[[Any], None]] = None,
        **kwargs
    ):
        # Store configuration
        self._label = label
        self._show_value = show_value
        self._value_format = value_format
        
        # Store theme overrides
        self._active_color = kwargs.pop('active_color', None)
        self._inactive_color = kwargs.pop('inactive_color', None)
        self._thumb_color = kwargs.pop('thumb_color', None)
        
        super().__init__(
            min=min,
            max=max,
            value=value,
            divisions=divisions,
            label=label if not show_value else None,
            on_change=on_change,
            on_change_start=on_change_start,
            on_change_end=on_change_end,
            **kwargs
        )
        
    def did_mount(self):
        """Apply theme styling after control is mounted."""
        super().did_mount()
        
        # Determine theme mode
        is_light = get_theme_mode(self.page if hasattr(self, 'page') else None) == 'light'
        
        # Apply theme-aware colors if not overridden
        if not self._active_color:
            if is_light:
                self.active_color = ft.Colors.PRIMARY
            else:
                self.active_color = ft.Colors.ORANGE_400
                
        if not self._inactive_color:
            if is_light:
                self.inactive_color = ft.Colors.GREY_300
            else:
                self.inactive_color = ft.Colors.GREY_700
                
        if not self._thumb_color:
            if is_light:
                self.thumb_color = ft.Colors.PRIMARY
            else:
                self.thumb_color = ft.Colors.ORANGE_400
                
        # Update label if showing value
        if self._show_value:
            self._update_label()
            
        if hasattr(self, 'update'):
            self.update()
            
    def _update_label(self):
        """Update label to show current value."""
        if self._label:
            self.label = f"{self._label}: {self._value_format.format(self.value)}"
        else:
            self.label = self._value_format.format(self.value)


class RangeSlider(ft.Container):
    """Range slider for selecting a value range.
    
    Combines two sliders to allow selection of a minimum and maximum value.
    
    Example:
        ```python
        price_range = RangeSlider(
            label="Price Range",
            min=0,
            max=1000,
            start_value=100,
            end_value=500,
            step=50,
            format_value=lambda v: f"${v}",
            on_change=handle_price_range_change
        )
        ```
    """
    
    def __init__(
        self,
        label: Optional[str] = None,
        min: float = 0,
        max: float = 100,
        start_value: float = 0,
        end_value: float = 100,
        step: Optional[float] = None,
        format_value: Optional[Callable[[float], str]] = None,
        on_change: Optional[Callable[[Tuple[float, float]], None]] = None,
        **kwargs
    ):
        self._label = label
        self._min = min
        self._max = max
        self._start_value = max(min, min(start_value, end_value))
        self._end_value = min(max, max(start_value, end_value))
        self._format_value = format_value or (lambda v: str(int(v)))
        self._on_change = on_change
        
        # Calculate divisions from step
        divisions = None
        if step:
            divisions = int((max - min) / step)
            
        # Create controls
        controls = []
        
        # Label
        if label:
            self._label_text = ft.Text(
                label,
                size=16,
                weight=ft.FontWeight.W_500
            )
            controls.append(self._label_text)
            
        # Value display
        self._value_text = ft.Text(
            self._get_range_text(),
            size=14
        )
        controls.append(self._value_text)
        
        # Min slider
        self._min_slider = ThemedSlider(
            min=min,
            max=max,
            value=self._start_value,
            divisions=divisions,
            on_change=self._handle_min_change
        )
        
        # Max slider  
        self._max_slider = ThemedSlider(
            min=min,
            max=max,
            value=self._end_value,
            divisions=divisions,
            on_change=self._handle_max_change
        )
        
        # Slider labels
        slider_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Min", size=12),
                            self._min_slider
                        ],
                        spacing=5
                    ),
                    expand=True
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text("Max", size=12),
                            self._max_slider
                        ],
                        spacing=5
                    ),
                    expand=True
                )
            ],
            spacing=20
        )
        
        controls.append(slider_row)
        
        # Set content
        content = ft.Column(
            controls=controls,
            spacing=10
        )
        
        super().__init__(content=content, **kwargs)
        
    def _get_range_text(self) -> str:
        """Get formatted range text."""
        return f"{self._format_value(self._start_value)} - {self._format_value(self._end_value)}"
        
    def _handle_min_change(self, e):
        """Handle minimum value change."""
        new_min = e.control.value
        
        # Ensure min doesn't exceed max
        if new_min > self._end_value:
            new_min = self._end_value
            self._min_slider.value = new_min
            self._min_slider.update()
            
        self._start_value = new_min
        self._value_text.value = self._get_range_text()
        self._value_text.update()
        
        if self._on_change:
            self._on_change((self._start_value, self._end_value))
            
    def _handle_max_change(self, e):
        """Handle maximum value change."""
        new_max = e.control.value
        
        # Ensure max doesn't go below min
        if new_max < self._start_value:
            new_max = self._start_value
            self._max_slider.value = new_max
            self._max_slider.update()
            
        self._end_value = new_max
        self._value_text.value = self._get_range_text()
        self._value_text.update()
        
        if self._on_change:
            self._on_change((self._start_value, self._end_value))
            
    def did_mount(self):
        """Apply theme styling after control is mounted."""
        super().did_mount()
        
        # Determine theme mode
        is_light = get_theme_mode(self.page if hasattr(self, 'page') else None) == 'light'
        
        # Apply theme to text elements
        if hasattr(self, '_label_text'):
            self._label_text.color = ft.Colors.BLACK if is_light else ft.Colors.WHITE
            
        self._value_text.color = ft.Colors.ON_SURFACE_VARIANT if is_light else ft.Colors.GREY_400
        
        # Update slider labels
        for control in self.content.controls[-1].controls:
            if isinstance(control, ft.Container) and isinstance(control.content, ft.Column):
                label_text = control.content.controls[0]
                label_text.color = ft.Colors.ON_SURFACE_VARIANT if is_light else ft.Colors.GREY_400
                
        if hasattr(self, 'update'):
            self.update()
            
    def get_range(self) -> Tuple[float, float]:
        """Get current selected range.
        
        Returns:
            Tuple of (start_value, end_value)
        """
        return (self._start_value, self._end_value)
        
    def set_range(self, start_value: float, end_value: float):
        """Set the range programmatically.
        
        Args:
            start_value: New minimum value
            end_value: New maximum value
        """
        self._start_value = max(self._min, min(start_value, end_value))
        self._end_value = min(self._max, max(start_value, end_value))
        
        self._min_slider.value = self._start_value
        self._max_slider.value = self._end_value
        self._value_text.value = self._get_range_text()
        
        if hasattr(self, 'update'):
            self.update()