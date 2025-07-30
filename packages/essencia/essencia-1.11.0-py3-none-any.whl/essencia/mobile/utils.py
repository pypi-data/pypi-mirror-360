"""
Mobile-specific utilities.
"""
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
import platform
import hashlib
import base64
from pathlib import Path

import flet as ft


class DeviceInfo:
    """Device information utilities."""
    
    @staticmethod
    def get_platform() -> str:
        """Get platform name."""
        system = platform.system().lower()
        if system == "darwin":
            return "ios"
        elif system == "linux":
            # Check if Android
            try:
                with open("/proc/version", "r") as f:
                    if "android" in f.read().lower():
                        return "android"
            except:
                pass
            return "linux"
        elif system == "windows":
            return "windows"
        return system
    
    @staticmethod
    def get_device_id() -> str:
        """Get unique device ID."""
        # In production, use platform-specific device ID
        # For now, generate based on hostname
        hostname = platform.node()
        return hashlib.sha256(hostname.encode()).hexdigest()[:16]
    
    @staticmethod
    def get_device_info() -> Dict[str, Any]:
        """Get device information."""
        return {
            "platform": DeviceInfo.get_platform(),
            "device_id": DeviceInfo.get_device_id(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
            "machine": platform.machine(),
            "processor": platform.processor()
        }


class MobilePermissions:
    """Mobile permissions manager."""
    
    CAMERA = "camera"
    LOCATION = "location"
    NOTIFICATIONS = "notifications"
    STORAGE = "storage"
    BIOMETRIC = "biometric"
    
    @staticmethod
    async def request_permission(permission: str) -> bool:
        """Request permission from user."""
        # In production, use platform-specific permission APIs
        # For now, simulate permission grant
        print(f"Requesting permission: {permission}")
        return True
    
    @staticmethod
    async def check_permission(permission: str) -> bool:
        """Check if permission is granted."""
        # In production, check actual permission status
        return True
    
    @staticmethod
    async def open_settings():
        """Open app settings."""
        # Platform-specific implementation
        print("Opening app settings...")


class BiometricAuth:
    """Biometric authentication utilities."""
    
    @staticmethod
    async def is_available() -> bool:
        """Check if biometric authentication is available."""
        platform_name = DeviceInfo.get_platform()
        return platform_name in ["ios", "android"]
    
    @staticmethod
    async def authenticate(reason: str = "Authenticate to continue") -> bool:
        """Perform biometric authentication."""
        if not await BiometricAuth.is_available():
            return False
        
        # In production, use platform-specific biometric APIs
        print(f"Biometric auth requested: {reason}")
        return True
    
    @staticmethod
    async def get_biometric_type() -> Optional[str]:
        """Get available biometric type."""
        platform_name = DeviceInfo.get_platform()
        if platform_name == "ios":
            return "face_id"  # or "touch_id"
        elif platform_name == "android":
            return "fingerprint"
        return None


class MobileNotifications:
    """Mobile notifications manager."""
    
    @staticmethod
    async def request_permission() -> bool:
        """Request notification permission."""
        return await MobilePermissions.request_permission(
            MobilePermissions.NOTIFICATIONS
        )
    
    @staticmethod
    async def schedule_notification(
        title: str,
        body: str,
        scheduled_time: datetime,
        notification_id: Optional[str] = None
    ) -> str:
        """Schedule a notification."""
        if not await MobilePermissions.check_permission(MobilePermissions.NOTIFICATIONS):
            raise PermissionError("Notification permission not granted")
        
        # Generate notification ID
        if not notification_id:
            notification_id = hashlib.md5(
                f"{title}{body}{scheduled_time}".encode()
            ).hexdigest()[:8]
        
        # In production, use platform notification APIs
        print(f"Scheduled notification: {title} at {scheduled_time}")
        
        return notification_id
    
    @staticmethod
    async def cancel_notification(notification_id: str):
        """Cancel a scheduled notification."""
        print(f"Cancelled notification: {notification_id}")
    
    @staticmethod
    async def show_notification(
        title: str,
        body: str,
        action_url: Optional[str] = None
    ):
        """Show immediate notification."""
        if not await MobilePermissions.check_permission(MobilePermissions.NOTIFICATIONS):
            return
        
        # In production, show actual notification
        print(f"Notification: {title} - {body}")


class MobileCamera:
    """Mobile camera utilities."""
    
    @staticmethod
    async def request_permission() -> bool:
        """Request camera permission."""
        return await MobilePermissions.request_permission(
            MobilePermissions.CAMERA
        )
    
    @staticmethod
    async def take_photo() -> Optional[str]:
        """Take a photo and return file path."""
        if not await MobilePermissions.check_permission(MobilePermissions.CAMERA):
            raise PermissionError("Camera permission not granted")
        
        # In production, use camera API
        # Return mock photo path
        return "/tmp/photo.jpg"
    
    @staticmethod
    async def scan_qr_code() -> Optional[str]:
        """Scan QR code and return content."""
        if not await MobilePermissions.check_permission(MobilePermissions.CAMERA):
            raise PermissionError("Camera permission not granted")
        
        # In production, use QR scanner
        return "https://example.com/qr-content"


class MobileFileManager:
    """Mobile file management utilities."""
    
    @staticmethod
    def get_app_directory() -> Path:
        """Get app-specific directory."""
        platform_name = DeviceInfo.get_platform()
        
        if platform_name == "ios":
            # iOS app directory
            return Path.home() / "Documents" / "Essencia"
        elif platform_name == "android":
            # Android app directory
            return Path("/sdcard") / "Essencia"
        else:
            # Desktop fallback
            return Path.home() / ".essencia"
    
    @staticmethod
    def get_cache_directory() -> Path:
        """Get cache directory."""
        return MobileFileManager.get_app_directory() / "cache"
    
    @staticmethod
    def get_documents_directory() -> Path:
        """Get documents directory."""
        return MobileFileManager.get_app_directory() / "documents"
    
    @staticmethod
    async def save_file(content: bytes, filename: str) -> str:
        """Save file to documents directory."""
        docs_dir = MobileFileManager.get_documents_directory()
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = docs_dir / filename
        file_path.write_bytes(content)
        
        return str(file_path)
    
    @staticmethod
    async def pick_file(
        allowed_extensions: Optional[List[str]] = None
    ) -> Optional[Tuple[str, bytes]]:
        """Pick a file from device."""
        # In production, use file picker API
        # Return mock file
        return ("document.pdf", b"Mock file content")


class MobileTheme:
    """Mobile theme utilities."""
    
    @staticmethod
    def get_system_theme() -> ft.ThemeMode:
        """Get system theme preference."""
        # In production, check system theme
        return ft.ThemeMode.LIGHT
    
    @staticmethod
    def get_mobile_theme(primary_color: str = ft.colors.BLUE) -> ft.Theme:
        """Get mobile-optimized theme."""
        return ft.Theme(
            color_scheme_seed=primary_color,
            use_material3=True,
            page_transitions={
                "android": ft.PageTransitionTheme.OPEN_UPWARDS,
                "ios": ft.PageTransitionTheme.CUPERTINO
            }
        )
    
    @staticmethod
    def apply_mobile_styles(page: ft.Page):
        """Apply mobile-specific styles to page."""
        # Set mobile viewport
        page.window_width = 400
        page.window_height = 800
        page.window_resizable = False
        
        # Set padding for safe areas
        page.padding = ft.padding.only(
            top=40,  # Status bar
            bottom=20  # Home indicator
        )
        
        # Enable pull to refresh
        page.scroll = ft.ScrollMode.ALWAYS
        
        # Set mobile fonts
        page.fonts = {
            "SF Pro": "/fonts/SF-Pro.ttf",  # iOS
            "Roboto": "/fonts/Roboto.ttf"   # Android
        }


class MobileConnectivity:
    """Network connectivity utilities."""
    
    @staticmethod
    async def is_online() -> bool:
        """Check if device is online."""
        try:
            # Simple connectivity check
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=3)
            return True
        except:
            return False
    
    @staticmethod
    async def get_connection_type() -> str:
        """Get connection type (wifi, cellular, none)."""
        if not await MobileConnectivity.is_online():
            return "none"
        
        # In production, check actual connection type
        return "wifi"
    
    @staticmethod
    async def monitor_connectivity(callback: callable):
        """Monitor connectivity changes."""
        # In production, use platform APIs
        import asyncio
        
        last_status = await MobileConnectivity.is_online()
        
        while True:
            await asyncio.sleep(5)
            current_status = await MobileConnectivity.is_online()
            
            if current_status != last_status:
                callback(current_status)
                last_status = current_status


class MobileDeepLinks:
    """Deep linking utilities."""
    
    @staticmethod
    def generate_deep_link(
        screen: str,
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate deep link URL."""
        base_url = "essencia://app"
        
        # Build URL
        url = f"{base_url}/{screen}"
        
        if params:
            query_params = "&".join(
                f"{k}={v}" for k, v in params.items()
            )
            url = f"{url}?{query_params}"
        
        return url
    
    @staticmethod
    def parse_deep_link(url: str) -> Tuple[str, Dict[str, Any]]:
        """Parse deep link URL."""
        # Remove scheme
        if url.startswith("essencia://"):
            url = url[11:]
        
        # Split path and query
        parts = url.split("?", 1)
        path = parts[0].lstrip("/")
        
        params = {}
        if len(parts) > 1:
            query = parts[1]
            for param in query.split("&"):
                if "=" in param:
                    key, value = param.split("=", 1)
                    params[key] = value
        
        return path, params