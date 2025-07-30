"""
Appointment scheduling and management endpoints.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_appointments():
    """List appointments."""
    return {"message": "Appointments endpoint"}