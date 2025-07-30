"""
Administrative functions endpoints.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def admin_dashboard():
    """Admin dashboard data."""
    return {"message": "Admin endpoint"}