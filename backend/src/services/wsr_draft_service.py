"""Application service for saving, restoring, and validating WSR drafts."""

from typing import Any
from uuid import UUID

from db.models import WsrReport, WsrRisk
from domain.wsr_drafts import DraftMetricCalculator
from domain.wsr_drafts.validation import WsrDraftValidator
from repositories.wsr_draft_repository import WsrDraftRepository
from sqlalchemy.orm import Session
from wsr_shared.dtos import (
    RiskInputDTO,
    WsrDraftResponseDTO,
    WsrDraftSaveRequestDTO,
    WsrDraftValidationResponseDTO,
)
from wsr_shared.enums import WsrGenerationStatus, WsrLifecycleStatus

DRAFT_SCHEMA_VERSION = "wsr-draft.v1"


class DraftAuthorizationError(Exception):
    """Raised when the requester is not assigned to the target account/project."""


class DraftNotFoundError(Exception):
    """Raised when a draft lookup does not find an editable draft report."""


class WsrDraftService:
    """Coordinates draft workflows across repository, calculator, and validator.

    The service owns transaction-level behavior for draft persistence. It keeps AI
    generation out of save operations so PMs can safely save work in progress.
    """

    def __init__(
        self,
        session: Session,
        calculator: DraftMetricCalculator | None = None,
    ) -> None:
        """Create a service bound to one SQLAlchemy session."""
        self._session = session
        self._repository = WsrDraftRepository(session)
        self._calculator = calculator or DraftMetricCalculator()
        self._validator = WsrDraftValidator(metric_calculator=self._calculator)

    def save_draft(self, payload: WsrDraftSaveRequestDTO) -> WsrDraftResponseDTO:
        """Create or update the current draft for one account/project/reporting week.

        The method recalculates metrics before persistence, replaces risk rows with the
        latest form state, commits the transaction, and leaves generation status as
        `NOT_STARTED`.
        """
        if not self._repository.has_project_access(
            payload.account_id,
            payload.project_id,
            payload.prepared_by,
        ):
            raise DraftAuthorizationError("User is not authorized for this account/project.")

        calculated_metrics = self._calculator.calculate(
            payload.delivery_model,
            payload.model_setup,
            payload.weekly_progress,
        )
        entered_snapshot = self._build_entered_snapshot(payload)

        draft = self._repository.find_current_draft(
            payload.account_id,
            payload.project_id,
            payload.reporting_week,
        )
        if draft is None:
            draft = WsrReport(
                account_id=payload.account_id,
                project_id=payload.project_id,
                prepared_by=payload.prepared_by,
                lifecycle_status=WsrLifecycleStatus.DRAFT.value,
                generation_status=WsrGenerationStatus.NOT_STARTED.value,
                reporting_week=payload.reporting_week,
                delivery_model=payload.delivery_model.value,
                schema_version=DRAFT_SCHEMA_VERSION,
                version_number=1,
            )

        draft.prepared_by = payload.prepared_by
        draft.delivery_model = payload.delivery_model.value
        draft.schema_version = DRAFT_SCHEMA_VERSION
        draft.generation_status = WsrGenerationStatus.NOT_STARTED.value
        draft.entered_data_snapshot = entered_snapshot
        draft.model_setup_snapshot = payload.model_setup
        draft.weekly_progress_snapshot = payload.weekly_progress
        draft.calculated_metrics_snapshot = calculated_metrics

        self._repository.save(draft)
        self._repository.replace_risks(draft, self._to_risk_models(payload, draft))
        self._session.commit()
        return self._to_response(draft)

    def get_draft(self, wsr_id: UUID, requested_by: UUID) -> WsrDraftResponseDTO:
        """Return a draft for UI restoration after checking project assignment."""
        draft = self._repository.get_draft(wsr_id)
        if draft is None:
            raise DraftNotFoundError("WSR draft was not found.")
        if not self._repository.has_project_access(
            draft.account_id,
            draft.project_id,
            requested_by,
        ):
            raise DraftAuthorizationError("User is not authorized for this account/project.")
        return self._to_response(draft)

    def validate_draft(self, payload: WsrDraftSaveRequestDTO) -> WsrDraftValidationResponseDTO:
        """Validate draft data without writing to the database."""
        result = self._validator.validate(payload)
        return WsrDraftValidationResponseDTO(
            is_valid=result.is_valid,
            calculated_metrics=result.calculated_metrics,
            errors=result.errors,
        )

    def _build_entered_snapshot(self, payload: WsrDraftSaveRequestDTO) -> dict[str, Any]:
        """Build the UI restore snapshot that is not stored in dedicated columns."""
        return {
            "overview": payload.overview,
            "keyAchievements": payload.key_achievements,
            "nextWeekFocus": payload.next_week_focus,
            "remarks": payload.remarks,
            "risks": [risk.model_dump(mode="json", by_alias=True) for risk in payload.risks],
        }

    def _to_risk_models(
        self,
        payload: WsrDraftSaveRequestDTO,
        draft: WsrReport,
    ) -> list[WsrRisk]:
        """Convert API risk rows into ORM rows linked to the saved WSR report."""
        return [
            WsrRisk(
                account_id=payload.account_id,
                project_id=payload.project_id,
                wsr_report_id=draft.id,
                description=risk.description,
                severity=risk.severity.value,
                status=risk.status.value,
                owner_contact=risk.owner_contact,
                mitigation=risk.mitigation,
                planned_closure_date=risk.planned_closure_date,
                closure_remark=risk.closure_remark,
            )
            for risk in payload.risks
        ]

    def _to_response(self, draft: WsrReport) -> WsrDraftResponseDTO:
        """Convert a report ORM object and its risk rows into the public API DTO."""
        return WsrDraftResponseDTO(
            wsr_id=draft.id,
            account_id=draft.account_id,
            project_id=draft.project_id,
            prepared_by=draft.prepared_by,
            reporting_week=draft.reporting_week,
            delivery_model=draft.delivery_model,
            lifecycle_status=draft.lifecycle_status,
            generation_status=draft.generation_status,
            schema_version=draft.schema_version,
            version_number=draft.version_number,
            entered_data_snapshot=draft.entered_data_snapshot,
            model_setup_snapshot=draft.model_setup_snapshot,
            weekly_progress_snapshot=draft.weekly_progress_snapshot,
            calculated_metrics_snapshot=draft.calculated_metrics_snapshot,
            risks=[self._to_risk_dto(risk) for risk in self._repository.list_risks(draft.id)],
        )

    def _to_risk_dto(self, risk: WsrRisk) -> RiskInputDTO:
        """Convert a persisted risk row back to the draft risk API shape."""
        return RiskInputDTO(
            description=risk.description,
            severity=risk.severity,
            status=risk.status,
            owner_contact=risk.owner_contact,
            mitigation=risk.mitigation,
            planned_closure_date=risk.planned_closure_date,
            closure_remark=risk.closure_remark,
        )
