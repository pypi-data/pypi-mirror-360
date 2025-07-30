"""
Text field input components with theme integration.
"""

from typing import Optional, Callable, Any, Union
import flet as ft
from .theme_helper import apply_input_theme


class ThemedTextField(ft.TextField):
    """TextField with automatic theme-aware styling.
    
    A text input field that automatically adapts its appearance to match
    the application's theme, providing consistent styling across light
    and dark modes.
    
    Example:
        ```python
        name_field = ThemedTextField(
            label="Full Name",
            hint_text="Enter your full name",
            prefix_icon=ft.Icons.PERSON,
            on_change=validate_name
        )
        ```
    """
    
    def __init__(self, **kwargs):
        # Extract theme-related kwargs that we'll handle
        self._theme_overrides = {}
        theme_props = [
            'filled', 'fill_color', 'color', 'label_style', 'hint_style',
            'border_color', 'focused_border_color', 'border_width',
            'focused_border_width', 'cursor_color', 'selection_color'
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


class PasswordField(ThemedTextField):
    """Specialized text field for password input.
    
    Features password visibility toggle and strength indicator support.
    
    Example:
        ```python
        password = PasswordField(
            label="Password",
            on_change=check_password_strength,
            show_strength_indicator=True
        )
        ```
    """
    
    def __init__(
        self,
        label: str = "Password",
        show_toggle: bool = True,
        show_strength_indicator: bool = False,
        on_strength_change: Optional[Callable[[str, float], None]] = None,
        **kwargs
    ):
        self._show_strength = show_strength_indicator
        self._on_strength_change = on_strength_change
        
        kwargs['label'] = label
        kwargs['password'] = True
        kwargs['can_reveal_password'] = show_toggle
        
        # Add password icon by default
        if 'prefix_icon' not in kwargs:
            kwargs['prefix_icon'] = ft.Icons.LOCK
            
        # Store original on_change
        self._user_on_change = kwargs.get('on_change')
        if show_strength_indicator:
            kwargs['on_change'] = self._handle_change
            
        super().__init__(**kwargs)
        
    def _handle_change(self, e):
        """Handle password change with strength calculation."""
        if self._user_on_change:
            self._user_on_change(e)
            
        if self._show_strength and self._on_strength_change:
            strength = self._calculate_strength(e.control.value)
            self._on_strength_change(e.control.value, strength)
    
    def _calculate_strength(self, password: str) -> float:
        """Calculate password strength (0.0 to 1.0)."""
        if not password:
            return 0.0
            
        score = 0.0
        
        # Length score
        score += min(len(password) / 12, 0.25)
        
        # Character variety
        if any(c.islower() for c in password):
            score += 0.25
        if any(c.isupper() for c in password):
            score += 0.25
        if any(c.isdigit() for c in password):
            score += 0.125
        if any(not c.isalnum() for c in password):
            score += 0.125
            
        return min(score, 1.0)


class SearchField(ThemedTextField):
    """Specialized text field for search input.
    
    Features search icon, clear button, and search-as-you-type support.
    
    Example:
        ```python
        search = SearchField(
            hint_text="Search products...",
            on_search=perform_search,
            debounce_ms=300
        )
        ```
    """
    
    def __init__(
        self,
        hint_text: str = "Search...",
        on_search: Optional[Callable[[str], None]] = None,
        debounce_ms: int = 0,
        show_clear: bool = True,
        **kwargs
    ):
        self._on_search = on_search
        self._debounce_ms = debounce_ms
        self._debounce_timer = None
        
        kwargs['hint_text'] = hint_text
        kwargs['prefix_icon'] = ft.Icons.SEARCH
        
        # Add clear button if requested
        if show_clear:
            kwargs['suffix'] = ft.IconButton(
                icon=ft.Icons.CLEAR,
                on_click=self._clear_search,
                visible=False
            )
            self._clear_button = True
        else:
            self._clear_button = False
            
        # Set up change handler
        kwargs['on_change'] = self._handle_search_change
        
        # Enter key triggers immediate search
        kwargs['on_submit'] = self._handle_submit
        
        super().__init__(**kwargs)
        
    def _handle_search_change(self, e):
        """Handle search input change with debouncing."""
        # Update clear button visibility
        if self._clear_button and hasattr(self, 'suffix'):
            self.suffix.visible = bool(e.control.value)
            self.suffix.update()
            
        # Cancel previous timer
        if self._debounce_timer:
            self.page.cancel_task(self._debounce_timer)
            
        # Debounce search
        if self._debounce_ms > 0 and self._on_search:
            import asyncio
            
            async def delayed_search():
                await asyncio.sleep(self._debounce_ms / 1000)
                if self._on_search:
                    self._on_search(e.control.value)
                    
            if hasattr(self, 'page') and self.page:
                self._debounce_timer = self.page.run_task(delayed_search())
        elif self._on_search:
            self._on_search(e.control.value)
            
    def _handle_submit(self, e):
        """Handle enter key press."""
        if self._debounce_timer:
            self.page.cancel_task(self._debounce_timer)
            
        if self._on_search:
            self._on_search(e.control.value)
            
    def _clear_search(self, e):
        """Clear search field."""
        self.value = ""
        if self._clear_button and hasattr(self, 'suffix'):
            self.suffix.visible = False
            
        self.update()
        
        if self._on_search:
            self._on_search("")


class MultilineTextField(ThemedTextField):
    """Multi-line text field for longer text input.
    
    Features line counting, character limit, and auto-resize support.
    
    Example:
        ```python
        notes = MultilineTextField(
            label="Notes",
            min_lines=3,
            max_lines=10,
            max_length=500,
            show_counter=True
        )
        ```
    """
    
    def __init__(
        self,
        min_lines: int = 3,
        max_lines: Optional[int] = None,
        max_length: Optional[int] = None,
        show_counter: bool = False,
        auto_resize: bool = False,
        **kwargs
    ):
        self._show_counter = show_counter
        self._auto_resize = auto_resize
        
        kwargs['multiline'] = True
        kwargs['min_lines'] = min_lines
        
        if max_lines:
            kwargs['max_lines'] = max_lines
            
        if max_length:
            kwargs['max_length'] = max_length
            self._max_length = max_length
        else:
            self._max_length = None
            
        # Set up change handler for counter
        if show_counter:
            self._user_on_change = kwargs.get('on_change')
            kwargs['on_change'] = self._handle_text_change
            
        super().__init__(**kwargs)
        
    def _handle_text_change(self, e):
        """Handle text change for counter update."""
        if self._user_on_change:
            self._user_on_change(e)
            
        if self._show_counter and self._max_length:
            current_length = len(e.control.value or "")
            self.helper_text = f"{current_length}/{self._max_length}"
            self.update()
            
        if self._auto_resize:
            # Simple auto-resize based on content
            lines = (e.control.value or "").count('\n') + 1
            if hasattr(self, 'min_lines') and hasattr(self, 'max_lines'):
                new_lines = max(self.min_lines, min(lines, self.max_lines or lines))
                if hasattr(self, 'height'):
                    # Approximate height calculation
                    self.height = new_lines * 24  # Rough estimate
                    self.update()