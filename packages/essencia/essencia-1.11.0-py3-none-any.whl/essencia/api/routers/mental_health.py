"""
Mental health assessments and tracking endpoints.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_assessments():
    """List mental health assessments."""
    return {"message": "Mental health endpoint"}