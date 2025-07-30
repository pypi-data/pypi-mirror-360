"""
Themed button components for essencia.

This module provides theme-aware button controls with consistent styling.
"""

from typing import Optional, Callable, List
import flet as ft

from .base import ThemedControl, ControlConfig, get_controls_config, DefaultTheme


class ThemedElevatedButton(ThemedControl):
    """Theme-aware elevated button with consistent styling."""
    
    def __init__(self,
                 text: str = "",
                 icon: Optional[str] = None,
                 on_click: Optional[Callable] = None,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 style: Optional[ft.ButtonStyle] = None,
                 autofocus: bool = False,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.text = text
        self.icon = icon
        self.on_click = on_click
        self.width = width
        self.height = height
        self.style = style
        self.autofocus = autofocus
    
    def build(self) -> ft.ElevatedButton:
        """Build the themed elevated button."""
        theme = self.theme or DefaultTheme()
        
        # Create button style if not provided
        if not self.style:
            self.style = ft.ButtonStyle(
                color={
                    ft.MaterialState.DEFAULT: theme.on_primary,
                    ft.MaterialState.HOVERED: theme.on_primary,
                    ft.MaterialState.FOCUSED: theme.on_primary,
                    ft.MaterialState.PRESSED: theme.on_primary,
                    ft.MaterialState.DISABLED: theme.on_surface_variant,
                },
                bgcolor={
                    ft.MaterialState.DEFAULT: theme.primary,
                    ft.MaterialState.HOVERED: theme.primary,
                    ft.MaterialState.FOCUSED: theme.primary,
                    ft.MaterialState.PRESSED: theme.primary_container,
                    ft.MaterialState.DISABLED: theme.surface_variant,
                },
                overlay_color={
                    ft.MaterialState.HOVERED: theme.on_primary + "20",
                    ft.MaterialState.FOCUSED: theme.on_primary + "30",
                    ft.MaterialState.PRESSED: theme.on_primary + "40",
                },
                elevation={
                    ft.MaterialState.DEFAULT: get_controls_config().default_elevation,
                    ft.MaterialState.HOVERED: get_controls_config().default_elevation + 2,
                    ft.MaterialState.PRESSED: 0,
                    ft.MaterialState.DISABLED: 0,
                },
                animation_duration=get_controls_config().animation_duration,
                shape=ft.RoundedRectangleBorder(radius=get_controls_config().default_border_radius),
            )
        
        self._control = ft.ElevatedButton(
            text=self.text,
            icon=self.icon,
            on_click=self.on_click,
            width=self.width,
            height=self.height,
            style=self.style,
            autofocus=self.autofocus,
            visible=self.config.visible,
            disabled=self.config.disabled,
            tooltip=self.config.tooltip,
            data=self.config.data,
        )
        
        return self._control


class ThemedTextButton(ThemedControl):
    """Theme-aware text button with consistent styling."""
    
    def __init__(self,
                 text: str = "",
                 icon: Optional[str] = None,
                 on_click: Optional[Callable] = None,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 style: Optional[ft.ButtonStyle] = None,
                 autofocus: bool = False,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.text = text
        self.icon = icon
        self.on_click = on_click
        self.width = width
        self.height = height
        self.style = style
        self.autofocus = autofocus
    
    def build(self) -> ft.TextButton:
        """Build the themed text button."""
        theme = self.theme or DefaultTheme()
        
        # Create button style if not provided
        if not self.style:
            self.style = ft.ButtonStyle(
                color={
                    ft.MaterialState.DEFAULT: theme.primary,
                    ft.MaterialState.HOVERED: theme.primary,
                    ft.MaterialState.FOCUSED: theme.primary,
                    ft.MaterialState.PRESSED: theme.primary,
                    ft.MaterialState.DISABLED: theme.on_surface_variant,
                },
                overlay_color={
                    ft.MaterialState.HOVERED: theme.primary + "10",
                    ft.MaterialState.FOCUSED: theme.primary + "20",
                    ft.MaterialState.PRESSED: theme.primary + "30",
                },
                animation_duration=get_controls_config().animation_duration,
                shape=ft.RoundedRectangleBorder(radius=get_controls_config().default_border_radius),
            )
        
        self._control = ft.TextButton(
            text=self.text,
            icon=self.icon,
            on_click=self.on_click,
            width=self.width,
            height=self.height,
            style=self.style,
            autofocus=self.autofocus,
            visible=self.config.visible,
            disabled=self.config.disabled,
            tooltip=self.config.tooltip,
            data=self.config.data,
        )
        
        return self._control


class ThemedOutlinedButton(ThemedControl):
    """Theme-aware outlined button with consistent styling."""
    
    def __init__(self,
                 text: str = "",
                 icon: Optional[str] = None,
                 on_click: Optional[Callable] = None,
                 width: Optional[int] = None,
                 height: Optional[int] = None,
                 style: Optional[ft.ButtonStyle] = None,
                 autofocus: bool = False,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.text = text
        self.icon = icon
        self.on_click = on_click
        self.width = width
        self.height = height
        self.style = style
        self.autofocus = autofocus
    
    def build(self) -> ft.OutlinedButton:
        """Build the themed outlined button."""
        theme = self.theme or DefaultTheme()
        
        # Create button style if not provided
        if not self.style:
            self.style = ft.ButtonStyle(
                color={
                    ft.MaterialState.DEFAULT: theme.primary,
                    ft.MaterialState.HOVERED: theme.primary,
                    ft.MaterialState.FOCUSED: theme.primary,
                    ft.MaterialState.PRESSED: theme.primary,
                    ft.MaterialState.DISABLED: theme.on_surface_variant,
                },
                side={
                    ft.MaterialState.DEFAULT: ft.BorderSide(1, theme.outline),
                    ft.MaterialState.HOVERED: ft.BorderSide(1, theme.primary),
                    ft.MaterialState.FOCUSED: ft.BorderSide(2, theme.primary),
                    ft.MaterialState.PRESSED: ft.BorderSide(2, theme.primary),
                    ft.MaterialState.DISABLED: ft.BorderSide(1, theme.surface_variant),
                },
                overlay_color={
                    ft.MaterialState.HOVERED: theme.primary + "10",
                    ft.MaterialState.FOCUSED: theme.primary + "20",
                    ft.MaterialState.PRESSED: theme.primary + "30",
                },
                animation_duration=get_controls_config().animation_duration,
                shape=ft.RoundedRectangleBorder(radius=get_controls_config().default_border_radius),
            )
        
        self._control = ft.OutlinedButton(
            text=self.text,
            icon=self.icon,
            on_click=self.on_click,
            width=self.width,
            height=self.height,
            style=self.style,
            autofocus=self.autofocus,
            visible=self.config.visible,
            disabled=self.config.disabled,
            tooltip=self.config.tooltip,
            data=self.config.data,
        )
        
        return self._control


class ThemedIconButton(ThemedControl):
    """Theme-aware icon button with consistent styling."""
    
    def __init__(self,
                 icon: str,
                 on_click: Optional[Callable] = None,
                 icon_size: Optional[int] = None,
                 icon_color: Optional[str] = None,
                 bgcolor: Optional[str] = None,
                 style: Optional[ft.ButtonStyle] = None,
                 autofocus: bool = False,
                 selected: bool = False,
                 selected_icon: Optional[str] = None,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.icon = icon
        self.on_click = on_click
        self.icon_size = icon_size
        self.icon_color = icon_color
        self.bgcolor = bgcolor
        self.style = style
        self.autofocus = autofocus
        self.selected = selected
        self.selected_icon = selected_icon
    
    def build(self) -> ft.IconButton:
        """Build the themed icon button."""
        theme = self.theme or DefaultTheme()
        
        # Set default colors if not provided
        if not self.icon_color:
            self.icon_color = theme.on_surface
        
        # Create button style if not provided
        if not self.style:
            self.style = ft.ButtonStyle(
                color={
                    ft.MaterialState.DEFAULT: self.icon_color,
                    ft.MaterialState.HOVERED: theme.primary,
                    ft.MaterialState.FOCUSED: theme.primary,
                    ft.MaterialState.PRESSED: theme.primary,
                    ft.MaterialState.DISABLED: theme.on_surface_variant,
                    ft.MaterialState.SELECTED: theme.primary,
                },
                bgcolor={
                    ft.MaterialState.HOVERED: theme.primary + "20",
                    ft.MaterialState.FOCUSED: theme.primary + "30",
                    ft.MaterialState.PRESSED: theme.primary + "40",
                    ft.MaterialState.SELECTED: theme.primary_container,
                } if self.bgcolor is None else None,
                overlay_color={
                    ft.MaterialState.HOVERED: theme.on_surface + "10",
                    ft.MaterialState.FOCUSED: theme.on_surface + "20",
                    ft.MaterialState.PRESSED: theme.on_surface + "30",
                },
                animation_duration=get_controls_config().animation_duration,
            )
        
        self._control = ft.IconButton(
            icon=self.icon,
            on_click=self.on_click,
            icon_size=self.icon_size,
            bgcolor=self.bgcolor,
            style=self.style,
            autofocus=self.autofocus,
            selected=self.selected,
            selected_icon=self.selected_icon,
            visible=self.config.visible,
            disabled=self.config.disabled,
            tooltip=self.config.tooltip,
            data=self.config.data,
        )
        
        return self._control


class ThemedFloatingActionButton(ThemedControl):
    """Theme-aware floating action button with consistent styling."""
    
    def __init__(self,
                 icon: Optional[str] = None,
                 text: Optional[str] = None,
                 on_click: Optional[Callable] = None,
                 bgcolor: Optional[str] = None,
                 foreground_color: Optional[str] = None,
                 elevation: Optional[int] = None,
                 mini: bool = False,
                 autofocus: bool = False,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.icon = icon
        self.text = text
        self.on_click = on_click
        self.bgcolor = bgcolor
        self.foreground_color = foreground_color
        self.elevation = elevation
        self.mini = mini
        self.autofocus = autofocus
    
    def build(self) -> ft.FloatingActionButton:
        """Build the themed floating action button."""
        theme = self.theme or DefaultTheme()
        
        # Set default colors if not provided
        if not self.bgcolor:
            self.bgcolor = theme.primary
        if not self.foreground_color:
            self.foreground_color = theme.on_primary
        if self.elevation is None:
            self.elevation = get_controls_config().default_elevation + 2
        
        self._control = ft.FloatingActionButton(
            icon=self.icon,
            text=self.text,
            on_click=self.on_click,
            bgcolor=self.bgcolor,
            foreground_color=self.foreground_color,
            elevation=self.elevation,
            mini=self.mini,
            autofocus=self.autofocus,
            visible=self.config.visible,
            disabled=self.config.disabled,
            tooltip=self.config.tooltip,
            data=self.config.data,
        )
        
        return self._control


class ButtonGroup(ThemedControl):
    """Group of buttons with consistent spacing and styling."""
    
    def __init__(self,
                 buttons: List[ThemedControl],
                 spacing: Optional[int] = None,
                 alignment: ft.MainAxisAlignment = ft.MainAxisAlignment.START,
                 vertical: bool = False,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.buttons = buttons
        self.spacing = spacing or get_controls_config().default_spacing
        self.alignment = alignment
        self.vertical = vertical
    
    def build(self) -> ft.Control:
        """Build the button group."""
        button_controls = [button.build() for button in self.buttons]
        
        if self.vertical:
            self._control = ft.Column(
                controls=button_controls,
                spacing=self.spacing,
                alignment=self.alignment,
                visible=self.config.visible,
                disabled=self.config.disabled,
            )
        else:
            self._control = ft.Row(
                controls=button_controls,
                spacing=self.spacing,
                alignment=self.alignment,
                visible=self.config.visible,
                disabled=self.config.disabled,
            )
        
        return self._control