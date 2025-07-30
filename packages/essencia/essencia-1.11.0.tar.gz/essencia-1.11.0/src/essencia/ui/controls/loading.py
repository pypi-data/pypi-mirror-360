"""
Loading indicator components for essencia.

This module provides various loading indicators and overlays.
"""

from typing import Optional, Union, List
import flet as ft

from .base import ThemedControl, ControlConfig, get_controls_config, DefaultTheme


class LoadingIndicator(ThemedControl):
    """Theme-aware loading indicator."""
    
    def __init__(self,
                 size: Optional[int] = None,
                 stroke_width: Optional[int] = None,
                 color: Optional[str] = None,
                 tooltip: Optional[str] = None,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.size = size or 40
        self.stroke_width = stroke_width or 4
        self.color = color
        self.tooltip = tooltip or "Carregando..."
    
    def build(self) -> ft.ProgressRing:
        """Build the loading indicator."""
        theme = self.theme or DefaultTheme()
        
        self._control = ft.ProgressRing(
            width=self.size,
            height=self.size,
            stroke_width=self.stroke_width,
            color=self.color or theme.primary,
            tooltip=self.tooltip,
            visible=self.config.visible,
            disabled=self.config.disabled,
        )
        
        return self._control


class LoadingOverlay(ThemedControl):
    """Full-screen loading overlay."""
    
    def __init__(self,
                 message: Optional[str] = None,
                 show_progress: bool = False,
                 progress_value: Optional[float] = None,
                 bgcolor: Optional[str] = None,
                 opacity: float = 0.8,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.message = message or "Carregando..."
        self.show_progress = show_progress
        self.progress_value = progress_value
        self.bgcolor = bgcolor
        self.opacity = opacity
    
    def build(self) -> ft.Container:
        """Build the loading overlay."""
        theme = self.theme or DefaultTheme()
        controls_config = get_controls_config()
        
        # Create loading content
        loading_controls = []
        
        # Add progress indicator
        if self.show_progress and self.progress_value is not None:
            loading_controls.append(
                ft.ProgressBar(
                    value=self.progress_value,
                    width=200,
                    color=theme.primary,
                    bgcolor=theme.surface_variant,
                )
            )
        else:
            loading_controls.append(
                LoadingIndicator(size=60, color=theme.primary).build()
            )
        
        # Add message
        loading_controls.append(
            ft.Text(
                self.message,
                size=16,
                color=theme.on_surface,
                weight=ft.FontWeight.W_500,
                text_align=ft.TextAlign.CENTER,
            )
        )
        
        # Create content container
        content = ft.Container(
            content=ft.Column(
                controls=loading_controls,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=controls_config.default_spacing * 2,
            ),
            bgcolor=theme.surface,
            padding=controls_config.default_padding * 2,
            border_radius=controls_config.default_border_radius,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=20,
                color=theme.shadow + "40",
                offset=ft.Offset(0, 10),
            ),
        )
        
        # Create overlay
        self._control = ft.Container(
            content=content,
            alignment=ft.alignment.center,
            bgcolor=self.bgcolor or (theme.background + f"{int(self.opacity * 255):02x}"),
            expand=True,
            visible=self.config.visible,
        )
        
        return self._control
    
    def update_message(self, message: str) -> None:
        """Update the loading message."""
        if self._control and self._control.content:
            text_control = self._control.content.content.controls[1]
            text_control.value = message
            text_control.update()
    
    def update_progress(self, value: float) -> None:
        """Update the progress value."""
        if self.show_progress and self._control and self._control.content:
            progress_control = self._control.content.content.controls[0]
            if isinstance(progress_control, ft.ProgressBar):
                progress_control.value = value
                progress_control.update()


class SkeletonLoader(ThemedControl):
    """Skeleton loader for content placeholders."""
    
    def __init__(self,
                 width: Optional[Union[int, float]] = None,
                 height: Optional[Union[int, float]] = None,
                 border_radius: Optional[Union[int, ft.border_radius.BorderRadius]] = None,
                 animate: bool = True,
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.width = width
        self.height = height or 20
        self.border_radius = border_radius
        self.animate = animate
    
    def build(self) -> ft.Container:
        """Build the skeleton loader."""
        theme = self.theme or DefaultTheme()
        controls_config = get_controls_config()
        
        # Set defaults
        if self.border_radius is None:
            self.border_radius = controls_config.default_border_radius // 2
        
        # Create animated gradient if enabled
        if self.animate:
            gradient = ft.LinearGradient(
                begin=ft.alignment.center_left,
                end=ft.alignment.center_right,
                colors=[
                    theme.surface_variant,
                    theme.surface,
                    theme.surface_variant,
                ],
                tile_mode=ft.GradientTileMode.CLAMP,
            )
            
            self._control = ft.Container(
                width=self.width,
                height=self.height,
                border_radius=self.border_radius,
                gradient=gradient,
                animate=ft.Animation(
                    duration=controls_config.skeleton_animation_duration,
                    curve=ft.AnimationCurve.EASE_IN_OUT,
                ),
                visible=self.config.visible,
            )
        else:
            self._control = ft.Container(
                width=self.width,
                height=self.height,
                bgcolor=theme.surface_variant,
                border_radius=self.border_radius,
                visible=self.config.visible,
            )
        
        return self._control


class ProgressTracker(ThemedControl):
    """Progress tracker for multi-step operations."""
    
    def __init__(self,
                 steps: List[str],
                 current_step: int = 0,
                 show_step_numbers: bool = True,
                 orientation: str = "horizontal",
                 config: Optional[ControlConfig] = None):
        super().__init__(config)
        self.steps = steps
        self.current_step = current_step
        self.show_step_numbers = show_step_numbers
        self.orientation = orientation
        self._step_indicators: List[ft.Container] = []
    
    def build(self) -> ft.Control:
        """Build the progress tracker."""
        theme = self.theme or DefaultTheme()
        controls_config = get_controls_config()
        
        step_controls = []
        
        for i, step in enumerate(self.steps):
            # Determine step state
            is_completed = i < self.current_step
            is_current = i == self.current_step
            is_pending = i > self.current_step
            
            # Step indicator
            if is_completed:
                indicator_content = ft.Icon(
                    ft.Icons.CHECK,
                    size=16,
                    color=theme.on_primary,
                )
                indicator_bgcolor = theme.primary
            elif is_current:
                if self.show_step_numbers:
                    indicator_content = ft.Text(
                        str(i + 1),
                        size=14,
                        color=theme.on_primary,
                        weight=ft.FontWeight.BOLD,
                    )
                else:
                    indicator_content = ft.Container(
                        width=8,
                        height=8,
                        bgcolor=theme.on_primary,
                        border_radius=4,
                    )
                indicator_bgcolor = theme.primary
            else:  # pending
                if self.show_step_numbers:
                    indicator_content = ft.Text(
                        str(i + 1),
                        size=14,
                        color=theme.on_surface_variant,
                    )
                else:
                    indicator_content = None
                indicator_bgcolor = theme.surface_variant
            
            indicator = ft.Container(
                content=indicator_content,
                width=32,
                height=32,
                bgcolor=indicator_bgcolor,
                border_radius=16,
                alignment=ft.alignment.center,
            )
            self._step_indicators.append(indicator)
            
            # Step label
            label = ft.Text(
                step,
                size=12,
                color=theme.on_surface if not is_pending else theme.on_surface_variant,
                weight=ft.FontWeight.W_500 if is_current else None,
                text_align=ft.TextAlign.CENTER if self.orientation == "horizontal" else ft.TextAlign.LEFT,
            )
            
            # Step container
            if self.orientation == "horizontal":
                step_control = ft.Column(
                    controls=[indicator, label],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                )
            else:
                step_control = ft.Row(
                    controls=[indicator, label],
                    spacing=controls_config.default_spacing,
                )
            
            step_controls.append(step_control)
            
            # Add connector line (except for last step)
            if i < len(self.steps) - 1:
                if self.orientation == "horizontal":
                    connector = ft.Container(
                        height=2,
                        width=40,
                        bgcolor=theme.primary if is_completed else theme.surface_variant,
                        margin=ft.margin.only(top=15),
                    )
                else:
                    connector = ft.Container(
                        width=2,
                        height=40,
                        bgcolor=theme.primary if is_completed else theme.surface_variant,
                        margin=ft.margin.only(left=15),
                    )
                step_controls.append(connector)
        
        # Create main container
        if self.orientation == "horizontal":
            self._control = ft.Row(
                controls=step_controls,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=0,
                visible=self.config.visible,
            )
        else:
            self._control = ft.Column(
                controls=step_controls,
                spacing=0,
                visible=self.config.visible,
            )
        
        return self._control
    
    def update_step(self, step: int) -> None:
        """Update the current step."""
        if 0 <= step < len(self.steps) and step != self.current_step:
            self.current_step = step
            
            # Rebuild the control
            if self._control:
                parent = self._control.parent
                new_control = self.build()
                
                if parent and hasattr(parent, 'controls'):
                    index = parent.controls.index(self._control)
                    parent.controls[index] = new_control
                    parent.update()
                elif parent:
                    parent.content = new_control
                    parent.update()