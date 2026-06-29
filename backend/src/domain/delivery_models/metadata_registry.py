from wsr_shared import (
    DeliveryModel,
    DeliveryModelFieldMetadataDTO,
    DeliveryModelFieldOptionDTO,
    DeliveryModelMetadataDTO,
    DeliveryModelSection,
    FieldInputType,
    RagStatus,
)

METADATA_VERSION = "delivery-models.v1"


class DeliveryModelRegistry:
    """Registry that owns delivery-model field metadata for UI and validation."""

    def list_metadata(self) -> list[DeliveryModelMetadataDTO]:
        """Return metadata for all enabled MVP delivery models."""
        return [self.get_metadata(DeliveryModel.SPRINT), self.get_metadata(DeliveryModel.PI)]

    def get_metadata(self, delivery_model: DeliveryModel) -> DeliveryModelMetadataDTO:
        """Return metadata for one delivery model."""
        fields_by_model = {
            DeliveryModel.SPRINT: self._sprint_fields,
            DeliveryModel.PI: self._pi_fields,
        }
        return DeliveryModelMetadataDTO(
            delivery_model=delivery_model,
            metadata_version=METADATA_VERSION,
            fields=fields_by_model[delivery_model](),
        )

    def required_field_keys_for(self, delivery_model: DeliveryModel) -> set[str]:
        """Return required keys for the selected model only."""
        return {
            field.key
            for field in self.get_metadata(delivery_model).fields
            if field.required and not field.read_only
        }

    def _sprint_fields(self) -> list[DeliveryModelFieldMetadataDTO]:
        rag_options = self._rag_status_options()
        return [
            self._field("sprintName", "Sprint name / number", FieldInputType.TEXT),
            self._field("startDate", "Start date", FieldInputType.DATE),
            self._field("endDate", "End date", FieldInputType.DATE),
            self._field("plannedStories", "Planned stories", FieldInputType.NUMBER),
            self._field("plannedStoryPoints", "Planned story points", FieldInputType.NUMBER),
            self._field("plannedEffortHours", "Planned sprint effort (hrs)", FieldInputType.NUMBER),
            self._field("dorPercent", "DOR %", FieldInputType.NUMBER),
            self._field(
                "progressUpdate",
                "High-level progress update",
                FieldInputType.TEXTAREA,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
                help_text="Customer-safe current week progress narrative.",
                validation_hints=["minLength:20"],
            ),
            self._field(
                "storiesCompleted",
                "Stories completed",
                FieldInputType.NUMBER,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
            ),
            self._field(
                "storyPointsCompleted",
                "Story points completed",
                FieldInputType.NUMBER,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
            ),
            self._field(
                "effortBurnedHours",
                "Effort burned (hrs)",
                FieldInputType.NUMBER,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
            ),
            self._field(
                "unplannedStories",
                "Unplanned stories",
                FieldInputType.NUMBER,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
                required=False,
                default_value=0,
            ),
            self._field(
                "unplannedStoryPoints",
                "Unplanned story points",
                FieldInputType.NUMBER,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
                required=False,
                default_value=0,
            ),
            self._field(
                "ragStatus",
                "Overall RAG status",
                FieldInputType.SELECT,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
                options=rag_options,
            ),
            self._field(
                "nextWeekPlan",
                "Next week plan",
                FieldInputType.TEXTAREA,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
                validation_hints=["minLength:10"],
            ),
            self._field(
                "remarks",
                "Remarks / notes",
                FieldInputType.TEXTAREA,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
                required=False,
            ),
            self._calculated_field(
                "completionPercent", "Story completion %", "sprint_completion_percent"
            ),
            self._calculated_field(
                "pointCompletionPercent",
                "Point completion %",
                "sprint_point_completion_percent",
            ),
            self._calculated_field(
                "effortUsagePercent", "Effort usage %", "sprint_effort_usage_percent"
            ),
        ]

    def _pi_fields(self) -> list[DeliveryModelFieldMetadataDTO]:
        rag_options = self._rag_status_options()
        return [
            self._field("piName", "PI name / number", FieldInputType.TEXT),
            self._field("piStartDate", "PI start date", FieldInputType.DATE),
            self._field("piEndDate", "PI end date", FieldInputType.DATE),
            self._field("totalSprints", "Total sprints in PI", FieldInputType.NUMBER),
            self._field("currentSprint", "Current sprint", FieldInputType.NUMBER),
            self._field("plannedStoryPoints", "Planned PI story points", FieldInputType.NUMBER),
            self._field(
                "completedToDateStoryPoints",
                "Completed story points to date",
                FieldInputType.NUMBER,
            ),
            self._field(
                "progressUpdate",
                "High-level PI progress update",
                FieldInputType.TEXTAREA,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
                help_text="Customer-safe current week PI progress narrative.",
                validation_hints=["minLength:20"],
            ),
            self._field(
                "storyPointsCompletedThisWeek",
                "Story points completed this week",
                FieldInputType.NUMBER,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
            ),
            self._field(
                "featuresCompletedThisWeek",
                "Features completed this week",
                FieldInputType.NUMBER,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
            ),
            self._field(
                "delayedScopeItems",
                "Delayed scope items",
                FieldInputType.NUMBER,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
                default_value=0,
            ),
            self._field(
                "blockersDependenciesCount",
                "Blockers / dependencies",
                FieldInputType.NUMBER,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
                default_value=0,
            ),
            self._field(
                "ragStatus",
                "Overall RAG status",
                FieldInputType.SELECT,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
                options=rag_options,
            ),
            self._field(
                "nextWeekPlan",
                "Next week plan",
                FieldInputType.TEXTAREA,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
                validation_hints=["minLength:10"],
            ),
            self._field(
                "remarks",
                "Remarks / notes",
                FieldInputType.TEXTAREA,
                section=DeliveryModelSection.WEEKLY_PROGRESS,
                required=False,
            ),
            self._calculated_field(
                "piCompletionPercent", "PI completion %", "pi_completion_percent"
            ),
            self._calculated_field(
                "remainingStoryPoints", "Remaining story points", "pi_remaining_points"
            ),
            self._calculated_field("requiredVelocity", "Required velocity", "pi_required_velocity"),
            self._calculated_field("averageVelocity", "Average velocity", "pi_average_velocity"),
        ]

    def _field(
        self,
        key: str,
        label: str,
        input_type: FieldInputType,
        *,
        section: DeliveryModelSection = DeliveryModelSection.SETUP,
        required: bool = True,
        help_text: str | None = None,
        options: list[DeliveryModelFieldOptionDTO] | None = None,
        default_value: str | int | float | bool | None = None,
        validation_hints: list[str] | None = None,
    ) -> DeliveryModelFieldMetadataDTO:
        return DeliveryModelFieldMetadataDTO(
            key=key,
            label=label,
            input_type=input_type,
            section=section,
            required=required,
            help_text=help_text or self._default_help_text(input_type),
            options=options or [],
            default_value=default_value,
            read_only=False,
            calculated=False,
            formula_key=None,
            validation_hints=validation_hints or self._default_validation_hints(input_type),
            visible_when=None,
        )

    def _calculated_field(
        self,
        key: str,
        label: str,
        formula_key: str,
    ) -> DeliveryModelFieldMetadataDTO:
        return DeliveryModelFieldMetadataDTO(
            key=key,
            label=label,
            input_type=FieldInputType.READONLY_METRIC,
            section=DeliveryModelSection.CALCULATED_METRICS,
            required=False,
            help_text="Calculated by the backend from PM-entered delivery metrics.",
            options=[],
            default_value=None,
            read_only=True,
            calculated=True,
            formula_key=formula_key,
            validation_hints=[],
            visible_when=None,
        )

    def _rag_status_options(self) -> list[DeliveryModelFieldOptionDTO]:
        return [
            DeliveryModelFieldOptionDTO(value=status.value, label=status.value.title())
            for status in RagStatus
        ]

    def _default_help_text(self, input_type: FieldInputType) -> str:
        help_text_by_type = {
            FieldInputType.TEXT: "Enter the value used for this delivery model.",
            FieldInputType.TEXTAREA: "Enter customer-safe report narrative.",
            FieldInputType.NUMBER: "Enter a non-negative number.",
            FieldInputType.DATE: "Select the applicable date.",
            FieldInputType.SELECT: "Select one allowed value.",
            FieldInputType.READONLY_METRIC: "Calculated by the backend.",
        }
        return help_text_by_type[input_type]

    def _default_validation_hints(self, input_type: FieldInputType) -> list[str]:
        if input_type == FieldInputType.NUMBER:
            return ["min:0"]
        return []
