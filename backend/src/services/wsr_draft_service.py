from typing import Any
from uuid import UUID

from db.models import WsrReport, WsrRisk
from domain.wsr_drafts import DraftMetricCalculator
from repositories.wsr_draft_repository import WsrDraftRepository
from sqlalchemy.orm import Session
from wsr_shared.dtos import RiskInputDTO, WsrDraftResponseDTO, WsrDraftSaveRequestDTO
from wsr_shared.enums import WsrGenerationStatus, WsrLifecycleStatus

DRAFT_SCHEMA_VERSION = "wsr-draft.v1"


class DraftAuthorizationError(Exception):
    """Raised when a user cannot save a draft for the requested project."""


class DraftNotFoundError(Exception):
    """Raised when a requested WSR draft does not exist."""


class WsrDraftService:
    """Coordinates WSR draft validation, calculation, and persistence."""

    def __init__(
        self,
        session: Session,
        calculator: DraftMetricCalculator | None = None,
    ) -> None:
        self._session = session
        self._repository = WsrDraftRepository(session)
        self._calculator = calculator or DraftMetricCalculator()

    def save_draft(self, payload: WsrDraftSaveRequestDTO) -> WsrDraftResponseDTO:
        """Create or update a weekly WSR draft without starting AI generation."""
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
        """Return the saved WSR draft state for UI restoration."""
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

    def _build_entered_snapshot(self, payload: WsrDraftSaveRequestDTO) -> dict[str, Any]:
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
        return RiskInputDTO(
            description=risk.description,
            severity=risk.severity,
            status=risk.status,
            owner_contact=risk.owner_contact,
            mitigation=risk.mitigation,
            planned_closure_date=risk.planned_closure_date,
            closure_remark=risk.closure_remark,
        )
