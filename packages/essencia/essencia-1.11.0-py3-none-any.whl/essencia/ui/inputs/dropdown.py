"""
Dropdown and autocomplete components with theme integration.
"""

from typing import Optional, List, Union, Callable, Any
import flet as ft
from .theme_helper import apply_input_theme


class ThemedDropdown(ft.Dropdown):
    """Dropdown with automatic theme-aware styling.
    
    A dropdown selection control that adapts to the application theme,
    providing consistent styling in both light and dark modes.
    
    Example:
        ```python
        country_dropdown = ThemedDropdown(
            label="Country",
            options=[
                ft.dropdown.Option("us", "United States"),
                ft.dropdown.Option("uk", "United Kingdom"),
                ft.dropdown.Option("ca", "Canada"),
            ],
            value="us",
            on_change=handle_country_change
        )
        ```
    """
    
    def __init__(self, **kwargs):
        # Extract theme-related kwargs
        self._theme_overrides = {}
        theme_props = [
            'filled', 'fill_color', 'color', 'label_style', 'hint_style',
            'border_color', 'focused_border_color', 'text_style',
            'icon_enabled_color'
        ]
        
        for prop in theme_props:
            if prop in kwargs:
                self._theme_overrides[prop] = kwargs.pop(prop)
                
        super().__init__(**kwargs)
        
    def did_mount(self):
        """Apply theme styling after control is mounted."""
        super().did_mount()
        
        # Apply theme with any overrides
        apply_input_theme(
            self,
            self.page if hasattr(self, 'page') else None,
            **self._theme_overrides
        )
        
        if hasattr(self, 'update'):
            self.update()


class ThemedAutocomplete(ft.Container):
    """Autocomplete input with filtering and theme support.
    
    Provides a text field with dropdown suggestions that filter
    as the user types.
    
    Example:
        ```python
        cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
        
        city_autocomplete = ThemedAutocomplete(
            label="City",
            suggestions=cities,
            on_select=handle_city_selection,
            strict=False  # Allow custom values
        )
        ```
    """
    
    def __init__(
        self,
        label: str = "",
        suggestions: List[str] = None,
        value: str = "",
        on_select: Optional[Callable[[str], None]] = None,
        on_change: Optional[Callable[[str], None]] = None,
        strict: bool = True,
        max_suggestions: int = 10,
        min_chars: int = 1,
        case_sensitive: bool = False,
        **kwargs
    ):
        self._suggestions = suggestions or []
        self._on_select = on_select
        self._on_change = on_change
        self._strict = strict
        self._max_suggestions = max_suggestions
        self._min_chars = min_chars
        self._case_sensitive = case_sensitive
        self._current_value = value
        
        # Create text field
        from .text_field import ThemedTextField
        self._text_field = ThemedTextField(
            label=label,
            value=value,
            on_change=self._handle_text_change,
            on_blur=self._handle_blur
        )
        
        # Create suggestions dropdown (initially hidden)
        self._suggestions_list = ft.ListView(
            height=200,
            spacing=0,
            padding=ft.padding.all(0)
        )
        
        self._suggestions_card = ft.Card(
            content=self._suggestions_list,
            visible=False,
            elevation=4,
            margin=ft.margin.only(top=2)
        )
        
        # Layout
        content = ft.Column(
            controls=[
                self._text_field,
                self._suggestions_card
            ],
            spacing=0
        )
        
        super().__init__(content=content, **kwargs)
        
    def _handle_text_change(self, e):
        """Handle text input change."""
        query = e.control.value
        self._current_value = query
        
        if self._on_change:
            self._on_change(query)
            
        # Filter suggestions
        if len(query) >= self._min_chars:
            filtered = self._filter_suggestions(query)
            self._show_suggestions(filtered[:self._max_suggestions])
        else:
            self._hide_suggestions()
            
    def _filter_suggestions(self, query: str) -> List[str]:
        """Filter suggestions based on query."""
        if not self._case_sensitive:
            query = query.lower()
            
        filtered = []
        for suggestion in self._suggestions:
            compare_text = suggestion if self._case_sensitive else suggestion.lower()
            if query in compare_text:
                filtered.append(suggestion)
                
        return filtered
        
    def _show_suggestions(self, suggestions: List[str]):
        """Show filtered suggestions."""
        if not suggestions:
            self._hide_suggestions()
            return
            
        # Clear and populate suggestions
        self._suggestions_list.controls.clear()
        
        for suggestion in suggestions:
            item = ft.ListTile(
                title=ft.Text(suggestion),
                on_click=lambda e, s=suggestion: self._select_suggestion(s),
                dense=True,
                content_padding=ft.padding.symmetric(horizontal=16, vertical=0)
            )
            self._suggestions_list.controls.append(item)
            
        self._suggestions_card.visible = True
        self.update()
        
    def _hide_suggestions(self):
        """Hide suggestions dropdown."""
        self._suggestions_card.visible = False
        self.update()
        
    def _select_suggestion(self, suggestion: str):
        """Handle suggestion selection."""
        self._text_field.value = suggestion
        self._current_value = suggestion
        self._hide_suggestions()
        
        if self._on_select:
            self._on_select(suggestion)
            
    def _handle_blur(self, e):
        """Handle focus loss."""
        # Delay to allow click on suggestion
        import threading
        
        def delayed_hide():
            import time
            time.sleep(0.2)
            if hasattr(self, '_suggestions_card'):
                self._hide_suggestions()
                
        thread = threading.Thread(target=delayed_hide)
        thread.daemon = True
        thread.start()
        
        # Validate strict mode
        if self._strict and self._current_value not in self._suggestions:
            self._text_field.error_text = "Please select a valid option"
            self._text_field.update()
        else:
            self._text_field.error_text = None
            self._text_field.update()
            
    @property
    def value(self) -> str:
        """Get current value."""
        return self._current_value
        
    @value.setter
    def value(self, value: str):
        """Set current value."""
        self._current_value = value
        self._text_field.value = value
        if hasattr(self, 'update'):
            self.update()
            
    def add_suggestion(self, suggestion: str):
        """Add a new suggestion."""
        if suggestion not in self._suggestions:
            self._suggestions.append(suggestion)
            
    def set_suggestions(self, suggestions: List[str]):
        """Replace all suggestions."""
        self._suggestions = suggestions
        
    def clear(self):
        """Clear the current value."""
        self.value = ""
        self._hide_suggestions()