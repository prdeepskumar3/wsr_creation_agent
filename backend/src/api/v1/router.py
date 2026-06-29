from fastapi import APIRouter

api_v1_router = APIRouter()


@api_v1_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return a lightweight health response for local smoke tests."""
    return {"status": "ok"}
