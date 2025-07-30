"""
Theme-aware components for essencia.

This module provides components that automatically adapt to theme changes
and provide consistent styling across the application.
"""

from typing import Any, List, Optional, Union
import flet as ft

from .base import ThemedControl, ControlConfig, get_controls_config, DefaultTheme


class ThemedComponent:
    """Mixin class for components that need theme awareness."""
    
    def apply_theme(self, control: ft.Control, theme: Any = None) -> None:
        """Apply theme to a control."""
        if theme is None:
            theme = get_controls_config().theme_provider or DefaultTheme()
        
        # Common theme properties
        theme_props = {
            'bgcolor': getattr(control, 'bgcolor', None),
            'color': getattr(control, 'color', None),
            'border_color': getattr(control, 'border_color', None),
        }
        
        # Apply based on control type
        if isinstance(control, ft.Container):
            if not control.bgcolor:
                control.bgcolor = theme.surface
        
        elif isinstance(control, ft.Text):
            if not control.color:
                control.color = theme.on_surface
        
        elif isinstance(control, ft.Icon):
            if not control.color:
                control.color = theme.on_surface
        
        elif isinstance(control, ft.Card):
            if not control.color:
                control.color = theme.surface
            if hasattr(control, 'shadow_color'):
                control.shadow_color = theme.shadow
        
        # Recursively apply to children
        if hasattr(control, 'content') and control.content:
            self.apply_theme(control.content, theme)
        
        if hasattr(control, 'controls') and control.controls:
            for child in control.controls:
                self.apply_theme(child, theme)


class ThemedContainer(ThemedControl, ThemedComponent):
    """Theme-aware container with automatic theme application."""
    
    def __init__(self,
                 content: Optional[ft.Control] = None,
                 width: Optional[Union[int, float]] = None,
                 height: Optional[Union[int, float]] = None,
                 padding: Optional[Union[int, ft.padding.Padding]] = None,
                 margin: Optional[Union[int, ft.margin.Margin]] = None,
                 alignment: Optional[ft.alignment.Alignment] = None,
                 bgcolor: Optional[str] = None,
                 gradient: Optional[Union[ft.LinearGradient, ft.RadialGradient, ft.SweepGradient]] = None,
                 border: Optional[ft.border.Border] = None,
                 border_radius: Optional[Union[int, ft.border_radius.BorderRadius]] = None,
                 shadow: Optional[ft.BoxShadow] = None,
                 animate: Optional[ft.Animation] = None,
                 expand: Union[bool, int] = False,
                 config: Optional[ControlConfig] = None):
        ThemedControl.__init__(self, config)
        self.content = content
        self.width = width
        self.height = height
        self.padding = padding
        self.margin = margin
        self.alignment = alignment
        self.bgcolor = bgcolor
        self.gradient = gradient
        self.border = border
        self.border_radius = border_radius
        self.shadow = shadow
        self.animate = animate
        self.expand = expand
    
    def build(self) -> ft.Container:
        """Build the themed container."""
        theme = self.theme or DefaultTheme()
        controls_config = get_controls_config()
        
        # Apply theme to content
        if self.content:
            self.apply_theme(self.content, theme)
        
        # Set defaults
        if self.bgcolor is None and not self.gradient:
            self.bgcolor = theme.surface
        
        if self.border_radius is None:
            self.border_radius = controls_config.default_border_radius
        
        if self.shadow is None and not self.border:
            self.shadow = ft.BoxShadow(
                spread_radius=0,
                blur_radius=controls_config.default_elevation * 2,
                color=theme.shadow + "20",
                offset=ft.Offset(0, controls_config.default_elevation),
            )
        
        self._control = ft.Container(
            content=self.content,
            width=self.width,
            height=self.height,
            padding=self.padding,
            margin=self.margin,
            alignment=self.alignment,
            bgcolor=self.bgcolor,
            gradient=self.gradient,
            border=self.border,
            border_radius=self.border_radius,
            shadow=self.shadow,
            animate=self.animate,
            expand=self.expand,
            visible=self.config.visible,
            disabled=self.config.disabled,
            tooltip=self.config.tooltip,
            data=self.config.data,
        )
        
        return self._control


class ThemedCard(ThemedControl, ThemedComponent):
    """Theme-aware card component."""
    
    def __init__(self,
                 content: Optional[ft.Control] = None,
                 elevation: Optional[int] = None,
                 color: Optional[str] = None,
                 shadow_color: Optional[str] = None,
                 surface_tint_color: Optional[str] = None,
                 config: Optional[ControlConfig] = None):
        ThemedControl.__init__(self, config)
        self.content = content
        self.elevation = elevation
        self.color = color
        self.shadow_color = shadow_color
        self.surface_tint_color = surface_tint_color
    
    def build(self) -> ft.Card:
        """Build the themed card."""
        theme = self.theme or DefaultTheme()
        controls_config = get_controls_config()
        
        # Apply theme to content
        if self.content:
            self.apply_theme(self.content, theme)
        
        # Set defaults
        if self.elevation is None:
            self.elevation = controls_config.default_elevation
        
        if self.color is None:
            self.color = theme.surface
        
        if self.shadow_color is None:
            self.shadow_color = theme.shadow
        
        self._control = ft.Card(
            content=self.content,
            elevation=self.elevation,
            color=self.color,
            shadow_color=self.shadow_color,
            surface_tint_color=self.surface_tint_color,
            visible=self.config.visible,
            disabled=self.config.disabled,
            tooltip=self.config.tooltip,
            data=self.config.data,
        )
        
        return self._control


class ThemedAppBar(ThemedControl):
    """Theme-aware app bar component."""
    
    def __init__(self,
                 title: Optional[ft.Control] = None,
                 leading: Optional[ft.Control] = None,
                 actions: Optional[List[ft.Control]] = None,
                 bgcolor: Optional[str] = None,
                 leading_width: Optional[int] = None,
                 center_title: bool = False,
                 elevation: Optional[int] = None,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.title = title
        self.leading = leading
        self.actions = actions
        self.bgcolor = bgcolor
        self.leading_width = leading_width
        self.center_title = center_title
        self.elevation = elevation
    
    def build(self) -> ft.AppBar:
        """Build the themed app bar."""
        theme = self.theme or DefaultTheme()
        controls_config = get_controls_config()
        
        # Set defaults
        if self.bgcolor is None:
            self.bgcolor = theme.primary
        
        if self.elevation is None:
            self.elevation = controls_config.default_elevation
        
        # Apply theme to title if it's a Text control
        if isinstance(self.title, ft.Text) and not self.title.color:
            self.title.color = theme.on_primary
        
        self._control = ft.AppBar(
            title=self.title,
            leading=self.leading,
            actions=self.actions,
            bgcolor=self.bgcolor,
            leading_width=self.leading_width,
            center_title=self.center_title,
            elevation=self.elevation,
            visible=self.config.visible,
        )
        
        return self._control


class ThemedNavigationRail(ThemedControl):
    """Theme-aware navigation rail component."""
    
    def __init__(self,
                 destinations: List[ft.NavigationRailDestination],
                 selected_index: int = 0,
                 bgcolor: Optional[str] = None,
                 extended: bool = False,
                 label_type: ft.NavigationRailLabelType = ft.NavigationRailLabelType.ALL,
                 on_change: Optional[Any] = None,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.destinations = destinations
        self.selected_index = selected_index
        self.bgcolor = bgcolor
        self.extended = extended
        self.label_type = label_type
        self.on_change = on_change
    
    def build(self) -> ft.NavigationRail:
        """Build the themed navigation rail."""
        theme = self.theme or DefaultTheme()
        
        # Set defaults
        if self.bgcolor is None:
            self.bgcolor = theme.surface_variant
        
        self._control = ft.NavigationRail(
            destinations=self.destinations,
            selected_index=self.selected_index,
            bgcolor=self.bgcolor,
            extended=self.extended,
            label_type=self.label_type,
            on_change=self.on_change,
            indicator_color=theme.primary_container,
            indicator_shape=ft.StadiumBorder(),
            visible=self.config.visible,
            disabled=self.config.disabled,
        )
        
        return self._control


class ThemedDataTable(ThemedControl):
    """Theme-aware data table component."""
    
    def __init__(self,
                 columns: List[ft.DataColumn],
                 rows: List[ft.DataRow],
                 border: Optional[ft.border.Border] = None,
                 border_radius: Optional[Union[int, ft.border_radius.BorderRadius]] = None,
                 heading_row_color: Optional[Any] = None,
                 data_row_color: Optional[Any] = None,
                 divider_thickness: Optional[float] = None,
                 sort_column_index: Optional[int] = None,
                 sort_ascending: bool = True,
                 show_checkbox_column: bool = False,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.columns = columns
        self.rows = rows
        self.border = border
        self.border_radius = border_radius
        self.heading_row_color = heading_row_color
        self.data_row_color = data_row_color
        self.divider_thickness = divider_thickness
        self.sort_column_index = sort_column_index
        self.sort_ascending = sort_ascending
        self.show_checkbox_column = show_checkbox_column
    
    def build(self) -> ft.DataTable:
        """Build the themed data table."""
        theme = self.theme or DefaultTheme()
        controls_config = get_controls_config()
        
        # Set defaults
        if self.border is None:
            self.border = ft.border.all(1, theme.outline)
        
        if self.border_radius is None:
            self.border_radius = controls_config.default_border_radius
        
        if self.heading_row_color is None:
            self.heading_row_color = ft.colors.with_opacity(0.05, theme.primary)
        
        self._control = ft.DataTable(
            columns=self.columns,
            rows=self.rows,
            border=self.border,
            border_radius=self.border_radius,
            heading_row_color=self.heading_row_color,
            data_row_color=self.data_row_color,
            divider_thickness=self.divider_thickness,
            sort_column_index=self.sort_column_index,
            sort_ascending=self.sort_ascending,
            show_checkbox_column=self.show_checkbox_column,
            visible=self.config.visible,
            disabled=self.config.disabled,
        )
        
        return self._control


def apply_theme_to_control(control: ft.Control, theme: Optional[Any] = None) -> None:
    """Apply theme to any control recursively."""
    component = ThemedComponent()
    component.apply_theme(control, theme)