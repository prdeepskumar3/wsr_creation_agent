"""Delivery-model metric calculations used by draft save and validation flows."""

from typing import Any

from wsr_shared.enums import ConfidenceLevel, DeliveryModel


class DraftMetricCalculator:
    """Calculates backend-owned metrics from PM-entered delivery data.

    The frontend may send form values as numbers or numeric strings. This class is the
    single place that normalizes those values before calculating Sprint and PI metrics.
    """

    def calculate(
        self,
        delivery_model: DeliveryModel,
        model_setup: dict[str, Any],
        weekly_progress: dict[str, Any],
    ) -> dict[str, Any]:
        """Return calculated metrics for the selected delivery model.

        Unknown delivery models return an empty metric set rather than raising here; enum
        validation happens at the API DTO boundary.
        """
        if delivery_model == DeliveryModel.SPRINT:
            return self._calculate_sprint_metrics(model_setup, weekly_progress)
        if delivery_model == DeliveryModel.PI:
            return self._calculate_pi_metrics(model_setup, weekly_progress)
        return {}

    def _calculate_sprint_metrics(
        self,
        model_setup: dict[str, Any],
        weekly_progress: dict[str, Any],
    ) -> dict[str, float]:
        """Calculate Sprint completion, point completion, and effort usage percentages."""
        planned_stories = self._number(model_setup, "plannedStories")
        planned_points = self._number(model_setup, "plannedStoryPoints")
        planned_effort = self._number(model_setup, "plannedEffortHours")

        return {
            "completionPercent": self._percent(
                self._number(weekly_progress, "storiesCompleted"), planned_stories
            ),
            "pointCompletionPercent": self._percent(
                self._number(weekly_progress, "storyPointsCompleted"), planned_points
            ),
            "effortUsagePercent": self._percent(
                self._number(weekly_progress, "effortBurnedHours"), planned_effort
            ),
        }

    def _calculate_pi_metrics(
        self,
        model_setup: dict[str, Any],
        weekly_progress: dict[str, Any],
    ) -> dict[str, float | int | str]:
        """Calculate PI progress, remaining scope, velocity, and confidence."""
        planned_points = self._number(model_setup, "plannedStoryPoints")
        prior_completed = self._number(model_setup, "completedToDateStoryPoints")
        completed_this_week = self._number(weekly_progress, "storyPointsCompletedThisWeek")
        total_sprints = self._number(model_setup, "totalSprints")
        current_sprint = self._number(weekly_progress, "currentSprint")
        if current_sprint == 0:
            current_sprint = self._number(model_setup, "currentSprint")

        completed_to_date = int(prior_completed + completed_this_week)
        remaining_points = max(int(planned_points - completed_to_date), 0)
        remaining_sprints = max(int(total_sprints - current_sprint), 1)
        average_velocity = round(completed_to_date / current_sprint, 2) if current_sprint else 0.0
        required_velocity = round(remaining_points / remaining_sprints, 2)

        return {
            "completedToDateStoryPoints": completed_to_date,
            "completionPercent": self._percent(completed_to_date, planned_points),
            "remainingStoryPoints": remaining_points,
            "requiredVelocity": required_velocity,
            "averageVelocity": average_velocity,
            "confidence": self._confidence(average_velocity, required_velocity).value,
        }

    def _number(self, payload: dict[str, Any], key: str) -> float:
        """Read and normalize a named numeric field from an API payload."""
        return self.coerce_number(payload.get(key, 0))

    def coerce_number(self, value: Any) -> float:
        """Convert UI/API input to a float, defaulting blank or invalid values to zero."""
        if isinstance(value, bool):
            return 0.0
        if isinstance(value, int | float):
            return float(value)
        if isinstance(value, str):
            stripped_value = value.strip()
            if stripped_value:
                try:
                    return float(stripped_value)
                except ValueError:
                    return 0.0
        return 0.0

    def _percent(self, numerator: float, denominator: float) -> float:
        """Return a rounded percentage while protecting against division by zero."""
        if denominator <= 0:
            return 0.0
        return round((numerator / denominator) * 100, 2)

    def _confidence(
        self,
        average_velocity: float,
        required_velocity: float,
    ) -> ConfidenceLevel:
        """Map PI velocity comparison to a simple delivery confidence signal."""
        if required_velocity == 0 or average_velocity >= required_velocity:
            return ConfidenceLevel.HIGH
        if average_velocity >= required_velocity * 0.8:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW
