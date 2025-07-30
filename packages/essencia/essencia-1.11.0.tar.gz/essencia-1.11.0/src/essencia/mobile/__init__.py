"""
Mobile app support module for Essencia using Flet.

Provides mobile-optimized UI components and navigation patterns.
"""
from .app import MobileApp, create_mobile_app
from .navigation import (
    MobileNavigator,
    MobileRoute,
    BottomNavigation,
    TabNavigation
)
from .components import (
    MobileHeader,
    MobileCard,
    MobileList,
    MobileForm,
    MobileButton,
    MobileDialog
)
from .screens import (
    LoginScreen,
    HomeScreen,
    PatientScreen,
    AppointmentScreen,
    MedicationScreen,
    ProfileScreen
)
from .storage import OfflineStorage, SyncManager, SyncStatus
from .utils import (
    DeviceInfo,
    MobilePermissions,
    BiometricAuth,
    MobileNotifications,
    MobileCamera,
    MobileFileManager,
    MobileTheme,
    MobileConnectivity,
    MobileDeepLinks
)

__all__ = [
    # App
    "MobileApp",
    "create_mobile_app",
    # Navigation
    "MobileNavigator",
    "MobileRoute",
    "BottomNavigation",
    "TabNavigation",
    # Components
    "MobileHeader",
    "MobileCard",
    "MobileList",
    "MobileForm",
    "MobileButton",
    "MobileDialog",
    # Screens
    "LoginScreen",
    "HomeScreen",
    "PatientScreen",
    "AppointmentScreen",
    "MedicationScreen",
    "ProfileScreen",
    # Storage
    "OfflineStorage",
    "SyncManager",
    "SyncStatus",
    # Utils
    "DeviceInfo",
    "MobilePermissions",
    "BiometricAuth",
    "MobileNotifications",
    "MobileCamera",
    "MobileFileManager",
    "MobileTheme",
    "MobileConnectivity",
    "MobileDeepLinks"
]