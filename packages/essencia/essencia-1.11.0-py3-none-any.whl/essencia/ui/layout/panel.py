"""
Panel and Grid components for consistent layout styling.
"""

from typing import Optional, Union, List
import flet as ft


class Panel(ft.Container):
    """A styled container with consistent border and background properties.
    
    Provides a reusable panel component with customizable appearance that
    automatically adapts to the application's theme.
    
    Example:
        ```python
        panel = Panel(
            content=ft.Text("Content"),
            padding=20,
            border_radius=15,
            elevation=2
        )
        ```
    
    Args:
        content (Optional[ft.Control]): The control to display inside the panel
        padding (Union[int, ft.Padding]): Inner padding (default: 10)
        margin (Union[int, ft.Margin]): Outer margin (default: None) 
        bgcolor (Optional[str]): Background color (uses theme surface by default)
        border_color (Optional[str]): Border color (uses theme outline by default)
        border_width (int): Border width in pixels (default: 1)
        border_radius (Union[int, ft.BorderRadius]): Border radius (default: 10)
        elevation (Optional[int]): Shadow elevation level
        **kwargs: Additional arguments passed to Container
    """
    def __init__(
        self,
        content: Optional[ft.Control] = None,
        padding: Union[int, ft.Padding] = 10,
        margin: Optional[Union[int, ft.Margin]] = None,
        bgcolor: Optional[str] = None,
        border_color: Optional[str] = None,
        border_width: int = 1,
        border_radius: Union[int, ft.BorderRadius] = 10,
        elevation: Optional[int] = None,
        **kwargs
    ):
        super().__init__(content=content, **kwargs)
        
        # Configure padding
        if isinstance(padding, int):
            self.padding = ft.padding.all(padding)
        else:
            self.padding = padding
            
        # Configure margin
        if margin:
            if isinstance(margin, int):
                self.margin = ft.margin.all(margin)
            else:
                self.margin = margin
        
        # Configure background
        self.bgcolor = bgcolor
        
        # Configure border
        if border_width > 0 and border_color is not False:
            self.border = ft.border.all(
                width=border_width,
                color=border_color
            )
        
        # Configure border radius
        if isinstance(border_radius, int):
            self.border_radius = ft.border_radius.all(border_radius)
        else:
            self.border_radius = border_radius
            
        # Configure elevation
        if elevation:
            self.shadow = ft.BoxShadow(
                spread_radius=1,
                blur_radius=elevation * 2,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                offset=ft.Offset(0, elevation)
            )
    
    def set_content(self, content: ft.Control):
        """Update the panel's content.
        
        Args:
            content: New content control
        """
        self.content = content
        if hasattr(self, 'update'):
            self.update()


class Grid(Panel):
    """A responsive grid layout container inheriting from Panel.
    
    Provides a responsive grid system with easy methods for adding and
    managing controls in a grid layout.
    
    Example:
        ```python
        grid = Grid(spacing=10)
        
        # Add controls with responsive columns
        grid.add(ft.Text("Item 1"), col={"sm": 12, "md": 6, "lg": 4})
        grid.add(ft.Text("Item 2"), col={"sm": 12, "md": 6, "lg": 4})
        ```
    
    Args:
        spacing (int): Space between grid items (default: 10)
        run_spacing (int): Space between rows (default: 10)
        **kwargs: Additional arguments passed to Panel
    """
    def __init__(
        self,
        spacing: int = 10,
        run_spacing: int = 10,
        **kwargs
    ):
        super().__init__(**kwargs)
        self._spacing = spacing
        self._run_spacing = run_spacing
        self.content = ft.ResponsiveRow(
            spacing=spacing,
            run_spacing=run_spacing
        )
        
    def add(self, control: ft.Control, col: Optional[Union[int, dict]] = None, **kwargs):
        """Add a control to the grid.
        
        Args:
            control: Control to add
            col: Column specification (int or responsive dict)
            **kwargs: Additional container properties
        """
        # Wrap control in container with column spec
        container = ft.Container(
            content=control,
            col=col or 12,
            **kwargs
        )
        self.content.controls.append(container)
        
    def insert(self, index: int, control: ft.Control, col: Optional[Union[int, dict]] = None, **kwargs):
        """Insert a control at a specific position.
        
        Args:
            index: Position to insert at
            control: Control to insert
            col: Column specification (int or responsive dict)
            **kwargs: Additional container properties
        """
        container = ft.Container(
            content=control,
            col=col or 12,
            **kwargs
        )
        self.content.controls.insert(index, container)
        
    def remove(self, control: ft.Control):
        """Remove a control from the grid.
        
        Args:
            control: Control to remove
        """
        # Find and remove the container holding this control
        for container in self.content.controls[:]:
            if container.content == control:
                self.content.controls.remove(container)
                break
                
    def clear(self):
        """Remove all controls from the grid."""
        self.content.controls.clear()
        
    def __len__(self):
        """Get the number of controls in the grid."""
        return len(self.content.controls)
        
    def __getitem__(self, index: int) -> ft.Control:
        """Get a control by index."""
        return self.content.controls[index].content
        
    @property
    def controls(self) -> List[ft.Control]:
        """Get list of all controls in the grid."""
        return [c.content for c in self.content.controls]