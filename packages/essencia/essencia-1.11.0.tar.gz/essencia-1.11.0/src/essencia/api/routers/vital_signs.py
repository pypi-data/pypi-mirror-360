"""
Vital signs recording and monitoring endpoints.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_vital_signs():
    """List vital signs."""
    return {"message": "Vital signs endpoint"}