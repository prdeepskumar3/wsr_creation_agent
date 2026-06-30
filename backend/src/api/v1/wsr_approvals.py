"""HTTP endpoints for formal WSR approval decisions."""

from uuid import UUID

from db.session import get_db_session
from fastapi import APIRouter, Depends, HTTPException, status
from services.wsr_approval_service import (
    WsrApprovalAuthorizationError,
    WsrApprovalNotFoundError,
    WsrApprovalService,
    WsrApprovalStateError,
)
from sqlalchemy.orm import Session
from wsr_shared.dtos import WsrApprovalRequestDTO, WsrApprovalResponseDTO

router = APIRouter(prefix="/wsr-approvals", tags=["wsr-approvals"])
DB_SESSION_DEPENDENCY = Depends(get_db_session)


@router.post("/{wsr_id}/approve", response_model=WsrApprovalResponseDTO)
def approve_wsr_content_version(
    wsr_id: UUID,
    requested_by: UUID,
    payload: WsrApprovalRequestDTO,
    session: Session = DB_SESSION_DEPENDENCY,
) -> WsrApprovalResponseDTO:
    """Approve a reviewed customer-facing WSR content version."""
    try:
        return WsrApprovalService(session).approve_content_version(
            wsr_id,
            requested_by,
            payload,
        )
    except WsrApprovalAuthorizationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except WsrApprovalNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except WsrApprovalStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
