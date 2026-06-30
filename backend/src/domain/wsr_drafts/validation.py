"""Validation rules for delivery-model-specific WSR draft data."""

import re
from dataclasses import dataclass
from datetime import date
from typing import Any
from uuid import UUID

from wsr_shared.dtos import FieldValidationErrorDTO, RiskInputDTO, WsrDraftSaveRequestDTO
from wsr_shared.enums import DeliveryModel, RagStatus, RiskSeverity, RiskStatus

from domain.delivery_models.validation import DeliveryModelPayloadValidator
from domain.wsr_drafts.calculations import DraftMetricCalculator

MIN_NARRATIVE_ITEMS = 3
MIN_NARRATIVE_ITEM_LENGTH = 5


@dataclass(frozen=True)
class DraftValidationResult:
    """Validation result passed from the domain layer to API/service callers.

    `calculated_metrics` always reflects the backend recalculation for the submitted
    payload, even when validation fails. This lets the UI show current numbers beside
    field-level errors.
    """

    calculated_metrics: dict[str, Any]
    errors: list[FieldValidationErrorDTO]
    warnings: list[FieldValidationErrorDTO]

    @property
    def is_valid(self) -> bool:
        """Return whether the draft is valid for AI generation."""
        return not self.errors


@dataclass(frozen=True)
class ExistingProjectRisk:
    """Project risk already persisted outside the submitted WSR payload."""

    risk_id: UUID
    description: str
    status: RiskStatus
    planned_closure_date: date | None


class WsrDraftValidator:
    """Validates draft data before the PM starts AI generation.

    The validator combines delivery-model metadata checks with domain cross-field rules.
    It does not persist anything and returns field-level errors suitable for direct UI
    highlighting.
    """

    def __init__(
        self,
        required_field_validator: DeliveryModelPayloadValidator | None = None,
        metric_calculator: DraftMetricCalculator | None = None,
    ) -> None:
        """Create a validator with injectable collaborators for focused unit tests."""
        self._required_field_validator = required_field_validator or DeliveryModelPayloadValidator()
        self._metric_calculator = metric_calculator or DraftMetricCalculator()

    def validate(
        self,
        payload: WsrDraftSaveRequestDTO,
        existing_project_risks: list[ExistingProjectRisk] | None = None,
    ) -> DraftValidationResult:
        """Validate one draft payload and return recalculated metrics plus errors."""
        combined_payload = payload.model_setup | payload.weekly_progress
        project_risks = existing_project_risks or []
        calculated_metrics = self._metric_calculator.calculate(
            payload.delivery_model,
            payload.model_setup,
            payload.weekly_progress,
        )
        errors = self._required_field_errors(payload.delivery_model, combined_payload)
        errors.extend(self._cross_field_errors(payload, combined_payload, calculated_metrics))
        errors.extend(self._rag_conflict_errors(payload, combined_payload, calculated_metrics))
        errors.extend(self._narrative_errors(payload))
        errors.extend(self._risk_row_errors(payload.risks, project_risks))
        warnings = self._risk_row_warnings(payload.risks)
        return DraftValidationResult(
            calculated_metrics=calculated_metrics,
            errors=errors,
            warnings=warnings,
        )

    def _required_field_errors(
        self,
        delivery_model: DeliveryModel,
        combined_payload: dict[str, Any],
    ) -> list[FieldValidationErrorDTO]:
        """Return missing-field errors based on delivery-model registry metadata."""
        return [
            self._error(field, "REQUIRED", "This field is required.")
            for field in sorted(
                self._required_field_validator.missing_required_fields(
                    delivery_model,
                    combined_payload,
                )
            )
        ]

    def _cross_field_errors(
        self,
        payload: WsrDraftSaveRequestDTO,
        combined_payload: dict[str, Any],
        calculated_metrics: dict[str, Any],
    ) -> list[FieldValidationErrorDTO]:
        """Dispatch to the delivery-model-specific cross-field rule set."""
        if payload.delivery_model == DeliveryModel.SPRINT:
            return self._sprint_cross_field_errors(combined_payload)
        if payload.delivery_model == DeliveryModel.PI:
            return self._pi_cross_field_errors(combined_payload, calculated_metrics)
        return []

    def _sprint_cross_field_errors(self, values: dict[str, Any]) -> list[FieldValidationErrorDTO]:
        """Validate Sprint actuals against planned story and point scope."""
        errors: list[FieldValidationErrorDTO] = []
        if self._number(values, "storiesCompleted") > self._number(values, "plannedStories"):
            errors.append(
                self._error(
                    "storiesCompleted",
                    "EXCEEDS_PLANNED_STORIES",
                    "Completed stories cannot exceed planned stories.",
                )
            )
        if self._number(values, "storyPointsCompleted") > self._number(
            values, "plannedStoryPoints"
        ):
            errors.append(
                self._error(
                    "storyPointsCompleted",
                    "EXCEEDS_PLANNED_POINTS",
                    "Completed story points cannot exceed planned story points.",
                )
            )
        return errors

    def _pi_cross_field_errors(
        self,
        values: dict[str, Any],
        calculated_metrics: dict[str, Any],
    ) -> list[FieldValidationErrorDTO]:
        """Validate PI sprint position, completed points, and velocity sanity."""
        errors: list[FieldValidationErrorDTO] = []
        current_sprint = self._number(values, "currentSprint")
        total_sprints = self._number(values, "totalSprints")
        if current_sprint > total_sprints:
            errors.append(
                self._error(
                    "currentSprint",
                    "CURRENT_SPRINT_EXCEEDS_TOTAL",
                    "Current sprint cannot exceed total sprints in the PI.",
                )
            )

        completed_points = self._number(values, "completedToDateStoryPoints") + self._number(
            values,
            "storyPointsCompletedThisWeek",
        )
        if completed_points > self._number(values, "plannedStoryPoints"):
            errors.append(
                self._error(
                    "completedToDateStoryPoints",
                    "EXCEEDS_PLANNED_POINTS",
                    "Completed PI points cannot exceed planned PI story points.",
                )
            )
        if calculated_metrics.get("requiredVelocity", 0) < 0:
            errors.append(
                self._error(
                    "requiredVelocity",
                    "INVALID_REQUIRED_VELOCITY",
                    "Required velocity must be zero or greater.",
                )
            )
        return errors

    def _rag_conflict_errors(
        self,
        payload: WsrDraftSaveRequestDTO,
        combined_payload: dict[str, Any],
        calculated_metrics: dict[str, Any],
    ) -> list[FieldValidationErrorDTO]:
        """Require PM explanation when selected RAG differs from calculated health."""
        rag_status = combined_payload.get("ragStatus")
        allowed_rag_values = {status.value for status in RagStatus}
        if not isinstance(rag_status, str) or rag_status not in allowed_rag_values:
            return [
                self._error("ragStatus", "INVALID_RAG_STATUS", "Select a valid RAG status.")
            ]

        expected_rag = self._expected_rag(payload.delivery_model, calculated_metrics)
        remarks = combined_payload.get("remarks")
        if rag_status != expected_rag.value and not self._has_text(remarks):
            return [
                self._error(
                    "remarks",
                    "RAG_REMARKS_REQUIRED",
                    "Remarks are required when selected RAG differs "
                    "from calculated delivery health.",
                )
            ]
        return []

    def _narrative_errors(self, payload: WsrDraftSaveRequestDTO) -> list[FieldValidationErrorDTO]:
        """Validate customer-facing narrative inputs before AI generation starts."""
        errors: list[FieldValidationErrorDTO] = []
        if not self._has_text(payload.overview):
            errors.append(
                self._error(
                    "overview",
                    "REQUIRED",
                    "Project overview is required before generation.",
                )
            )

        achievements = self._narrative_items(payload.key_achievements)
        if len(achievements) < MIN_NARRATIVE_ITEMS:
            errors.append(
                self._error(
                    "keyAchievements",
                    "MIN_ACHIEVEMENTS_REQUIRED",
                    "Enter at least three key achievements.",
                )
            )

        next_week_plan_items = self._narrative_items(payload.next_week_focus)
        if len(next_week_plan_items) < MIN_NARRATIVE_ITEMS:
            errors.append(
                self._error(
                    "nextWeekFocus",
                    "MIN_NEXT_WEEK_PLAN_ITEMS_REQUIRED",
                    "Enter at least three next-week plan items.",
                )
            )
        return errors

    def _risk_row_errors(
        self,
        risks: list[RiskInputDTO],
        existing_project_risks: list[ExistingProjectRisk],
    ) -> list[FieldValidationErrorDTO]:
        """Validate WSR risk rows without treating them as a separate risk tracker."""
        errors: list[FieldValidationErrorDTO] = []
        seen_active_descriptions: set[str] = set()
        persisted_risks_by_description = self._active_risks_by_description(
            existing_project_risks
        )
        persisted_risks_by_id = {
            risk.risk_id: risk
            for risk in existing_project_risks
        }
        for index, risk in enumerate(risks):
            field_prefix = f"risks[{index}]"
            source_risk = (
                persisted_risks_by_id.get(risk.source_risk_id)
                if risk.source_risk_id is not None
                else None
            )
            errors.extend(self._risk_transition_errors(field_prefix, risk, source_risk))
            if risk.status in {RiskStatus.OPEN, RiskStatus.IN_PROGRESS}:
                errors.extend(self._active_risk_required_errors(field_prefix, risk))
                normalized_description = risk.description.strip().casefold()
                if normalized_description in seen_active_descriptions:
                    errors.append(
                        self._error(
                            f"{field_prefix}.description",
                            "DUPLICATE_ACTIVE_RISK",
                            "Active risk descriptions must be unique for this WSR.",
                        )
                    )
                matching_persisted_risk_ids = persisted_risks_by_description.get(
                    normalized_description,
                    set(),
                )
                is_known_carry_forward = risk.source_risk_id in matching_persisted_risk_ids
                if matching_persisted_risk_ids and not is_known_carry_forward:
                    errors.append(
                        self._error(
                            f"{field_prefix}.description",
                            "DUPLICATE_ACTIVE_PROJECT_RISK",
                            "An active risk with this description already exists for this project.",
                        )
                    )
                seen_active_descriptions.add(normalized_description)
            if risk.status == RiskStatus.CLOSED and not self._has_text(risk.closure_remark):
                errors.append(
                    self._error(
                        f"{field_prefix}.closureRemark",
                        "CLOSURE_REMARK_REQUIRED",
                        "Closure remark is required when a risk is closed.",
                    )
                )
        return errors

    def _active_risks_by_description(
        self,
        existing_project_risks: list[ExistingProjectRisk],
    ) -> dict[str, set[UUID]]:
        """Group persisted active risks by normalized description for duplicate checks."""
        risks_by_description: dict[str, set[UUID]] = {}
        for risk in existing_project_risks:
            if risk.status not in {RiskStatus.OPEN, RiskStatus.IN_PROGRESS}:
                continue
            normalized_description = risk.description.strip().casefold()
            risks_by_description.setdefault(normalized_description, set()).add(risk.risk_id)
        return risks_by_description

    def _risk_transition_errors(
        self,
        field_prefix: str,
        risk: RiskInputDTO,
        source_risk: ExistingProjectRisk | None,
    ) -> list[FieldValidationErrorDTO]:
        """Return errors for disallowed risk lifecycle transitions."""
        if source_risk is None:
            if risk.status == RiskStatus.CLOSED:
                return [
                    self._error(
                        f"{field_prefix}.status",
                        "NEW_RISK_CANNOT_BE_CLOSED",
                        "A new risk must be Open or In-Progress before it can be closed.",
                    )
                ]
            return []

        if source_risk.status == RiskStatus.OPEN and risk.status == RiskStatus.CLOSED:
            return [
                self._error(
                    f"{field_prefix}.status",
                    "OPEN_RISK_CANNOT_CLOSE_DIRECTLY",
                    "Open risks must move to In-Progress before closure.",
                )
            ]

        if source_risk.status == RiskStatus.CLOSED and risk.status != RiskStatus.CLOSED:
            return [
                self._error(
                    f"{field_prefix}.status",
                    "CLOSED_RISK_CANNOT_REOPEN",
                    "Closed risks cannot be reopened; create a new linked risk if it recurs.",
                )
            ]
        return []

    def _active_risk_required_errors(
        self,
        field_prefix: str,
        risk: RiskInputDTO,
    ) -> list[FieldValidationErrorDTO]:
        """Return missing-field errors for risks that are still active."""
        errors: list[FieldValidationErrorDTO] = []
        required_text_fields = {
            "ownerContact": risk.owner_contact,
            "mitigation": risk.mitigation,
        }
        for field_name, value in required_text_fields.items():
            if not self._has_text(value):
                errors.append(
                    self._error(
                        f"{field_prefix}.{field_name}",
                        "REQUIRED",
                        "This field is required for active risks.",
                    )
                )
        if risk.severity == RiskSeverity.HIGH and risk.planned_closure_date is None:
            errors.append(
                self._error(
                    f"{field_prefix}.plannedClosureDate",
                    "REQUIRED",
                    "High active risks require a planned closure date.",
                )
            )
        return errors

    def _risk_row_warnings(self, risks: list[RiskInputDTO]) -> list[FieldValidationErrorDTO]:
        """Return non-blocking risk warnings that the UI should highlight."""
        warnings: list[FieldValidationErrorDTO] = []
        today = date.today()
        for index, risk in enumerate(risks):
            if (
                risk.status in {RiskStatus.OPEN, RiskStatus.IN_PROGRESS}
                and risk.planned_closure_date is not None
                and risk.planned_closure_date < today
            ):
                warnings.append(
                    self._error(
                        f"risks[{index}].plannedClosureDate",
                        "RISK_OVERDUE",
                        "This risk is past its planned closure date.",
                    )
                )
        return warnings

    def _expected_rag(
        self,
        delivery_model: DeliveryModel,
        calculated_metrics: dict[str, Any],
    ) -> RagStatus:
        """Derive a baseline RAG value from calculated completion percentage."""
        metric_key = "completionPercent"
        if delivery_model == DeliveryModel.PI:
            metric_key = "completionPercent"
        completion_percent = float(calculated_metrics.get(metric_key, 0))
        if completion_percent >= 80:
            return RagStatus.GREEN
        if completion_percent >= 50:
            return RagStatus.AMBER
        return RagStatus.RED

    def _number(self, payload: dict[str, Any], key: str) -> float:
        """Read a numeric field using the same coercion rules as metric calculation."""
        return float(self._metric_calculator.coerce_number(payload.get(key, 0)))

    def _has_text(self, value: Any) -> bool:
        """Return whether a value contains non-whitespace text."""
        return isinstance(value, str) and bool(value.strip())

    def _narrative_items(self, value: Any) -> list[str]:
        """Split PM-entered multiline narrative text into meaningful list items."""
        if not isinstance(value, str):
            return []
        item_candidates = re.split(r"[\n;]+", value)
        return [
            cleaned_item
            for item in item_candidates
            if len(cleaned_item := self._clean_narrative_item(item)) >= MIN_NARRATIVE_ITEM_LENGTH
        ]

    def _clean_narrative_item(self, value: str) -> str:
        """Remove common bullet and numbering prefixes from one narrative item."""
        return re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", value).strip()

    def _error(self, field: str, code: str, message: str) -> FieldValidationErrorDTO:
        """Create a field-level validation error DTO with a stable code."""
        return FieldValidationErrorDTO(field=field, code=code, message=message)
