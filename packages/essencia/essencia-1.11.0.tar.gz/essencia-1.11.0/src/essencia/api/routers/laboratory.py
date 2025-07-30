"""
Laboratory tests and results endpoints.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_lab_tests():
    """List laboratory tests."""
    return {"message": "Laboratory endpoint"}