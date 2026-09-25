from fastapi import APIRouter
from typing import Dict, Any

try:
    from backend.app.db.session import check_database_health
except ImportError:
    from app.db.session import check_database_health

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Health Check")
async def health_check() -> Dict[str, Any]:
    """
    Returns service health and operational status, including database connectivity.
    Strictly redacts sensitive connection details and passwords.
    """
    db_health = await check_database_health()
    return {
        "status": "ok",
        "service": "lexguard-backend",
        "version": "1.0.0",
        "database": {
            "connected": db_health["connected"],
            "vector_extension": db_health["vector_extension"],
        },
    }
