"""HTTP endpoints for executive WSR dashboard summaries."""

from uuid import UUID

from db.session import get_db_session
from fastapi import APIRouter, Depends
from services.wsr_dashboard_service import WsrDashboardService
from sqlalchemy.orm import Session
from wsr_shared.dtos import WsrDashboardResponseDTO

router = APIRouter(prefix="/wsr-dashboard", tags=["wsr-dashboard"])
DB_SESSION_DEPENDENCY = Depends(get_db_session)


@router.get("", response_model=WsrDashboardResponseDTO)
def get_wsr_dashboard(
    requested_by: UUID,
    account_id: UUID | None = None,
    session: Session = DB_SESSION_DEPENDENCY,
) -> WsrDashboardResponseDTO:
    """Return latest approved WSR health across authorized projects."""
    return WsrDashboardService(session).get_dashboard(requested_by, account_id)
