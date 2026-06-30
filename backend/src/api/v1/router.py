from fastapi import APIRouter

from api.v1.delivery_models import router as delivery_models_router
from api.v1.wsr_approvals import router as wsr_approvals_router
from api.v1.wsr_dashboard import router as wsr_dashboard_router
from api.v1.wsr_drafts import router as wsr_drafts_router
from api.v1.wsr_exports import router as wsr_exports_router

api_v1_router = APIRouter()
api_v1_router.include_router(delivery_models_router)
api_v1_router.include_router(wsr_approvals_router)
api_v1_router.include_router(wsr_dashboard_router)
api_v1_router.include_router(wsr_drafts_router)
api_v1_router.include_router(wsr_exports_router)


@api_v1_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return a lightweight health response for local smoke tests."""
    return {"status": "ok"}
