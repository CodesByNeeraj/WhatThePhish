from fastapi import APIRouter

from backend.services.store import get_stats

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/stats")
async def stats():
    return get_stats()
