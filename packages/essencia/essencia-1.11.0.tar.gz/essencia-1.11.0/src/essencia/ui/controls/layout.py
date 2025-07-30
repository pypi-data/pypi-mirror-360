"""
Layout components for essencia.

This module provides theme-aware layout components for organizing UI elements.
"""

from typing import Optional, List, Any, Union
import flet as ft

from .base import ThemedControl, ControlConfig, get_controls_config, DefaultTheme


class Panel(ThemedControl):
    """Theme-aware panel container with consistent styling."""
    
    def __init__(self,
                 content: Optional[ft.Control] = None,
                 title: Optional[str] = None,
                 width: Optional[Union[int, float]] = None,
                 height: Optional[Union[int, float]] = None,
                 padding: Optional[Union[int, ft.padding.Padding]] = None,
                 margin: Optional[Union[int, ft.margin.Margin]] = None,
                 bgcolor: Optional[str] = None,
                 border: Optional[ft.border.Border] = None,
                 border_radius: Optional[Union[int, ft.border_radius.BorderRadius]] = None,
                 elevation: Optional[int] = None,
                 expand: Union[bool, int] = False,
                 alignment: Optional[ft.alignment.Alignment] = None,
                 gradient: Optional[Union[ft.LinearGradient, ft.RadialGradient, ft.SweepGradient]] = None,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.content = content
        self.title = title
        self.width = width
        self.height = height
        self.padding = padding
        self.margin = margin
        self.bgcolor = bgcolor
        self.border = border
        self.border_radius = border_radius
        self.elevation = elevation
        self.expand = expand
        self.alignment = alignment
        self.gradient = gradient
    
    def build(self) -> ft.Container:
        """Build the themed panel."""
        theme = self.theme or DefaultTheme()
        controls_config = get_controls_config()
        
        # Set defaults
        if self.bgcolor is None:
            self.bgcolor = theme.surface
        if self.padding is None:
            self.padding = controls_config.default_padding
        if self.border_radius is None:
            self.border_radius = controls_config.default_border_radius
        if self.elevation is None and not self.border:
            self.elevation = controls_config.default_elevation
        
        # Create content with optional title
        panel_content = self.content
        if self.title:
            title_text = ft.Text(
                self.title,
                size=18,
                weight=ft.FontWeight.W_500,
                color=theme.on_surface,
            )
            if self.content:
                panel_content = ft.Column(
                    controls=[
                        title_text,
                        ft.Divider(color=theme.outline, height=1),
                        self.content,
                    ],
                    spacing=controls_config.default_spacing,
                )
            else:
                panel_content = title_text
        
        self._control = ft.Container(
            content=panel_content,
            width=self.width,
            height=self.height,
            padding=self.padding,
            margin=self.margin,
            bgcolor=self.bgcolor,
            border=self.border,
            border_radius=self.border_radius,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=self.elevation * 2,
                color=theme.shadow + "20",
                offset=ft.Offset(0, self.elevation),
            ) if self.elevation else None,
            expand=self.expand,
            alignment=self.alignment,
            gradient=self.gradient,
            visible=self.config.visible,
            disabled=self.config.disabled,
            tooltip=self.config.tooltip,
            data=self.config.data,
        )
        
        return self._control


class Section(ThemedControl):
    """Theme-aware section container for grouping related content."""
    
    def __init__(self,
                 title: str,
                 content: Optional[ft.Control] = None,
                 subtitle: Optional[str] = None,
                 collapsible: bool = False,
                 initially_expanded: bool = True,
                 padding: Optional[Union[int, ft.padding.Padding]] = None,
                 spacing: Optional[int] = None,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.title = title
        self.content = content
        self.subtitle = subtitle
        self.collapsible = collapsible
        self.initially_expanded = initially_expanded
        self.padding = padding
        self.spacing = spacing
        self._expanded = initially_expanded
    
    def build(self) -> ft.Control:
        """Build the themed section."""
        theme = self.theme or DefaultTheme()
        controls_config = get_controls_config()
        
        # Set defaults
        if self.padding is None:
            self.padding = controls_config.default_padding
        if self.spacing is None:
            self.spacing = controls_config.default_spacing
        
        # Create header
        header_controls = [
            ft.Text(
                self.title,
                size=16,
                weight=ft.FontWeight.W_600,
                color=theme.on_surface,
            )
        ]
        
        if self.subtitle:
            header_controls.append(
                ft.Text(
                    self.subtitle,
                    size=12,
                    color=theme.on_surface_variant,
                )
            )
        
        header = ft.Column(
            controls=header_controls,
            spacing=2,
        )
        
        if self.collapsible:
            # Create expandable section
            def toggle_expand(e):
                self._expanded = not self._expanded
                content_container.visible = self._expanded
                expand_icon.name = ft.Icons.EXPAND_MORE if self._expanded else ft.Icons.CHEVRON_RIGHT
                self._control.update()
            
            expand_icon = ft.Icon(
                name=ft.Icons.EXPAND_MORE if self._expanded else ft.Icons.CHEVRON_RIGHT,
                color=theme.on_surface_variant,
                size=20,
            )
            
            header_row = ft.Row(
                controls=[
                    header,
                    expand_icon,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
            
            header_container = ft.Container(
                content=header_row,
                on_click=toggle_expand,
                padding=ft.padding.symmetric(vertical=8),
            )
            
            content_container = ft.Container(
                content=self.content,
                visible=self._expanded,
                animate_opacity=controls_config.animation_duration,
                padding=ft.padding.only(top=8) if self.content else None,
            )
            
            self._control = ft.Container(
                content=ft.Column(
                    controls=[
                        header_container,
                        content_container,
                    ] if self.content else [header_container],
                    spacing=0,
                ),
                padding=self.padding,
                visible=self.config.visible,
                disabled=self.config.disabled,
                tooltip=self.config.tooltip,
                data=self.config.data,
            )
        else:
            # Non-collapsible section
            section_controls = [header]
            if self.content:
                section_controls.append(self.content)
            
            self._control = ft.Container(
                content=ft.Column(
                    controls=section_controls,
                    spacing=self.spacing,
                ),
                padding=self.padding,
                visible=self.config.visible,
                disabled=self.config.disabled,
                tooltip=self.config.tooltip,
                data=self.config.data,
            )
        
        return self._control


class Grid(ThemedControl):
    """Responsive grid layout component."""
    
    def __init__(self,
                 controls: List[ft.Control],
                 columns: int = 2,
                 spacing: Optional[int] = None,
                 run_spacing: Optional[int] = None,
                 child_aspect_ratio: float = 1.0,
                 main_axis_extent: Optional[int] = None,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.controls = controls
        self.columns = columns
        self.spacing = spacing
        self.run_spacing = run_spacing
        self.child_aspect_ratio = child_aspect_ratio
        self.main_axis_extent = main_axis_extent
    
    def build(self) -> ft.GridView:
        """Build the grid layout."""
        controls_config = get_controls_config()
        
        # Set defaults
        if self.spacing is None:
            self.spacing = controls_config.default_spacing
        if self.run_spacing is None:
            self.run_spacing = self.spacing
        
        self._control = ft.GridView(
            controls=self.controls,
            runs_count=self.columns,
            spacing=self.spacing,
            run_spacing=self.run_spacing,
            child_aspect_ratio=self.child_aspect_ratio,
            max_extent=self.main_axis_extent,
            visible=self.config.visible,
            disabled=self.config.disabled,
        )
        
        return self._control


class FlexLayout(ThemedControl):
    """Flexible layout with wrap support."""
    
    def __init__(self,
                 controls: List[ft.Control],
                 wrap: bool = True,
                 spacing: Optional[int] = None,
                 run_spacing: Optional[int] = None,
                 alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.START,
                 vertical_alignment: ft.CrossAxisAlignment = ft.CrossAxisAlignment.START,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.controls = controls
        self.wrap = wrap
        self.spacing = spacing
        self.run_spacing = run_spacing
        self.alignment = alignment
        self.vertical_alignment = vertical_alignment
    
    def build(self) -> ft.Row:
        """Build the flex layout."""
        controls_config = get_controls_config()
        
        # Set defaults
        if self.spacing is None:
            self.spacing = controls_config.default_spacing
        if self.run_spacing is None:
            self.run_spacing = self.spacing
        
        self._control = ft.Row(
            controls=self.controls,
            wrap=self.wrap,
            spacing=self.spacing,
            run_spacing=self.run_spacing,
            alignment=self.alignment,
            vertical_alignment=self.vertical_alignment,
            visible=self.config.visible,
            disabled=self.config.disabled,
        )
        
        return self._control


class TabLayout(ThemedControl):
    """Tab-based layout component."""
    
    def __init__(self,
                 tabs: List[ft.Tab],
                 selected_index: int = 0,
                 animation_duration: Optional[int] = None,
                 on_change: Optional[Any] = None,
                 scrollable: bool = False,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.tabs = tabs
        self.selected_index = selected_index
        self.animation_duration = animation_duration
        self.on_change = on_change
        self.scrollable = scrollable
    
    def build(self) -> ft.Tabs:
        """Build the tab layout."""
        theme = self.theme or DefaultTheme()
        controls_config = get_controls_config()
        
        # Set defaults
        if self.animation_duration is None:
            self.animation_duration = controls_config.animation_duration
        
        # Apply theme to tabs
        for tab in self.tabs:
            if not hasattr(tab, 'text_color'):
                tab.text_color = theme.on_surface
            if not hasattr(tab, 'icon_color'):
                tab.icon_color = theme.on_surface
        
        self._control = ft.Tabs(
            tabs=self.tabs,
            selected_index=self.selected_index,
            animation_duration=self.animation_duration,
            on_change=self.on_change,
            scrollable=self.scrollable,
            label_color=theme.primary,
            unselected_label_color=theme.on_surface_variant,
            indicator_color=theme.primary,
            divider_color=theme.outline,
            visible=self.config.visible,
            disabled=self.config.disabled,
        )
        
        return self._control


class SplitView(ThemedControl):
    """Split view layout with resizable panels."""
    
    def __init__(self,
                 left: Optional[ft.Control] = None,
                 right: Optional[ft.Control] = None,
                 horizontal: bool = True,
                 split_ratio: float = 0.5,
                 min_split_ratio: float = 0.2,
                 max_split_ratio: float = 0.8,
                 divider_thickness: int = 1,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.left = left
        self.right = right
        self.horizontal = horizontal
        self.split_ratio = split_ratio
        self.min_split_ratio = min_split_ratio
        self.max_split_ratio = max_split_ratio
        self.divider_thickness = divider_thickness
    
    def build(self) -> ft.Container:
        """Build the split view."""
        theme = self.theme or DefaultTheme()
        
        # Create divider
        divider = ft.Container(
            bgcolor=theme.outline,
            width=self.divider_thickness if self.horizontal else None,
            height=self.divider_thickness if not self.horizontal else None,
            expand=False,
        )
        
        # Create panels
        if self.horizontal:
            left_panel = ft.Container(
                content=self.left,
                expand=self.split_ratio,
            )
            right_panel = ft.Container(
                content=self.right,
                expand=1 - self.split_ratio,
            )
            
            self._control = ft.Row(
                controls=[left_panel, divider, right_panel],
                spacing=0,
                expand=True,
                visible=self.config.visible,
                disabled=self.config.disabled,
            )
        else:
            top_panel = ft.Container(
                content=self.left,  # Top content
                expand=self.split_ratio,
            )
            bottom_panel = ft.Container(
                content=self.right,  # Bottom content
                expand=1 - self.split_ratio,
            )
            
            self._control = ft.Column(
                controls=[top_panel, divider, bottom_panel],
                spacing=0,
                expand=True,
                visible=self.config.visible,
                disabled=self.config.disabled,
            )
        
        return self._control


class ResponsiveLayout(ThemedControl):
    """Responsive layout that adapts to screen size."""
    
    def __init__(self,
                 mobile: Optional[ft.Control] = None,
                 tablet: Optional[ft.Control] = None,
                 desktop: Optional[ft.Control] = None,
                 mobile_breakpoint: int = 600,
                 tablet_breakpoint: int = 1024,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.mobile = mobile
        self.tablet = tablet
        self.desktop = desktop
        self.mobile_breakpoint = mobile_breakpoint
        self.tablet_breakpoint = tablet_breakpoint
    
    def build(self) -> ft.ResponsiveRow:
        """Build the responsive layout."""
        # Create responsive content
        controls = []
        
        if self.mobile:
            controls.append(
                ft.Container(
                    content=self.mobile,
                    col={"sm": 12, "md": 0, "xl": 0},
                )
            )
        
        if self.tablet:
            controls.append(
                ft.Container(
                    content=self.tablet,
                    col={"sm": 0, "md": 12, "xl": 0},
                )
            )
        
        if self.desktop:
            controls.append(
                ft.Container(
                    content=self.desktop,
                    col={"sm": 0, "md": 0, "xl": 12},
                )
            )
        
        self._control = ft.ResponsiveRow(
            controls=controls,
            visible=self.config.visible,
            disabled=self.config.disabled,
        )
        
        return self._control