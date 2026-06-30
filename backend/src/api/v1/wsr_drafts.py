"""HTTP endpoints for WSR draft save, restore, and validation flows."""

from uuid import UUID

from db.session import get_db_session
from fastapi import APIRouter, Depends, HTTPException, status
from services.wsr_draft_service import (
    DraftAuthorizationError,
    DraftNotFoundError,
    WsrDraftService,
    WsrGenerationStateError,
    WsrReviewStateError,
)
from sqlalchemy.orm import Session
from wsr_shared.dtos import (
    RiskInputDTO,
    WsrDraftResponseDTO,
    WsrDraftSaveRequestDTO,
    WsrDraftValidationResponseDTO,
    WsrGenerationStartResponseDTO,
    WsrPrefillResponseDTO,
    WsrReviewRequestDTO,
    WsrReviewResponseDTO,
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


@router.get("/carry-forward-risks", response_model=list[RiskInputDTO])
def list_carry_forward_risks(
    account_id: UUID,
    project_id: UUID,
    requested_by: UUID,
    session: Session = DB_SESSION_DEPENDENCY,
) -> list[RiskInputDTO]:
    """Return active risks from the latest approved WSR for the same project."""
    service = WsrDraftService(session)
    if not service.user_can_access_project(account_id, project_id, requested_by):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized for this account/project.",
        )
    risks: list[RiskInputDTO] = service.list_carry_forward_risks(account_id, project_id)
    return risks


@router.get("/prefill", response_model=WsrPrefillResponseDTO)
def get_wsr_prefill(
    account_id: UUID,
    project_id: UUID,
    requested_by: UUID,
    session: Session = DB_SESSION_DEPENDENCY,
) -> WsrPrefillResponseDTO:
    """Return reusable data from the latest approved WSR for the same project."""
    service = WsrDraftService(session)
    if not service.user_can_access_project(account_id, project_id, requested_by):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized for this account/project.",
        )
    return service.get_prefill(account_id, project_id)


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


@router.post("/{wsr_id}/generate", response_model=WsrGenerationStartResponseDTO)
def start_wsr_generation(
    wsr_id: UUID,
    requested_by: UUID,
    session: Session = DB_SESSION_DEPENDENCY,
) -> WsrGenerationStartResponseDTO:
    """Validate a persisted draft and start the LangGraph generation workflow."""
    try:
        return WsrDraftService(session).start_generation(wsr_id, requested_by)
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
    except WsrGenerationStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post("/{wsr_id}/review-preview", response_model=WsrReviewResponseDTO)
def review_wsr_preview(
    wsr_id: UUID,
    requested_by: UUID,
    payload: WsrReviewRequestDTO,
    session: Session = DB_SESSION_DEPENDENCY,
) -> WsrReviewResponseDTO:
    """Persist PM-edited ready-to-share WSR preview at the HITL checkpoint."""
    try:
        return WsrDraftService(session).review_wsr_preview(wsr_id, requested_by, payload)
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
    except WsrReviewStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
