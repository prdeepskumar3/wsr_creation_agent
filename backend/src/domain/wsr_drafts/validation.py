"""Validation rules for delivery-model-specific WSR draft data."""

from dataclasses import dataclass
from typing import Any

from wsr_shared.dtos import FieldValidationErrorDTO, WsrDraftSaveRequestDTO
from wsr_shared.enums import DeliveryModel, RagStatus

from domain.delivery_models.validation import DeliveryModelPayloadValidator
from domain.wsr_drafts.calculations import DraftMetricCalculator


@dataclass(frozen=True)
class DraftValidationResult:
    """Validation result passed from the domain layer to API/service callers.

    `calculated_metrics` always reflects the backend recalculation for the submitted
    payload, even when validation fails. This lets the UI show current numbers beside
    field-level errors.
    """

    calculated_metrics: dict[str, Any]
    errors: list[FieldValidationErrorDTO]

    @property
    def is_valid(self) -> bool:
        """Return whether the draft is valid for AI generation."""
        return not self.errors


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

    def validate(self, payload: WsrDraftSaveRequestDTO) -> DraftValidationResult:
        """Validate one draft payload and return recalculated metrics plus errors."""
        combined_payload = payload.model_setup | payload.weekly_progress
        calculated_metrics = self._metric_calculator.calculate(
            payload.delivery_model,
            payload.model_setup,
            payload.weekly_progress,
        )
        errors = self._required_field_errors(payload.delivery_model, combined_payload)
        errors.extend(self._cross_field_errors(payload, combined_payload, calculated_metrics))
        errors.extend(self._rag_conflict_errors(payload, combined_payload, calculated_metrics))
        return DraftValidationResult(calculated_metrics=calculated_metrics, errors=errors)

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

    def _error(self, field: str, code: str, message: str) -> FieldValidationErrorDTO:
        """Create a field-level validation error DTO with a stable code."""
        return FieldValidationErrorDTO(field=field, code=code, message=message)
