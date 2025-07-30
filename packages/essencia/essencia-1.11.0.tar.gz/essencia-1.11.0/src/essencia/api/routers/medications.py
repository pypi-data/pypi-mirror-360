"""
Medication and prescription management endpoints.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_medications():
    """List medications."""
    return {"message": "Medications endpoint"}