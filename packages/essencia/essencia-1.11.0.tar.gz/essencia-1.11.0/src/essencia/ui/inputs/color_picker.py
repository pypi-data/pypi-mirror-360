"""
Color picker component with theme integration.
"""

from typing import Optional, Callable, Any, List
import flet as ft


class ThemedColorPicker(ft.Container):
    """Color picker with theme-aware styling.
    
    Provides a color selection interface with preset colors
    and custom color input.
    
    Example:
        ```python
        color_picker = ThemedColorPicker(
            label="Theme Color",
            value="#2196F3",
            on_change=handle_color_change,
            show_presets=True
        )
        ```
    """
    
    def __init__(
        self,
        label: Optional[str] = None,
        value: str = "#000000",
        on_change: Optional[Callable[[str], None]] = None,
        show_presets: bool = True,
        preset_colors: Optional[List[str]] = None,
        allow_custom: bool = True,
        **kwargs
    ):
        self._value = value
        self._on_change = on_change
        self._show_presets = show_presets
        self._allow_custom = allow_custom
        
        # Default preset colors if not provided
        if preset_colors is None:
            preset_colors = [
                "#F44336",  # Red
                "#E91E63",  # Pink
                "#9C27B0",  # Purple
                "#673AB7",  # Deep Purple
                "#3F51B5",  # Indigo
                "#2196F3",  # Blue
                "#03A9F4",  # Light Blue
                "#00BCD4",  # Cyan
                "#009688",  # Teal
                "#4CAF50",  # Green
                "#8BC34A",  # Light Green
                "#CDDC39",  # Lime
                "#FFEB3B",  # Yellow
                "#FFC107",  # Amber
                "#FF9800",  # Orange
                "#FF5722",  # Deep Orange
                "#795548",  # Brown
                "#9E9E9E",  # Grey
                "#607D8B",  # Blue Grey
                "#000000",  # Black
                "#FFFFFF",  # White
            ]
        self._preset_colors = preset_colors
        
        # Create controls
        controls = []
        
        # Label
        if label:
            self._label_text = ft.Text(label, size=14, weight=ft.FontWeight.W_500)
            controls.append(self._label_text)
            
        # Color display and selector
        color_row = ft.Row(spacing=10)
        
        # Current color display
        self._color_display = ft.Container(
            width=50,
            height=50,
            bgcolor=value,
            border_radius=ft.border_radius.all(8),
            border=ft.border.all(2, ft.Colors.OUTLINE)
        )
        color_row.controls.append(self._color_display)
        
        # Color value input
        if allow_custom:
            from .text_field import ThemedTextField
            self._color_input = ThemedTextField(
                value=value,
                label="Hex Color",
                prefix_text="#",
                max_length=6,
                on_change=self._handle_input_change,
                width=150
            )
            # Remove the # from value for input
            if value.startswith("#"):
                self._color_input.value = value[1:]
            color_row.controls.append(self._color_input)
            
        controls.append(color_row)
        
        # Preset colors
        if show_presets:
            preset_grid = ft.GridView(
                expand=False,
                height=120,
                runs_count=7,
                spacing=5,
                run_spacing=5,
                child_aspect_ratio=1.0
            )
            
            for color in self._preset_colors:
                color_chip = ft.Container(
                    width=30,
                    height=30,
                    bgcolor=color,
                    border_radius=ft.border_radius.all(4),
                    on_click=lambda e, c=color: self._select_color(c),
                    tooltip=color,
                    border=ft.border.all(
                        2,
                        ft.Colors.PRIMARY if color == value else ft.Colors.TRANSPARENT
                    )
                )
                preset_grid.controls.append(color_chip)
                
            controls.append(ft.Container(
                content=preset_grid,
                margin=ft.margin.only(top=10)
            ))
            
        # Set content
        content = ft.Column(controls=controls, spacing=10)
        
        super().__init__(content=content, **kwargs)
        
    def _handle_input_change(self, e):
        """Handle manual color input."""
        # Get the value without #
        hex_value = e.control.value.strip()
        
        # Validate hex color
        if self._is_valid_hex(hex_value):
            color = f"#{hex_value}"
            self._update_color(color)
            
    def _is_valid_hex(self, hex_str: str) -> bool:
        """Check if string is valid hex color."""
        if len(hex_str) not in [3, 6]:
            return False
            
        try:
            int(hex_str, 16)
            return True
        except ValueError:
            return False
            
    def _select_color(self, color: str):
        """Handle preset color selection."""
        self._update_color(color)
        
        # Update input field if exists
        if hasattr(self, '_color_input'):
            self._color_input.value = color[1:] if color.startswith("#") else color
            self._color_input.update()
            
    def _update_color(self, color: str):
        """Update the selected color."""
        self._value = color
        self._color_display.bgcolor = color
        self._color_display.update()
        
        # Update preset selection borders
        if self._show_presets:
            preset_grid = self.content.controls[-1].content
            for i, chip in enumerate(preset_grid.controls):
                if i < len(self._preset_colors):
                    chip.border = ft.border.all(
                        2,
                        ft.Colors.PRIMARY if self._preset_colors[i] == color else ft.Colors.TRANSPARENT
                    )
            preset_grid.update()
            
        if self._on_change:
            self._on_change(color)
            
    @property
    def value(self) -> str:
        """Get current color value."""
        return self._value
        
    @value.setter
    def value(self, color: str):
        """Set color value."""
        self._update_color(color)
        if hasattr(self, '_color_input'):
            self._color_input.value = color[1:] if color.startswith("#") else color
            self._color_input.update()
            
    def add_preset(self, color: str):
        """Add a color to presets."""
        if color not in self._preset_colors:
            self._preset_colors.append(color)
            # Recreate preset grid
            # This would require rebuilding the grid