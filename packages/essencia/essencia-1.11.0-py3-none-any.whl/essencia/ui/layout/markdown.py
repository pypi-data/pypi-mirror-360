"""
Styled Markdown renderer with customizable theme integration.
"""

from typing import Optional, Dict, Any
import flet as ft


class StyledMarkdown(ft.Markdown):
    """Custom Markdown renderer with application-specific styling.
    
    Provides a markdown component with pre-configured styles suitable for
    professional applications, with full customization support.
    
    Example:
        ```python
        # Basic usage with default styling
        markdown = StyledMarkdown("# Hello World\\n\\nThis is **bold** text.")
        
        # Custom styling
        markdown = StyledMarkdown(
            value="## Custom Styled",
            heading_style={"color": ft.Colors.BLUE, "weight": ft.FontWeight.BOLD},
            code_theme="monokai",
            selectable=True
        )
        ```
    
    Args:
        value (str): Markdown content to render
        selectable (bool): Whether text is selectable (default: True)
        extension_set (ft.MarkdownExtensionSet): Markdown extensions to use
        heading_style (Dict[str, Any]): Style overrides for headings
        text_style (Dict[str, Any]): Style overrides for body text
        code_style (Dict[str, Any]): Style overrides for code blocks
        code_theme (str): Code syntax highlighting theme
        **kwargs: Additional arguments passed to Markdown
    """
    
    # Default style presets
    STYLE_PRESETS = {
        "default": {
            "h1": {"size": 30, "weight": ft.FontWeight.BOLD},
            "h2": {"size": 24, "weight": ft.FontWeight.W_600},
            "h3": {"size": 20, "weight": ft.FontWeight.W_500},
            "h4": {"size": 18, "weight": ft.FontWeight.W_500},
            "h5": {"size": 16, "weight": ft.FontWeight.W_500},
            "h6": {"size": 14, "weight": ft.FontWeight.W_500},
            "p": {"size": 14},
            "code": {"size": 13, "font_family": "monospace"},
            "blockquote": {"size": 14, "italic": True}
        },
        "article": {
            "h1": {"size": 36, "weight": ft.FontWeight.BOLD},
            "h2": {"size": 28, "weight": ft.FontWeight.W_600}, 
            "h3": {"size": 22, "weight": ft.FontWeight.W_500},
            "h4": {"size": 18, "weight": ft.FontWeight.W_500},
            "h5": {"size": 16, "weight": ft.FontWeight.W_500},
            "h6": {"size": 14, "weight": ft.FontWeight.W_500},
            "p": {"size": 16},
            "code": {"size": 14, "font_family": "monospace"},
            "blockquote": {"size": 16, "italic": True}
        },
        "compact": {
            "h1": {"size": 24, "weight": ft.FontWeight.BOLD},
            "h2": {"size": 20, "weight": ft.FontWeight.W_600},
            "h3": {"size": 18, "weight": ft.FontWeight.W_500},
            "h4": {"size": 16, "weight": ft.FontWeight.W_500},
            "h5": {"size": 14, "weight": ft.FontWeight.W_500},
            "h6": {"size": 12, "weight": ft.FontWeight.W_500},
            "p": {"size": 13},
            "code": {"size": 12, "font_family": "monospace"},
            "blockquote": {"size": 13, "italic": True}
        }
    }
    
    def __init__(
        self,
        value: str = "",
        selectable: bool = True,
        extension_set: ft.MarkdownExtensionSet = ft.MarkdownExtensionSet.GITHUB_WEB,
        style_preset: str = "default",
        heading_style: Optional[Dict[str, Any]] = None,
        text_style: Optional[Dict[str, Any]] = None,
        code_style: Optional[Dict[str, Any]] = None,
        code_theme: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            value=value,
            selectable=selectable,
            extension_set=extension_set,
            **kwargs
        )
        
        # Get base styles from preset
        preset_styles = self.STYLE_PRESETS.get(style_preset, self.STYLE_PRESETS["default"])
        
        # Build markdown style sheet
        self.md_style_sheet = ft.MarkdownStyleSheet(
            # Headings
            h1_text_style=self._build_text_style(preset_styles["h1"], heading_style),
            h2_text_style=self._build_text_style(preset_styles["h2"], heading_style),
            h3_text_style=self._build_text_style(preset_styles["h3"], heading_style),
            h4_text_style=self._build_text_style(preset_styles["h4"], heading_style),
            h5_text_style=self._build_text_style(preset_styles["h5"], heading_style),
            h6_text_style=self._build_text_style(preset_styles["h6"], heading_style),
            
            # Body text
            p_text_style=self._build_text_style(preset_styles["p"], text_style),
            
            # Code
            code_text_style=self._build_text_style(preset_styles["code"], code_style),
            
            # Blockquote
            blockquote_text_style=self._build_text_style(preset_styles["blockquote"], text_style)
        )
        
        # Set code theme if provided
        if code_theme:
            self.code_theme = code_theme
    
    def _build_text_style(self, base_style: Dict[str, Any], overrides: Optional[Dict[str, Any]] = None) -> ft.TextStyle:
        """Build a TextStyle object from base style and overrides."""
        style_dict = base_style.copy()
        if overrides:
            style_dict.update(overrides)
        
        return ft.TextStyle(**style_dict)
    
    def update_content(self, value: str):
        """Update the markdown content.
        
        Args:
            value: New markdown content
        """
        self.value = value
        if hasattr(self, 'update'):
            self.update()
    
    def apply_style_preset(self, preset: str):
        """Apply a different style preset.
        
        Args:
            preset: Name of the preset ('default', 'article', 'compact')
        """
        if preset not in self.STYLE_PRESETS:
            return
            
        preset_styles = self.STYLE_PRESETS[preset]
        
        self.md_style_sheet = ft.MarkdownStyleSheet(
            h1_text_style=self._build_text_style(preset_styles["h1"]),
            h2_text_style=self._build_text_style(preset_styles["h2"]),
            h3_text_style=self._build_text_style(preset_styles["h3"]),
            h4_text_style=self._build_text_style(preset_styles["h4"]),
            h5_text_style=self._build_text_style(preset_styles["h5"]),
            h6_text_style=self._build_text_style(preset_styles["h6"]),
            p_text_style=self._build_text_style(preset_styles["p"]),
            code_text_style=self._build_text_style(preset_styles["code"]),
            blockquote_text_style=self._build_text_style(preset_styles["blockquote"])
        )
        
        if hasattr(self, 'update'):
            self.update()