"""
Base classes and protocols for essencia UI controls.

This module provides the foundation for all UI controls including:
- Protocol definitions for providers (theme, data, security)
- Base configuration system
- Common base classes for themed controls
"""

from typing import Protocol, Optional, Any, Dict, List, runtime_checkable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
import flet as ft


@runtime_checkable
class ThemeProvider(Protocol):
    """Protocol for theme providers."""
    
    @property
    def primary(self) -> str:
        """Primary color."""
        ...
    
    @property
    def primary_container(self) -> str:
        """Primary container color."""
        ...
    
    @property
    def secondary(self) -> str:
        """Secondary color."""
        ...
    
    @property
    def secondary_container(self) -> str:
        """Secondary container color."""
        ...
    
    @property
    def tertiary(self) -> str:
        """Tertiary color."""
        ...
    
    @property
    def error(self) -> str:
        """Error color."""
        ...
    
    @property
    def surface(self) -> str:
        """Surface color."""
        ...
    
    @property
    def surface_variant(self) -> str:
        """Surface variant color."""
        ...
    
    @property
    def background(self) -> str:
        """Background color."""
        ...
    
    @property
    def on_primary(self) -> str:
        """On primary color."""
        ...
    
    @property
    def on_secondary(self) -> str:
        """On secondary color."""
        ...
    
    @property
    def on_surface(self) -> str:
        """On surface color."""
        ...
    
    @property
    def on_background(self) -> str:
        """On background color."""
        ...
    
    @property
    def outline(self) -> str:
        """Outline color."""
        ...
    
    @property
    def shadow(self) -> str:
        """Shadow color."""
        ...
    
    @property
    def inverse_surface(self) -> str:
        """Inverse surface color."""
        ...
    
    @property
    def on_surface_variant(self) -> str:
        """On surface variant color."""
        ...


@runtime_checkable
class DataProvider(Protocol):
    """Protocol for data providers."""
    
    async def get_items(self, 
                       model_type: str,
                       filters: Optional[Dict[str, Any]] = None,
                       skip: int = 0,
                       limit: Optional[int] = None,
                       sort: Optional[Dict[str, int]] = None) -> List[Any]:
        """Get items with optional filtering, pagination and sorting."""
        ...
    
    async def get_count(self,
                       model_type: str,
                       filters: Optional[Dict[str, Any]] = None) -> int:
        """Get count of items matching filters."""
        ...
    
    async def get_by_id(self,
                       model_type: str,
                       item_id: str) -> Optional[Any]:
        """Get single item by ID."""
        ...
    
    async def create(self,
                    model_type: str,
                    data: Dict[str, Any]) -> Any:
        """Create new item."""
        ...
    
    async def update(self,
                    model_type: str,
                    item_id: str,
                    data: Dict[str, Any]) -> Any:
        """Update existing item."""
        ...
    
    async def delete(self,
                    model_type: str,
                    item_id: str) -> bool:
        """Delete item."""
        ...


@runtime_checkable
class SecurityProvider(Protocol):
    """Protocol for security providers."""
    
    def validate_csrf_token(self, token: str) -> bool:
        """Validate CSRF token."""
        ...
    
    def generate_csrf_token(self) -> str:
        """Generate new CSRF token."""
        ...
    
    def sanitize_html(self, content: str) -> str:
        """Sanitize HTML content."""
        ...
    
    def sanitize_input(self, value: str, input_type: str = "text") -> str:
        """Sanitize user input based on type."""
        ...
    
    def has_permission(self, permission: str, user: Optional[Any] = None) -> bool:
        """Check if user has permission."""
        ...
    
    def encrypt_field(self, value: str, field_type: str = "default") -> str:
        """Encrypt sensitive field value."""
        ...
    
    def decrypt_field(self, value: str, field_type: str = "default") -> str:
        """Decrypt sensitive field value."""
        ...


@dataclass
class EssenciaControlsConfig:
    """Configuration for essencia controls."""
    
    theme_provider: Optional[ThemeProvider] = None
    data_provider: Optional[DataProvider] = None
    security_provider: Optional[SecurityProvider] = None
    locale: str = "pt_BR"
    timezone: str = "America/Sao_Paulo"
    date_format: str = "%d/%m/%Y"
    time_format: str = "%H:%M"
    currency_symbol: str = "R$"
    debug: bool = False
    
    # UI-specific settings
    default_elevation: int = 2
    default_border_radius: int = 8
    default_padding: int = 16
    default_spacing: int = 8
    animation_duration: int = 300
    
    # Form settings
    show_validation_on_blur: bool = True
    show_validation_on_submit: bool = True
    auto_focus_first_error: bool = True
    
    # Pagination settings
    default_page_size: int = 10
    page_size_options: List[int] = field(default_factory=lambda: [10, 25, 50, 100])
    
    # Loading settings
    loading_delay_ms: int = 200
    skeleton_animation_duration: int = 1500


# Global configuration instance
_config: Optional[EssenciaControlsConfig] = None


def configure_controls(config: EssenciaControlsConfig) -> None:
    """Configure essencia controls globally."""
    global _config
    _config = config


def get_controls_config() -> EssenciaControlsConfig:
    """Get current controls configuration."""
    global _config
    if _config is None:
        _config = EssenciaControlsConfig()
    return _config


@dataclass
class ControlConfig:
    """Base configuration for individual controls."""
    
    visible: bool = True
    disabled: bool = False
    tooltip: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    

class ThemedControl(ABC):
    """Base class for theme-aware controls."""
    
    def __init__(self, config: Optional[ControlConfig] = None):
        self.config = config or ControlConfig()
        self._theme = None
        self._control = None
    
    @property
    def theme(self) -> Optional[ThemeProvider]:
        """Get current theme provider."""
        if self._theme is None:
            config = get_controls_config()
            self._theme = config.theme_provider
        return self._theme
    
    @theme.setter
    def theme(self, value: Optional[ThemeProvider]) -> None:
        """Set theme provider."""
        self._theme = value
        if self._control:
            self._apply_theme()
    
    @abstractmethod
    def build(self) -> ft.Control:
        """Build the Flet control."""
        ...
    
    def _apply_theme(self) -> None:
        """Apply theme to control."""
        if self._control and self.theme:
            # Base implementation - subclasses should override
            pass
    
    def update(self) -> None:
        """Update the control."""
        if self._control:
            self._control.update()


class DefaultTheme:
    """Default theme implementation."""
    
    primary = "#1976D2"
    primary_container = "#BBDEFB"
    secondary = "#388E3C"
    secondary_container = "#C8E6C9"
    tertiary = "#F57C00"
    error = "#D32F2F"
    surface = "#FFFFFF"
    surface_variant = "#F5F5F5"
    background = "#FAFAFA"
    on_primary = "#FFFFFF"
    on_secondary = "#FFFFFF"
    on_surface = "#000000"
    on_background = "#000000"
    outline = "#E0E0E0"
    shadow = "#000000"
    inverse_surface = "#303030"
    on_surface_variant = "#757575"