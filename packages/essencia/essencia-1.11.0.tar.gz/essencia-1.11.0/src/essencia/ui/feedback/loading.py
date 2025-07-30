"""
Loading and skeleton components for better UX.

Provides various loading indicators, skeleton loaders, and
progress tracking components for Flet applications.
"""

import asyncio
import logging
from typing import Optional, Callable, Any, Union, List
from enum import Enum

import flet as ft

from ..themes import ThemedComponent, get_theme_from_page

logger = logging.getLogger(__name__)


class LoadingStyle(Enum):
    """Loading indicator styles."""
    CIRCULAR = "circular"
    LINEAR = "linear"
    DOTS = "dots"
    SKELETON = "skeleton"


class LoadingSize(Enum):
    """Loading indicator sizes."""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class LoadingIndicator(ft.Container, ThemedComponent):
    """
    Customizable loading indicator with different styles.
    
    Example:
        ```python
        # Circular loading indicator
        loader = LoadingIndicator(
            style=LoadingStyle.CIRCULAR,
            size=LoadingSize.MEDIUM
        )
        
        # Linear progress bar
        progress = LoadingIndicator(
            style=LoadingStyle.LINEAR,
            size=LoadingSize.LARGE
        )
        
        # Animated dots
        dots = LoadingIndicator(
            style=LoadingStyle.DOTS,
            size=LoadingSize.SMALL
        )
        ```
    """
    
    def __init__(
        self,
        style: Union[LoadingStyle, str] = LoadingStyle.CIRCULAR,
        size: Union[LoadingSize, str] = LoadingSize.MEDIUM,
        color: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs
    ):
        ThemedComponent.__init__(self)
        
        # Convert string to enum if needed
        if isinstance(style, str):
            style = LoadingStyle(style)
        if isinstance(size, str):
            size = LoadingSize(size)
            
        self.style = style
        self.size = size
        self._color = color
        self.message = message
        
        # Size configurations
        self.sizes = {
            LoadingSize.SMALL: {"ring": 20, "bar": 100, "dot": 8, "stroke": 3},
            LoadingSize.MEDIUM: {"ring": 40, "bar": 200, "dot": 12, "stroke": 4},
            LoadingSize.LARGE: {"ring": 60, "bar": 300, "dot": 16, "stroke": 5}
        }
        
        # Initialize with placeholder content
        super().__init__(
            content=self._build_content(),
            **kwargs
        )
    
    def did_mount(self):
        """Start animations when mounted."""
        super().did_mount()
        
        # Apply theme colors
        if not self._color:
            self.color = self.primary_color
        else:
            self.color = self._color
            
        # Rebuild content with theme colors
        self.content = self._build_content()
        self.update()
        
        # Start animations
        if self.style == LoadingStyle.DOTS:
            self.page.run_task(self._animate_dots)
    
    def _build_content(self) -> ft.Control:
        """Build the loading indicator based on style."""
        size_config = self.sizes[self.size]
        color = getattr(self, 'color', self._color) or ft.Colors.PRIMARY
        
        content_controls = []
        
        if self.style == LoadingStyle.CIRCULAR:
            content_controls.append(
                ft.ProgressRing(
                    width=size_config["ring"],
                    height=size_config["ring"],
                    color=color,
                    stroke_width=size_config["stroke"]
                )
            )
        
        elif self.style == LoadingStyle.LINEAR:
            content_controls.append(
                ft.ProgressBar(
                    width=size_config["bar"],
                    color=color,
                    bgcolor=ft.Colors.with_opacity(0.2, color)
                )
            )
        
        elif self.style == LoadingStyle.DOTS:
            dots = ft.Row(
                controls=[
                    ft.Container(
                        width=size_config["dot"],
                        height=size_config["dot"],
                        bgcolor=color,
                        border_radius=size_config["dot"] // 2,
                        animate=ft.Animation(
                            duration=600,
                            curve=ft.AnimationCurve.EASE_IN_OUT
                        ),
                        animate_scale=ft.Animation(
                            duration=600,
                            curve=ft.AnimationCurve.EASE_IN_OUT
                        )
                    )
                    for _ in range(3)
                ],
                spacing=5
            )
            content_controls.append(dots)
        
        # Add message if provided
        if self.message:
            content_controls.append(
                ft.Text(
                    self.message,
                    size=14 if self.size == LoadingSize.SMALL else 16,
                    weight=ft.FontWeight.W_500
                )
            )
        
        # Return single control or column
        if len(content_controls) == 1:
            return content_controls[0]
        else:
            return ft.Column(
                controls=content_controls,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            )
    
    async def _animate_dots(self):
        """Animate loading dots."""
        if self.style != LoadingStyle.DOTS:
            return
            
        # Get dots from nested structure
        dots_container = self.content
        if isinstance(dots_container, ft.Column):
            dots_container = dots_container.controls[0]
            
        if not hasattr(dots_container, 'controls'):
            return
            
        dots = dots_container.controls
        
        while self.page and dots:
            try:
                for i, dot in enumerate(dots):
                    if dot and self.page:
                        dot.scale = 1.3
                        dot.update()
                        await asyncio.sleep(0.2)
                        if dot and self.page:
                            dot.scale = 1.0
                            dot.update()
            except Exception as e:
                logger.warning(f"Error in dots animation: {e}")
                break


class SkeletonLoader(ft.Column):
    """
    Skeleton loading animation for content placeholders.
    Shows animated bars while content is loading.
    
    Example:
        ```python
        # Show skeleton while loading
        skeleton = SkeletonLoader(
            rows=3,
            row_height=20,
            spacing=10
        )
        
        # Replace with actual content when loaded
        container.content = loaded_content
        ```
    """
    
    def __init__(
        self,
        rows: int = 3,
        row_height: int = 20,
        spacing: int = 10,
        animate: bool = True,
        **kwargs
    ):
        super().__init__(spacing=spacing, **kwargs)
        
        self.animate = animate
        self._animation_task = None
        
        # Create skeleton rows with varying widths
        for i in range(rows):
            # Vary widths for more realistic look
            width_percent = 100 - (i * 10) if i < 3 else 60
            
            self.controls.append(
                ft.Container(
                    height=row_height,
                    width=f"{width_percent}%",
                    bgcolor=ft.Colors.SURFACE_VARIANT,
                    border_radius=4,
                    animate=ft.Animation(
                        duration=1500,
                        curve=ft.AnimationCurve.EASE_IN_OUT
                    ) if animate else None,
                    animate_opacity=ft.Animation(
                        duration=1500,
                        curve=ft.AnimationCurve.EASE_IN_OUT
                    ) if animate else None
                )
            )
    
    def did_mount(self):
        """Start animation when mounted."""
        super().did_mount()
        
        if self.animate and self.page:
            self._animation_task = self.page.run_task(self._animate)
    
    def will_unmount(self):
        """Stop animation when unmounting."""
        if self._animation_task:
            self._animation_task.cancel()
        super().will_unmount()
    
    async def _animate(self):
        """Pulse animation effect."""
        while self.page:
            try:
                # Fade out
                for control in self.controls:
                    if control and self.page:
                        control.opacity = 0.5
                self._safe_update()
                await asyncio.sleep(0.75)
                
                # Fade in
                for control in self.controls:
                    if control and self.page:
                        control.opacity = 1.0
                self._safe_update()
                await asyncio.sleep(0.75)
                
            except Exception as e:
                logger.warning(f"Error in skeleton animation: {e}")
                break
    
    def _safe_update(self):
        """Safe update method that handles edge cases."""
        try:
            if self.page and hasattr(self, 'parent') and self.parent is not None:
                self.update()
        except Exception as e:
            logger.debug(f"Update skipped: {e}")


class LoadingOverlay(ft.Stack):
    """
    Full-screen loading overlay for blocking operations.
    
    Example:
        ```python
        overlay = LoadingOverlay(
            message="Loading data...",
            opacity=0.8
        )
        
        # Show overlay
        overlay.show()
        
        # Hide overlay
        overlay.hide()
        ```
    """
    
    def __init__(
        self,
        message: str = "Loading...",
        opacity: float = 0.8,
        style: Union[LoadingStyle, str] = LoadingStyle.CIRCULAR,
        size: Union[LoadingSize, str] = LoadingSize.LARGE,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.message = message
        self.opacity = opacity
        self.style = style
        self.size = size
        
        # Create overlay container
        self.overlay = ft.Container(
            content=LoadingIndicator(
                style=style,
                size=size,
                message=message
            ),
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(opacity, ft.Colors.BLACK),
            visible=False,
            expand=True
        )
        
        self.controls = [self.overlay]
    
    def show(self, message: Optional[str] = None):
        """Show the loading overlay."""
        if message:
            self.message = message
            # Update loading indicator message
            if hasattr(self.overlay.content, 'message'):
                self.overlay.content.message = message
                
        self.overlay.visible = True
        self.update()
    
    def hide(self):
        """Hide the loading overlay."""
        self.overlay.visible = False
        self.update()


class LoadingWrapper(ft.Stack):
    """
    Wraps content with a loading overlay.
    Shows loading spinner over content when loading=True.
    
    Example:
        ```python
        wrapped_content = LoadingWrapper(
            content=my_content,
            loading=False
        )
        
        # Show loading
        wrapped_content.show_loading("Processing...")
        
        # Hide loading
        wrapped_content.hide_loading()
        ```
    """
    
    def __init__(
        self,
        content: ft.Control,
        loading: bool = False,
        opacity: float = 0.8,
        style: Union[LoadingStyle, str] = LoadingStyle.CIRCULAR,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.content_control = content
        self.is_loading = loading
        
        # Create loading overlay
        self.loading_overlay = ft.Container(
            content=LoadingIndicator(
                style=style,
                size=LoadingSize.MEDIUM,
                message="Loading..."
            ),
            alignment=ft.alignment.center,
            bgcolor=ft.Colors.with_opacity(opacity, ft.Colors.BLACK),
            visible=loading,
            expand=True
        )
        
        self.controls = [content, self.loading_overlay]
    
    def show_loading(self, message: str = "Loading..."):
        """Show loading overlay with optional message."""
        try:
            self.loading_overlay.visible = True
            
            # Update message
            if hasattr(self.loading_overlay.content, 'message'):
                self.loading_overlay.content.message = message
                
            self.update()
        except Exception as e:
            logger.warning(f"Error showing loading overlay: {e}")
    
    def hide_loading(self):
        """Hide loading overlay."""
        try:
            self.loading_overlay.visible = False
            self.update()
        except Exception as e:
            logger.warning(f"Error hiding loading overlay: {e}")
    
    def set_content(self, content: ft.Control):
        """Update the wrapped content."""
        try:
            self.controls[0] = content
            self.update()
        except Exception as e:
            logger.warning(f"Error setting content: {e}")


class LoadingButton(ft.ElevatedButton):
    """
    Button that shows loading state during async operations.
    Prevents multiple clicks and provides visual feedback.
    
    Example:
        ```python
        async def handle_save(e):
            await save_data()
            
        button = LoadingButton(
            text="Save",
            on_click=handle_save,
            loading_text="Saving...",
            icon=ft.Icons.SAVE
        )
        ```
    """
    
    def __init__(
        self,
        text: str,
        on_click: Optional[Callable] = None,
        loading_text: str = "Processing...",
        icon: Optional[str] = None,
        show_progress: bool = True,
        **kwargs
    ):
        self._original_text = text
        self._loading_text = loading_text
        self._original_icon = icon
        self._on_click_handler = on_click
        self._is_loading = False
        self._show_progress = show_progress
        
        super().__init__(
            text=text,
            icon=icon,
            on_click=self._handle_click,
            **kwargs
        )
    
    async def _handle_click(self, e):
        """Handle button click with loading state."""
        if self._is_loading or not self._on_click_handler:
            return
        
        # Set loading state
        self._is_loading = True
        self.disabled = True
        self.icon = None
        
        if self._show_progress:
            self.content = ft.Row(
                controls=[
                    ft.ProgressRing(width=16, height=16, stroke_width=2),
                    ft.Text(self._loading_text)
                ],
                spacing=10,
                alignment=ft.MainAxisAlignment.CENTER
            )
        else:
            self.text = self._loading_text
            
        self.update()
        
        try:
            # Execute the handler
            if asyncio.iscoroutinefunction(self._on_click_handler):
                await self._on_click_handler(e)
            else:
                self._on_click_handler(e)
        except Exception as e:
            logger.error(f"Error in button handler: {e}")
        finally:
            # Reset to original state
            self._is_loading = False
            self.disabled = False
            self.icon = self._original_icon
            self.content = None
            self.text = self._original_text
            self.update()


class LazyLoadContainer(ft.Column):
    """
    Container that loads content when scrolled into view.
    Useful for long lists or heavy content.
    
    Example:
        ```python
        async def load_heavy_content():
            # Simulate loading
            await asyncio.sleep(1)
            return ft.Text("Loaded content!")
            
        lazy_container = LazyLoadContainer(
            load_function=load_heavy_content,
            placeholder=SkeletonLoader(rows=5)
        )
        ```
    """
    
    def __init__(
        self,
        load_function: Callable[[], Any],
        placeholder: Optional[ft.Control] = None,
        error_widget: Optional[ft.Control] = None,
        threshold: int = 100,
        auto_load: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.load_function = load_function
        self.threshold = threshold
        self.auto_load = auto_load
        self.loaded = False
        self.loading = False
        self.error_widget = error_widget
        
        # Show placeholder initially
        self.controls = [
            placeholder or SkeletonLoader(rows=3)
        ]
    
    def did_mount(self):
        """Auto-load content when mounted if enabled."""
        super().did_mount()
        
        if self.auto_load:
            self.page.run_task(self.load_content)
    
    async def load_content(self):
        """Load the actual content."""
        if self.loaded or self.loading:
            return
            
        self.loading = True
        
        try:
            # Load content
            if asyncio.iscoroutinefunction(self.load_function):
                content = await self.load_function()
            else:
                content = self.load_function()
            
            # Replace placeholder with content
            self.controls = [content] if content else []
            self.loaded = True
            self.update()
            
        except Exception as e:
            logger.error(f"Error loading content: {e}")
            
            # Show error widget or default error
            if self.error_widget:
                self.controls = [self.error_widget]
            else:
                self.controls = [
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.ERROR, color=ft.Colors.ERROR),
                            ft.Text(f"Error loading: {str(e)}", color=ft.Colors.ERROR)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20
                    )
                ]
            self.update()
            
        finally:
            self.loading = False
    
    async def reload(self):
        """Force reload the content."""
        self.loaded = False
        self.loading = False
        await self.load_content()


class ProgressTracker(ft.Column):
    """
    Track progress of multi-step operations.
    
    Example:
        ```python
        tracker = ProgressTracker(
            steps=["Upload", "Process", "Complete"],
            style="steps"  # or "linear"
        )
        
        # Update progress
        tracker.set_step(1)  # Mark first step complete
        tracker.set_progress(0.5)  # Set to 50%
        ```
    """
    
    def __init__(
        self,
        steps: Optional[List[str]] = None,
        style: str = "linear",  # "linear" or "steps"
        show_percentage: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        
        self.steps = steps or []
        self.style = style
        self.show_percentage = show_percentage
        self.current_step = 0
        self.progress = 0.0
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the progress UI."""
        self.controls.clear()
        
        if self.style == "linear":
            # Progress bar with percentage
            progress_row = [
                ft.ProgressBar(
                    value=self.progress,
                    width=300,
                    height=10,
                    bgcolor=ft.Colors.SURFACE_VARIANT
                )
            ]
            
            if self.show_percentage:
                progress_row.append(
                    ft.Text(f"{int(self.progress * 100)}%", size=14)
                )
                
            self.controls.append(
                ft.Row(progress_row, spacing=10)
            )
            
            # Step text
            if self.steps and self.current_step < len(self.steps):
                self.controls.append(
                    ft.Text(
                        self.steps[self.current_step],
                        size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT
                    )
                )
                
        elif self.style == "steps" and self.steps:
            # Step indicators
            step_row = []
            
            for i, step in enumerate(self.steps):
                # Step circle
                is_complete = i < self.current_step
                is_current = i == self.current_step
                
                circle = ft.Container(
                    content=ft.Text(
                        str(i + 1) if not is_complete else "✓",
                        size=12,
                        color=ft.Colors.ON_PRIMARY if is_complete or is_current else ft.Colors.ON_SURFACE
                    ),
                    width=30,
                    height=30,
                    border_radius=15,
                    bgcolor=(
                        ft.Colors.PRIMARY if is_complete or is_current
                        else ft.Colors.SURFACE_VARIANT
                    ),
                    alignment=ft.alignment.center
                )
                
                step_col = ft.Column([
                    circle,
                    ft.Text(
                        step,
                        size=10,
                        text_align=ft.TextAlign.CENTER,
                        width=60
                    )
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                
                step_row.append(step_col)
                
                # Add connector line
                if i < len(self.steps) - 1:
                    step_row.append(
                        ft.Container(
                            width=30,
                            height=2,
                            bgcolor=(
                                ft.Colors.PRIMARY if i < self.current_step
                                else ft.Colors.SURFACE_VARIANT
                            ),
                            margin=ft.margin.only(top=15)
                        )
                    )
            
            self.controls.append(
                ft.Row(step_row, alignment=ft.MainAxisAlignment.CENTER)
            )
    
    def set_progress(self, value: float):
        """Set overall progress (0.0 to 1.0)."""
        self.progress = max(0.0, min(1.0, value))
        self._build_ui()
        self.update()
    
    def set_step(self, step: int):
        """Set current step (0-based index)."""
        self.current_step = max(0, min(step, len(self.steps)))
        
        # Update progress based on steps
        if self.steps:
            self.progress = self.current_step / len(self.steps)
            
        self._build_ui()
        self.update()
    
    def complete(self):
        """Mark as complete."""
        self.current_step = len(self.steps)
        self.progress = 1.0
        self._build_ui()
        self.update()