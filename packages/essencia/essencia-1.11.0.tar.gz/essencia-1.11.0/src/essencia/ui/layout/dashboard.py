"""
Dashboard layout component for complex application interfaces.
"""

from typing import Optional, Union, Callable, Dict, Any
import flet as ft


class Dashboard(ft.ResponsiveRow):
    """Primary layout component for dashboard interfaces.
    
    Provides a responsive multi-section layout structure with:
    - Header area (full width)
    - Sidebar column (navigation/actions)
    - Main content area
    - Optional footer
    
    The layout automatically adapts to different screen sizes, collapsing
    the sidebar on mobile devices.
    
    Example:
        ```python
        dashboard = Dashboard(
            header_height=80,
            sidebar_width={"sm": 12, "md": 4, "lg": 3},
            show_sidebar=True
        )
        
        # Add header content
        dashboard.set_header(ft.Text("Dashboard Title", size=24))
        
        # Add sidebar navigation
        dashboard.add_to_sidebar(ft.ElevatedButton("Home"))
        dashboard.add_to_sidebar(ft.ElevatedButton("Settings"))
        
        # Set main content
        dashboard.set_body(MyContentView())
        ```
    
    Args:
        header_height (Optional[int]): Fixed height for header area
        sidebar_width (Union[int, dict]): Responsive width for sidebar
        body_width (Union[int, dict]): Responsive width for body (auto-calculated if not set)
        show_header (bool): Whether to show header section (default: True)
        show_sidebar (bool): Whether to show sidebar section (default: True)
        show_footer (bool): Whether to show footer section (default: False)
        spacing (int): Space between sections (default: 10)
        padding (Union[int, ft.Padding]): Dashboard padding (default: 20)
        user_context (Optional[Callable]): Function to get user context
        **kwargs: Additional arguments passed to ResponsiveRow
    """
    def __init__(
        self,
        header_height: Optional[int] = None,
        sidebar_width: Union[int, Dict[str, int]] = {"sm": 12, "md": 4, "lg": 3},
        body_width: Optional[Union[int, Dict[str, int]]] = None,
        show_header: bool = True,
        show_sidebar: bool = True, 
        show_footer: bool = False,
        spacing: int = 10,
        padding: Union[int, ft.Padding] = 20,
        user_context: Optional[Callable] = None,
        **kwargs
    ):
        super().__init__(spacing=spacing, **kwargs)
        
        self._user_context = user_context
        self._sidebar_width = sidebar_width
        self._body_width = body_width or self._calculate_body_width(sidebar_width)
        self._show_header = show_header
        self._show_sidebar = show_sidebar
        self._show_footer = show_footer
        
        # Convert padding to Padding object
        if isinstance(padding, int):
            padding = ft.padding.all(padding)
        
        # Initialize sections
        if show_header:
            self.header = ft.ResponsiveRow(spacing=10)
            self.header_container = ft.Container(
                content=self.header,
                col=12,
                height=header_height,
                padding=padding,
                bgcolor=ft.Colors.SURFACE,
                border_radius=ft.border_radius.all(10)
            )
            self.controls.append(self.header_container)
        
        # Create main content row
        self.main_row = ft.ResponsiveRow(spacing=spacing)
        
        if show_sidebar:
            self.sidebar = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
            self.sidebar_container = ft.Container(
                content=self.sidebar,
                col=sidebar_width,
                padding=padding,
                bgcolor=ft.Colors.SURFACE,
                border_radius=ft.border_radius.all(10)
            )
            self.main_row.controls.append(self.sidebar_container)
        
        # Body section
        self.body = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO)
        self.body_container = ft.Container(
            content=self.body,
            col=self._body_width,
            padding=padding,
            bgcolor=ft.Colors.SURFACE,
            border_radius=ft.border_radius.all(10)
        )
        self.main_row.controls.append(self.body_container)
        
        # Add main row to dashboard
        self.controls.append(self.main_row)
        
        # Footer section
        if show_footer:
            self.footer = ft.ResponsiveRow(spacing=10)
            self.footer_container = ft.Container(
                content=self.footer,
                col=12,
                padding=padding,
                bgcolor=ft.Colors.SURFACE,
                border_radius=ft.border_radius.all(10)
            )
            self.controls.append(self.footer_container)
    
    def _calculate_body_width(self, sidebar_width: Union[int, Dict[str, int]]) -> Union[int, Dict[str, int]]:
        """Calculate body width based on sidebar width."""
        if isinstance(sidebar_width, int):
            return 12 - sidebar_width
        else:
            return {
                size: 12 - width for size, width in sidebar_width.items()
            }
    
    @property
    def user(self) -> Optional[Any]:
        """Get the current user context if available."""
        if self._user_context:
            return self._user_context()
        return None
    
    # Header methods
    def set_header(self, content: Union[ft.Control, list]):
        """Set the header content."""
        if not self._show_header:
            return
            
        self.header.controls.clear()
        if isinstance(content, list):
            self.header.controls.extend(content)
        else:
            self.header.controls.append(ft.Container(content, col=12))
    
    def add_to_header(self, control: ft.Control, col: Optional[Union[int, dict]] = None):
        """Add a control to the header."""
        if not self._show_header:
            return
            
        container = ft.Container(content=control, col=col or 12)
        self.header.controls.append(container)
    
    def clear_header(self):
        """Clear all header content."""
        if self._show_header:
            self.header.controls.clear()
    
    # Sidebar methods
    def set_sidebar(self, content: Union[ft.Control, list]):
        """Set the sidebar content."""
        if not self._show_sidebar:
            return
            
        self.sidebar.controls.clear()
        if isinstance(content, list):
            self.sidebar.controls.extend(content)
        else:
            self.sidebar.controls.append(content)
    
    def add_to_sidebar(self, control: ft.Control):
        """Add a control to the sidebar."""
        if not self._show_sidebar:
            return
            
        self.sidebar.controls.append(control)
    
    def clear_sidebar(self):
        """Clear all sidebar content."""
        if self._show_sidebar:
            self.sidebar.controls.clear()
    
    # Body methods  
    def set_body(self, content: Union[ft.Control, list]):
        """Set the main body content."""
        self.body.controls.clear()
        if isinstance(content, list):
            self.body.controls.extend(content)
        else:
            self.body.controls.append(content)
    
    def add_to_body(self, control: ft.Control):
        """Add a control to the body."""
        self.body.controls.append(control)
    
    def clear_body(self):
        """Clear all body content."""
        self.body.controls.clear()
    
    # Footer methods
    def set_footer(self, content: Union[ft.Control, list]):
        """Set the footer content."""
        if not self._show_footer:
            return
            
        self.footer.controls.clear()
        if isinstance(content, list):
            self.footer.controls.extend(content)
        else:
            self.footer.controls.append(ft.Container(content, col=12))
    
    def add_to_footer(self, control: ft.Control, col: Optional[Union[int, dict]] = None):
        """Add a control to the footer."""
        if not self._show_footer:
            return
            
        container = ft.Container(content=control, col=col or 12)
        self.footer.controls.append(container)
    
    def clear_footer(self):
        """Clear all footer content."""
        if self._show_footer:
            self.footer.controls.clear()
    
    # Utility methods
    def clear_all(self):
        """Clear all sections."""
        self.clear_header()
        self.clear_sidebar()
        self.clear_body()
        self.clear_footer()
    
    def toggle_sidebar(self):
        """Toggle sidebar visibility."""
        if self._show_sidebar:
            self.sidebar_container.visible = not self.sidebar_container.visible
            # Adjust body width when sidebar is hidden
            if not self.sidebar_container.visible:
                self.body_container.col = 12
            else:
                self.body_container.col = self._body_width
            
            if hasattr(self, 'update'):
                self.update()