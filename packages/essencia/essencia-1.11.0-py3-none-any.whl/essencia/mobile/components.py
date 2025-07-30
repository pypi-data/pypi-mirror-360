"""
Mobile-optimized UI components.
"""
from typing import Optional, List, Dict, Any, Callable, Union
import flet as ft


class MobileHeader(ft.Container):
    """Mobile screen header."""
    
    def __init__(
        self,
        title: str,
        subtitle: Optional[str] = None,
        back_button: bool = False,
        on_back: Optional[Callable] = None,
        actions: Optional[List[ft.Control]] = None,
        **kwargs
    ):
        controls = []
        
        # Back button and title row
        title_row_controls = []
        if back_button and on_back:
            title_row_controls.append(
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: on_back(),
                    icon_size=24
                )
            )
        
        # Title column
        title_column = ft.Column(
            controls=[
                ft.Text(
                    title,
                    size=24,
                    weight=ft.FontWeight.BOLD
                )
            ],
            spacing=2
        )
        
        if subtitle:
            title_column.controls.append(
                ft.Text(
                    subtitle,
                    size=14,
                    color=ft.colors.ON_SURFACE_VARIANT
                )
            )
        
        title_row_controls.append(title_column)
        
        # Actions
        if actions:
            title_row_controls.append(ft.Row(controls=actions))
        
        controls.append(
            ft.Row(
                controls=title_row_controls,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                expand=True
            )
        )
        
        super().__init__(
            content=ft.Column(controls=controls),
            padding=ft.padding.only(left=16, right=16, top=16, bottom=8),
            **kwargs
        )


class MobileCard(ft.Card):
    """Mobile-optimized card component."""
    
    def __init__(
        self,
        title: Optional[str] = None,
        subtitle: Optional[str] = None,
        content: Optional[ft.Control] = None,
        actions: Optional[List[ft.Control]] = None,
        on_click: Optional[Callable] = None,
        leading: Optional[ft.Control] = None,
        trailing: Optional[ft.Control] = None,
        **kwargs
    ):
        card_content = []
        
        # Header section
        if title or subtitle or leading or trailing:
            header_controls = []
            
            if leading:
                header_controls.append(leading)
            
            # Title and subtitle
            text_column = ft.Column(spacing=2, expand=True)
            if title:
                text_column.controls.append(
                    ft.Text(title, size=16, weight=ft.FontWeight.W_500)
                )
            if subtitle:
                text_column.controls.append(
                    ft.Text(subtitle, size=14, color=ft.colors.ON_SURFACE_VARIANT)
                )
            
            header_controls.append(text_column)
            
            if trailing:
                header_controls.append(trailing)
            
            card_content.append(
                ft.Container(
                    content=ft.Row(
                        controls=header_controls,
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=ft.padding.symmetric(horizontal=16, vertical=12)
                )
            )
            
            if content:
                card_content.append(ft.Divider(height=1))
        
        # Main content
        if content:
            card_content.append(
                ft.Container(
                    content=content,
                    padding=16 if not (title or subtitle) else ft.padding.only(
                        left=16, right=16, bottom=16
                    )
                )
            )
        
        # Actions
        if actions:
            if content or title:
                card_content.append(ft.Divider(height=1))
            
            card_content.append(
                ft.Container(
                    content=ft.Row(
                        controls=actions,
                        alignment=ft.MainAxisAlignment.END,
                        spacing=8
                    ),
                    padding=8
                )
            )
        
        super().__init__(
            content=ft.Column(
                controls=card_content,
                spacing=0
            ),
            elevation=1,
            **kwargs
        )
        
        if on_click:
            self.on_click = on_click


class MobileList(ft.ListView):
    """Mobile-optimized list view."""
    
    def __init__(
        self,
        items: Optional[List[ft.Control]] = None,
        item_builder: Optional[Callable[[Any], ft.Control]] = None,
        data: Optional[List[Any]] = None,
        on_item_click: Optional[Callable[[Any], None]] = None,
        empty_message: str = "Nenhum item encontrado",
        loading: bool = False,
        **kwargs
    ):
        controls = []
        
        if loading:
            # Show loading indicator
            controls.append(
                ft.Container(
                    content=ft.ProgressRing(),
                    alignment=ft.alignment.center,
                    height=200
                )
            )
        elif items:
            controls = items
        elif item_builder and data:
            for item in data:
                control = item_builder(item)
                if on_item_click:
                    control.on_click = lambda e, i=item: on_item_click(i)
                controls.append(control)
        
        if not controls and not loading:
            # Show empty message
            controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.icons.INBOX_OUTLINED,
                                size=64,
                                color=ft.colors.ON_SURFACE_VARIANT
                            ),
                            ft.Text(
                                empty_message,
                                size=16,
                                color=ft.colors.ON_SURFACE_VARIANT,
                                text_align=ft.TextAlign.CENTER
                            )
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=16
                    ),
                    alignment=ft.alignment.center,
                    height=300
                )
            )
        
        super().__init__(
            controls=controls,
            spacing=8,
            padding=ft.padding.symmetric(horizontal=16),
            **kwargs
        )


class MobileForm(ft.Column):
    """Mobile-optimized form container."""
    
    def __init__(
        self,
        fields: List[ft.Control],
        on_submit: Optional[Callable[[Dict[str, Any]], None]] = None,
        submit_text: str = "Salvar",
        **kwargs
    ):
        self.fields = {}
        controls = []
        
        # Add fields with proper spacing
        for field in fields:
            controls.append(field)
            
            # Track TextField and Dropdown controls
            if isinstance(field, (ft.TextField, ft.Dropdown)):
                if hasattr(field, 'label'):
                    self.fields[field.label] = field
        
        # Add submit button
        if on_submit:
            controls.append(
                ft.Container(height=16)  # Spacer
            )
            controls.append(
                MobileButton(
                    text=submit_text,
                    on_click=lambda e: self._handle_submit(on_submit),
                    width=float("inf"),
                    style=MobileButtonStyle.PRIMARY
                )
            )
        
        super().__init__(
            controls=controls,
            spacing=16,
            **kwargs
        )
    
    def _handle_submit(self, on_submit: Callable):
        """Handle form submission."""
        data = {}
        for name, field in self.fields.items():
            if hasattr(field, 'value'):
                data[name] = field.value
        on_submit(data)
    
    def get_values(self) -> Dict[str, Any]:
        """Get all form values."""
        data = {}
        for name, field in self.fields.items():
            if hasattr(field, 'value'):
                data[name] = field.value
        return data
    
    def set_values(self, data: Dict[str, Any]):
        """Set form values."""
        for name, value in data.items():
            if name in self.fields and hasattr(self.fields[name], 'value'):
                self.fields[name].value = value


class MobileButtonStyle:
    """Mobile button styles."""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    TEXT = "text"
    DANGER = "danger"


class MobileButton(ft.ElevatedButton):
    """Mobile-optimized button."""
    
    def __init__(
        self,
        text: str,
        on_click: Optional[Callable] = None,
        icon: Optional[str] = None,
        style: str = MobileButtonStyle.PRIMARY,
        loading: bool = False,
        **kwargs
    ):
        # Set style-based properties
        if style == MobileButtonStyle.PRIMARY:
            kwargs.setdefault('bgcolor', ft.colors.PRIMARY)
            kwargs.setdefault('color', ft.colors.ON_PRIMARY)
        elif style == MobileButtonStyle.SECONDARY:
            kwargs.setdefault('bgcolor', ft.colors.SECONDARY_CONTAINER)
            kwargs.setdefault('color', ft.colors.ON_SECONDARY_CONTAINER)
        elif style == MobileButtonStyle.TEXT:
            kwargs.setdefault('bgcolor', ft.colors.TRANSPARENT)
            kwargs.setdefault('color', ft.colors.PRIMARY)
            kwargs.setdefault('elevation', 0)
        elif style == MobileButtonStyle.DANGER:
            kwargs.setdefault('bgcolor', ft.colors.ERROR)
            kwargs.setdefault('color', ft.colors.ON_ERROR)
        
        # Set default height for mobile
        kwargs.setdefault('height', 48)
        
        # Handle loading state
        if loading:
            content = ft.Row(
                controls=[
                    ft.ProgressRing(width=16, height=16, stroke_width=2),
                    ft.Text(text)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=8
            )
            on_click = None  # Disable click when loading
        else:
            content = ft.Text(text)
            if icon:
                content = ft.Row(
                    controls=[
                        ft.Icon(icon, size=20),
                        ft.Text(text)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=8
                )
        
        super().__init__(
            content=content,
            on_click=on_click,
            **kwargs
        )


class MobileDialog(ft.AlertDialog):
    """Mobile-optimized dialog."""
    
    def __init__(
        self,
        title: str,
        content: Optional[Union[str, ft.Control]] = None,
        actions: Optional[List[ft.Control]] = None,
        on_dismiss: Optional[Callable] = None,
        **kwargs
    ):
        # Convert string content to Text
        if isinstance(content, str):
            content = ft.Text(content)
        
        # Default actions if none provided
        if not actions:
            actions = [
                ft.TextButton(
                    "Fechar",
                    on_click=lambda e: self.close_dialog(e.page)
                )
            ]
        
        super().__init__(
            title=ft.Text(title),
            content=content,
            actions=actions,
            actions_alignment=ft.MainAxisAlignment.END,
            **kwargs
        )
        
        if on_dismiss:
            self.on_dismiss = on_dismiss
    
    def close_dialog(self, page: ft.Page):
        """Close the dialog."""
        self.open = False
        page.update()


class MobileSearchBar(ft.Container):
    """Mobile search bar component."""
    
    def __init__(
        self,
        hint_text: str = "Pesquisar...",
        on_search: Optional[Callable[[str], None]] = None,
        on_clear: Optional[Callable] = None,
        **kwargs
    ):
        self.search_field = ft.TextField(
            hint_text=hint_text,
            border=ft.InputBorder.NONE,
            filled=True,
            prefix_icon=ft.icons.SEARCH,
            on_change=lambda e: on_search(e.control.value) if on_search else None,
            expand=True
        )
        
        controls = [self.search_field]
        
        # Add clear button if there's text
        if on_clear:
            self.clear_button = ft.IconButton(
                icon=ft.icons.CLEAR,
                on_click=lambda e: self._handle_clear(on_clear),
                visible=False
            )
            controls.append(self.clear_button)
            
            # Show/hide clear button based on text
            self.search_field.on_change = lambda e: self._handle_text_change(e, on_search)
        
        super().__init__(
            content=ft.Row(controls=controls),
            padding=ft.padding.symmetric(horizontal=8),
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=28,
            height=48,
            **kwargs
        )
    
    def _handle_text_change(self, e, on_search):
        """Handle text change."""
        if hasattr(self, 'clear_button'):
            self.clear_button.visible = bool(e.control.value)
            e.page.update()
        
        if on_search:
            on_search(e.control.value)
    
    def _handle_clear(self, on_clear):
        """Handle clear button click."""
        self.search_field.value = ""
        if hasattr(self, 'clear_button'):
            self.clear_button.visible = False
        on_clear()


class MobileChip(ft.Chip):
    """Mobile-optimized chip component."""
    
    def __init__(
        self,
        label: str,
        selected: bool = False,
        on_select: Optional[Callable[[bool], None]] = None,
        on_delete: Optional[Callable] = None,
        avatar: Optional[ft.Control] = None,
        **kwargs
    ):
        super().__init__(
            label=ft.Text(label),
            selected=selected,
            on_select=lambda e: on_select(e.control.selected) if on_select else None,
            on_delete=lambda e: on_delete() if on_delete else None,
            leading=avatar,
            **kwargs
        )