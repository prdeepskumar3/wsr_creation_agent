"""HTTP endpoints for WSR draft save, restore, and validation flows."""

from uuid import UUID

from db.session import get_db_session
from fastapi import APIRouter, Depends, HTTPException, status
from services.wsr_draft_service import (
    DraftAuthorizationError,
    DraftNotFoundError,
    WsrDraftService,
)
from sqlalchemy.orm import Session
from wsr_shared.dtos import (
    WsrDraftResponseDTO,
    WsrDraftSaveRequestDTO,
    WsrDraftValidationResponseDTO,
)

router = APIRouter(prefix="/wsr-drafts", tags=["wsr-drafts"])
DB_SESSION_DEPENDENCY = Depends(get_db_session)


@router.post("", response_model=WsrDraftResponseDTO)
def save_wsr_draft(
    payload: WsrDraftSaveRequestDTO,
    session: Session = DB_SESSION_DEPENDENCY,
) -> WsrDraftResponseDTO:
    """Persist a PM draft without triggering the LangGraph generation workflow."""
    try:
        return WsrDraftService(session).save_draft(payload)
    except DraftAuthorizationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc


@router.post("/validate", response_model=WsrDraftValidationResponseDTO)
def validate_wsr_draft(
    payload: WsrDraftSaveRequestDTO,
    session: Session = DB_SESSION_DEPENDENCY,
) -> WsrDraftValidationResponseDTO:
    """Return calculated metrics and field-level errors for a draft payload."""
    return WsrDraftService(session).validate_draft(payload)


@router.get("/{wsr_id}", response_model=WsrDraftResponseDTO)
def get_wsr_draft(
    wsr_id: UUID,
    requested_by: UUID,
    session: Session = DB_SESSION_DEPENDENCY,
) -> WsrDraftResponseDTO:
    """Restore a saved draft for an authorized requester."""
    try:
        return WsrDraftService(session).get_draft(wsr_id, requested_by)
    except DraftAuthorizationError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc
    except DraftNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
