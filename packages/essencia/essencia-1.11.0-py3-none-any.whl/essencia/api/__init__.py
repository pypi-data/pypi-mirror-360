"""
API module for Essencia framework.

Provides FastAPI-based REST API with automatic OpenAPI documentation.
"""
from .app import create_app, get_app_settings
from .dependencies import (
    get_db,
    get_cache,
    get_current_user,
    require_permission,
    rate_limit
)
from .routers import (
    auth_router,
    patients_router,
    appointments_router,
    medications_router,
    vital_signs_router,
    mental_health_router,
    admin_router
)

__all__ = [
    # App
    "create_app",
    "get_app_settings",
    # Dependencies
    "get_db",
    "get_cache",
    "get_current_user",
    "require_permission",
    "rate_limit",
    # Routers
    "auth_router",
    "patients_router", 
    "appointments_router",
    "medications_router",
    "vital_signs_router",
    "mental_health_router",
    "admin_router"
]