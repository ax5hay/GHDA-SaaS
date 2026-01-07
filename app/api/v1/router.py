"""API v1 router - main router that includes all endpoint modules."""

from fastapi import APIRouter

# TODO: Import endpoint routers as they are created
# from app.api.v1 import documents, reports, analytics, admin, health

router = APIRouter()

# TODO: Include endpoint routers
# router.include_router(documents.router, prefix="/documents", tags=["documents"])
# router.include_router(reports.router, prefix="/reports", tags=["reports"])
# router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
# router.include_router(admin.router, prefix="/admin", tags=["admin"])
# router.include_router(health.router, prefix="/health", tags=["health"])


@router.get("/")
async def api_info() -> dict[str, str]:
    """API version information."""
    return {
        "version": "1.0.0",
        "status": "active",
        "message": "Government Health Data Automation API v1",
    }
