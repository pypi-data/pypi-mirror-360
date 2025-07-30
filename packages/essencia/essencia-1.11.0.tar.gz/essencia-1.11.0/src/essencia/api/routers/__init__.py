"""
API routers for different endpoints.
"""
from .auth import router as auth_router
from .patients import router as patients_router
from .appointments import router as appointments_router
from .medications import router as medications_router
from .vital_signs import router as vital_signs_router
from .mental_health import router as mental_health_router
from .laboratory import router as laboratory_router
from .admin import router as admin_router

__all__ = [
    "auth_router",
    "patients_router",
    "appointments_router",
    "medications_router",
    "vital_signs_router",
    "mental_health_router",
    "laboratory_router",
    "admin_router"
]