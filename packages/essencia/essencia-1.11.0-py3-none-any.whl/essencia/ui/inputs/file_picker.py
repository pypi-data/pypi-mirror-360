"""
File picker components with theme integration.
"""

from typing import Optional, List, Callable, Any
import flet as ft
from .theme_helper import apply_input_theme


class ThemedFilePicker(ft.Container):
    """File picker with theme-aware styling.
    
    Provides a file selection interface with preview support
    and theme-consistent styling.
    
    Example:
        ```python
        file_picker = ThemedFilePicker(
            label="Upload Document",
            allowed_extensions=["pdf", "doc", "docx"],
            multiple=False,
            on_result=handle_file_selection
        )
        ```
    """
    
    def __init__(
        self,
        label: Optional[str] = None,
        allowed_extensions: Optional[List[str]] = None,
        multiple: bool = False,
        dialog_title: Optional[str] = None,
        on_result: Optional[Callable[[ft.FilePickerResultEvent], None]] = None,
        show_preview: bool = True,
        **kwargs
    ):
        self._label = label
        self._multiple = multiple
        self._on_result = on_result
        self._show_preview = show_preview
        self._selected_files = []
        
        # Create file picker
        self._file_picker = ft.FilePicker(
            on_result=self._handle_result
        )
        
        # Set dialog options
        self._dialog_title = dialog_title or ("Select Files" if multiple else "Select File")
        self._allowed_extensions = allowed_extensions
        
        # Create UI elements
        controls = []
        
        # Label
        if label:
            self._label_text = ft.Text(label, size=14, weight=ft.FontWeight.W_500)
            controls.append(self._label_text)
            
        # File selection button
        from ..buttons import PrimaryButton
        self._select_button = PrimaryButton(
            text="Choose Files" if multiple else "Choose File",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self._open_picker
        )
        
        # Preview area
        self._preview_area = ft.Column(spacing=5)
        
        # Layout
        controls.extend([
            self._select_button,
            self._preview_area
        ])
        
        content = ft.Column(controls=controls, spacing=10)
        
        super().__init__(content=content, **kwargs)
        
    def did_mount(self):
        """Add file picker to page overlay when mounted."""
        super().did_mount()
        
        if hasattr(self, 'page') and self.page:
            # Add file picker to page overlay
            if self._file_picker not in self.page.overlay:
                self.page.overlay.append(self._file_picker)
                self.page.update()
                
    def _open_picker(self, e):
        """Open the file picker dialog."""
        if self._multiple:
            self._file_picker.pick_files(
                dialog_title=self._dialog_title,
                allowed_extensions=self._allowed_extensions,
                allow_multiple=True
            )
        else:
            self._file_picker.pick_files(
                dialog_title=self._dialog_title,
                allowed_extensions=self._allowed_extensions,
                allow_multiple=False
            )
            
    def _handle_result(self, e: ft.FilePickerResultEvent):
        """Handle file picker result."""
        if e.files:
            self._selected_files = e.files
            if self._show_preview:
                self._update_preview()
                
            if self._on_result:
                self._on_result(e)
                
    def _update_preview(self):
        """Update file preview area."""
        self._preview_area.controls.clear()
        
        for file in self._selected_files:
            # Create file item
            file_item = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(
                            name=self._get_file_icon(file.name),
                            size=20
                        ),
                        ft.Text(
                            file.name,
                            size=12,
                            expand=True,
                            no_wrap=True
                        ),
                        ft.Text(
                            self._format_file_size(file.size),
                            size=11,
                            color=ft.Colors.ON_SURFACE_VARIANT
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            on_click=lambda e, f=file: self._remove_file(f)
                        )
                    ],
                    spacing=10
                ),
                bgcolor=ft.Colors.SURFACE_VARIANT,
                padding=ft.padding.all(8),
                border_radius=ft.border_radius.all(4)
            )
            
            self._preview_area.controls.append(file_item)
            
        self._preview_area.update()
        
    def _get_file_icon(self, filename: str) -> str:
        """Get appropriate icon for file type."""
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        
        icon_map = {
            'pdf': ft.Icons.PICTURE_AS_PDF,
            'doc': ft.Icons.DESCRIPTION,
            'docx': ft.Icons.DESCRIPTION,
            'txt': ft.Icons.TEXT_SNIPPET,
            'jpg': ft.Icons.IMAGE,
            'jpeg': ft.Icons.IMAGE,
            'png': ft.Icons.IMAGE,
            'gif': ft.Icons.IMAGE,
            'mp3': ft.Icons.AUDIO_FILE,
            'mp4': ft.Icons.VIDEO_FILE,
            'zip': ft.Icons.FOLDER_ZIP,
            'rar': ft.Icons.FOLDER_ZIP,
        }
        
        return icon_map.get(ext, ft.Icons.INSERT_DRIVE_FILE)
        
    def _format_file_size(self, size: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
        
    def _remove_file(self, file):
        """Remove a file from selection."""
        self._selected_files = [f for f in self._selected_files if f != file]
        self._update_preview()
        
    def get_files(self) -> List[Any]:
        """Get list of selected files."""
        return self._selected_files
        
    def clear(self):
        """Clear all selected files."""
        self._selected_files = []
        self._preview_area.controls.clear()
        self._preview_area.update()


class ImagePicker(ThemedFilePicker):
    """Specialized file picker for image selection.
    
    Features image preview thumbnails and automatic format filtering.
    
    Example:
        ```python
        avatar_picker = ImagePicker(
            label="Profile Picture",
            max_size_mb=5,
            on_result=handle_avatar_selection
        )
        ```
    """
    
    def __init__(
        self,
        label: Optional[str] = None,
        max_size_mb: Optional[float] = None,
        on_result: Optional[Callable[[ft.FilePickerResultEvent], None]] = None,
        **kwargs
    ):
        # Set image-specific defaults
        kwargs.setdefault('allowed_extensions', ['jpg', 'jpeg', 'png', 'gif', 'webp'])
        kwargs.setdefault('dialog_title', 'Select Image')
        
        self._max_size_mb = max_size_mb
        
        # Wrap on_result to add validation
        if on_result and max_size_mb:
            def validated_result(e):
                # Check file size
                for file in e.files:
                    if file.size > max_size_mb * 1024 * 1024:
                        # Show error
                        if hasattr(self, 'page') and self.page:
                            self.page.show_snack_bar(
                                ft.SnackBar(
                                    content=ft.Text(
                                        f"File {file.name} exceeds {max_size_mb}MB limit"
                                    ),
                                    bgcolor=ft.Colors.ERROR
                                )
                            )
                        return
                on_result(e)
                
            kwargs['on_result'] = validated_result
        else:
            kwargs['on_result'] = on_result
            
        super().__init__(label=label, **kwargs)
        
    def _update_preview(self):
        """Update preview with image thumbnails."""
        self._preview_area.controls.clear()
        
        for file in self._selected_files:
            # For images, we could show actual thumbnails if we had file access
            # For now, show a stylized preview card
            preview_card = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.IMAGE,
                                size=40,
                                color=ft.Colors.ON_SURFACE_VARIANT
                            ),
                            bgcolor=ft.Colors.SURFACE_VARIANT,
                            width=80,
                            height=80,
                            alignment=ft.alignment.center,
                            border_radius=ft.border_radius.all(8)
                        ),
                        ft.Text(
                            file.name,
                            size=11,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            width=80,
                            text_align=ft.TextAlign.CENTER
                        ),
                        ft.Text(
                            self._format_file_size(file.size),
                            size=10,
                            color=ft.Colors.ON_SURFACE_VARIANT,
                            text_align=ft.TextAlign.CENTER
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5
                ),
                on_click=lambda e, f=file: self._remove_file(f),
                tooltip="Click to remove"
            )
            
            self._preview_area.controls.append(preview_card)
            
        # Arrange in a row for images
        if self._selected_files:
            self._preview_area.controls = [
                ft.Row(
                    controls=self._preview_area.controls,
                    spacing=10,
                    wrap=True
                )
            ]
            
        self._preview_area.update()