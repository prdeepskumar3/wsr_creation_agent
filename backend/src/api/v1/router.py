from fastapi import APIRouter

from api.v1.wsr_drafts import router as wsr_drafts_router

api_v1_router = APIRouter()
api_v1_router.include_router(wsr_drafts_router)


@api_v1_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return a lightweight health response for local smoke tests."""
    return {"status": "ok"}
