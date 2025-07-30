"""
Theme system for Flet applications.

Provides a comprehensive theming system with theme-aware components,
theme providers, and utilities for consistent styling.
"""

from .theme_aware import (
    ThemedComponent,
    ThemedContainer,
    ThemedCard, 
    ThemedText,
    ThemedDivider,
    apply_theme_to_control,
    get_theme_from_page,
)
from .theme_provider import (
    ThemeProvider,
    DefaultTheme,
    create_theme,
    apply_theme_to_page,
)

__all__ = [
    # Theme-aware components
    "ThemedComponent",
    "ThemedContainer",
    "ThemedCard",
    "ThemedText", 
    "ThemedDivider",
    "apply_theme_to_control",
    "get_theme_from_page",
    
    # Theme provider
    "ThemeProvider",
    "DefaultTheme",
    "create_theme",
    "apply_theme_to_page",
]