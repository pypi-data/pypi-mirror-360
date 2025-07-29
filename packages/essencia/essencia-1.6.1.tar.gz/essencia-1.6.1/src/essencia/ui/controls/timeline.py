"""
Timeline components for essencia.

This module provides timeline visualization components for displaying
chronological data in various orientations.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, List, Optional, Union
from datetime import datetime, date
import flet as ft

from .base import ThemedControl, ControlConfig, get_controls_config, DefaultTheme
from .layout import Panel


class TimelineOrientation(Enum):
    """Orientation options for timeline display."""
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"


@dataclass
class TimelineItem:
    """Configuration for a timeline item."""
    timestamp: Union[datetime, date, str]
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None
    icon_color: Optional[str] = None
    content: Optional[ft.Control] = None
    on_click: Optional[Callable[[], None]] = None
    data: Optional[Any] = None
    
    def format_time(self, format_str: str = "%d/%m/%Y") -> str:
        """Format the timestamp as string."""
        if isinstance(self.timestamp, (datetime, date)):
            return self.timestamp.strftime(format_str)
        return str(self.timestamp)


@dataclass
class TimelineConfig:
    """Configuration for timeline behavior and appearance."""
    orientation: TimelineOrientation = TimelineOrientation.VERTICAL
    show_connectors: bool = True
    show_timestamps: bool = True
    timestamp_format: str = "%d/%m/%Y %H:%M"
    date_only_format: str = "%d/%m/%Y"
    connector_width: int = 2
    node_size: int = 40
    spacing: int = 20
    animate_on_scroll: bool = False
    expandable_items: bool = False
    group_by_date: bool = False


class BaseTimeline(ThemedControl):
    """Base class for timeline components."""
    
    def __init__(self,
                 items: List[TimelineItem],
                 config: Optional[TimelineConfig] = None,
                 control_config: Optional[ControlConfig] = None):
        super().__init__(control_config)
        self.items = items
        self.config = config or TimelineConfig()
        self._item_controls: List[ft.Control] = []
    
    def _build_timeline_node(self, item: TimelineItem, is_last: bool = False) -> ft.Control:
        """Build a timeline node (icon/indicator)."""
        theme = self.theme or DefaultTheme()
        
        # Node content
        if item.icon:
            node_content = ft.Icon(
                item.icon,
                size=20,
                color=theme.on_primary if item.icon_color else theme.on_surface,
            )
        else:
            node_content = ft.Container(
                width=10,
                height=10,
                bgcolor=theme.on_primary if item.icon_color else theme.on_surface,
                border_radius=5,
            )
        
        # Node container
        node = ft.Container(
            content=node_content,
            width=self.config.node_size,
            height=self.config.node_size,
            bgcolor=item.icon_color or theme.primary,
            border_radius=self.config.node_size // 2,
            alignment=ft.alignment.center,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color=theme.shadow + "40",
                offset=ft.Offset(0, 2),
            ),
        )
        
        return node
    
    def _build_timeline_connector(self, height: Optional[int] = None, width: Optional[int] = None) -> ft.Control:
        """Build a connector line between timeline nodes."""
        theme = self.theme or DefaultTheme()
        
        return ft.Container(
            width=width or self.config.connector_width,
            height=height,
            bgcolor=theme.outline,
            margin=ft.margin.symmetric(
                horizontal=(self.config.node_size - self.config.connector_width) // 2
                if self.config.orientation == TimelineOrientation.VERTICAL else 0,
                vertical=(self.config.node_size - self.config.connector_width) // 2
                if self.config.orientation == TimelineOrientation.HORIZONTAL else 0,
            ),
        )
    
    def _build_timeline_content(self, item: TimelineItem) -> ft.Control:
        """Build the content section of a timeline item."""
        theme = self.theme or DefaultTheme()
        controls_config = get_controls_config()
        
        content_controls = []
        
        # Timestamp
        if self.config.show_timestamps:
            format_str = self.config.date_only_format if isinstance(item.timestamp, date) else self.config.timestamp_format
            content_controls.append(
                ft.Text(
                    item.format_time(format_str),
                    size=12,
                    color=theme.on_surface_variant,
                )
            )
        
        # Title
        content_controls.append(
            ft.Text(
                item.title,
                size=16,
                weight=ft.FontWeight.W_500,
                color=theme.on_surface,
            )
        )
        
        # Description
        if item.description:
            content_controls.append(
                ft.Text(
                    item.description,
                    size=14,
                    color=theme.on_surface_variant,
                )
            )
        
        # Custom content
        if item.content:
            content_controls.append(item.content)
        
        # Build content container
        content = ft.Column(
            controls=content_controls,
            spacing=controls_config.default_spacing // 2,
        )
        
        # Wrap in panel if expandable
        if self.config.expandable_items and (item.description or item.content):
            content = Panel(
                content=content,
                padding=controls_config.default_padding,
            ).build()
        
        # Add click handler
        if item.on_click:
            content = ft.Container(
                content=content,
                on_click=lambda e: item.on_click(),
                ink=True,
                padding=controls_config.default_padding if not self.config.expandable_items else 0,
            )
        
        return content
    
    def build(self) -> ft.Control:
        """Build the timeline (to be overridden by subclasses)."""
        raise NotImplementedError


class VerticalTimeline(BaseTimeline):
    """Vertical timeline component."""
    
    def build(self) -> ft.Control:
        """Build the vertical timeline."""
        timeline_controls = []
        
        # Group items by date if configured
        if self.config.group_by_date:
            grouped_items = self._group_items_by_date()
            
            for date_str, items in grouped_items.items():
                # Add date header
                timeline_controls.append(self._build_date_header(date_str))
                
                # Add items for this date
                for i, item in enumerate(items):
                    is_last = (i == len(items) - 1 and date_str == list(grouped_items.keys())[-1])
                    timeline_controls.append(self._build_vertical_item(item, is_last))
        else:
            # Add all items without grouping
            for i, item in enumerate(self.items):
                is_last = i == len(self.items) - 1
                timeline_controls.append(self._build_vertical_item(item, is_last))
        
        self._control = ft.Column(
            controls=timeline_controls,
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
            visible=self.config.visible,
            disabled=self.config.disabled,
        )
        
        return self._control
    
    def _build_vertical_item(self, item: TimelineItem, is_last: bool) -> ft.Control:
        """Build a single vertical timeline item."""
        controls = []
        
        # Timeline node and content
        node = self._build_timeline_node(item, is_last)
        content = self._build_timeline_content(item)
        
        # Item row
        item_row = ft.Row(
            controls=[
                node,
                ft.Container(
                    content=content,
                    expand=True,
                    margin=ft.margin.only(left=self.config.spacing),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        controls.append(item_row)
        
        # Connector (unless last item)
        if self.config.show_connectors and not is_last:
            connector = self._build_timeline_connector(height=50)
            controls.append(connector)
        
        return ft.Column(
            controls=controls,
            spacing=0,
        )
    
    def _group_items_by_date(self) -> dict:
        """Group timeline items by date."""
        grouped = {}
        
        for item in self.items:
            if isinstance(item.timestamp, datetime):
                date_key = item.timestamp.date()
            elif isinstance(item.timestamp, date):
                date_key = item.timestamp
            else:
                date_key = str(item.timestamp)
            
            date_str = date_key.strftime(self.config.date_only_format) if hasattr(date_key, 'strftime') else str(date_key)
            
            if date_str not in grouped:
                grouped[date_str] = []
            grouped[date_str].append(item)
        
        return grouped
    
    def _build_date_header(self, date_str: str) -> ft.Control:
        """Build a date header for grouped items."""
        theme = self.theme or DefaultTheme()
        
        return ft.Container(
            content=ft.Text(
                date_str,
                size=14,
                weight=ft.FontWeight.BOLD,
                color=theme.primary,
            ),
            padding=ft.padding.symmetric(vertical=10),
        )


class HorizontalTimeline(BaseTimeline):
    """Horizontal timeline component."""
    
    def build(self) -> ft.Control:
        """Build the horizontal timeline."""
        timeline_controls = []
        
        for i, item in enumerate(self.items):
            is_last = i == len(self.items) - 1
            
            # Build item column
            item_controls = []
            
            # Content above timeline
            content = self._build_timeline_content(item)
            item_controls.append(
                ft.Container(
                    content=content,
                    width=150,  # Fixed width for horizontal items
                    height=100,  # Fixed height
                    alignment=ft.alignment.top_center,
                )
            )
            
            # Timeline node
            node = self._build_timeline_node(item, is_last)
            item_controls.append(node)
            
            item_column = ft.Column(
                controls=item_controls,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=self.config.spacing,
            )
            
            timeline_controls.append(item_column)
            
            # Connector (unless last item)
            if self.config.show_connectors and not is_last:
                connector = self._build_timeline_connector(width=50)
                timeline_controls.append(
                    ft.Container(
                        content=connector,
                        alignment=ft.alignment.center,
                        height=self.config.node_size,
                    )
                )
        
        self._control = ft.Row(
            controls=timeline_controls,
            spacing=0,
            scroll=ft.ScrollMode.HORIZONTAL,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            visible=self.config.visible,
            disabled=self.config.disabled,
        )
        
        return self._control