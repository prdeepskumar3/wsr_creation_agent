"""HTTP endpoints for customer-safe WSR exports."""

from uuid import UUID

from db.session import get_db_session
from fastapi import APIRouter, Depends, HTTPException, status
from services.wsr_export_service import (
    WsrExportAuthorizationError,
    WsrExportNotFoundError,
    WsrExportService,
    WsrExportStateError,
)
from sqlalchemy.orm import Session
from wsr_shared.dtos import WsrExportRequestDTO, WsrExportResponseDTO

router = APIRouter(prefix="/wsr-exports", tags=["wsr-exports"])
DB_SESSION_DEPENDENCY = Depends(get_db_session)


@router.post("/{wsr_id}/pptx", response_model=WsrExportResponseDTO)
def export_wsr_to_pptx(
    wsr_id: UUID,
    requested_by: UUID,
    payload: WsrExportRequestDTO,
    session: Session = DB_SESSION_DEPENDENCY,
) -> WsrExportResponseDTO:
    """Queue a PPTX export for an approved customer-facing WSR."""
    try:
        return WsrExportService(session).request_pptx_export(wsr_id, requested_by, payload)
    except WsrExportAuthorizationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except WsrExportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except WsrExportStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
