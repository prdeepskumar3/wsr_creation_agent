from datetime import date
from typing import Any
from uuid import UUID

from pydantic import Field

from wsr_shared.api import ApiDTO
from wsr_shared.enums import (
    ConfidenceLevel,
    DeliveryModel,
    DeliveryModelSection,
    FieldInputType,
    RagStatus,
    RiskSeverity,
    RiskStatus,
    WsrApprovalDecision,
    WsrGenerationStatus,
    WsrLifecycleStatus,
    WsrReviewDecision,
)


class DeliveryModelFieldOptionDTO(ApiDTO):
    """Allowed option for a selectable delivery-model field."""

    value: str = Field(..., description="Submitted option value.", examples=["AMBER"])
    label: str = Field(..., description="Human-readable option label.", examples=["Amber"])


class DeliveryModelFieldMetadataDTO(ApiDTO):
    """Metadata that lets the frontend render one delivery-model field."""

    key: str = Field(
        ...,
        description="Stable camelCase field key used by API payloads and frontend forms.",
        examples=["plannedStoryPoints"],
    )
    label: str = Field(
        ..., description="Field label displayed in the WSR form.", examples=["Planned Story Points"]
    )
    input_type: FieldInputType = Field(
        ..., description="Frontend input control type.", examples=[FieldInputType.NUMBER]
    )
    section: DeliveryModelSection = Field(
        ..., description="Delivery-model form section containing this field."
    )
    required: bool = Field(
        ..., description="Whether this field is required when its delivery model is active."
    )
    help_text: str | None = Field(None, description="Short helper text shown near the field.")
    options: list[DeliveryModelFieldOptionDTO] = Field(
        default_factory=list, description="Allowed options for select fields."
    )
    default_value: str | int | float | bool | None = Field(
        None, description="Default value suggested by backend metadata."
    )
    read_only: bool = Field(
        False, description="Whether the frontend should render the field as read-only."
    )
    calculated: bool = Field(False, description="Whether the field is calculated by the backend.")
    formula_key: str | None = Field(
        None, description="Stable formula identifier for calculated fields."
    )
    validation_hints: list[str] = Field(
        default_factory=list, description="Validation hints for frontend UX."
    )
    visible_when: dict[str, str] | None = Field(
        None, description="Optional visibility rule expressed as field-value equality."
    )


class DeliveryModelMetadataDTO(ApiDTO):
    """Versioned delivery-model metadata returned to the frontend."""

    delivery_model: DeliveryModel = Field(
        ..., description="Delivery model described by this metadata."
    )
    metadata_version: str = Field(
        ...,
        description="Version used by frontend caches and schema migrations.",
        examples=["1.0.0"],
    )
    fields: list[DeliveryModelFieldMetadataDTO] = Field(
        ..., description="Ordered field metadata for rendering."
    )


class RiskInputDTO(ApiDTO):
    """Risk/dependency row captured as part of WSR creation."""

    description: str = Field(
        ..., min_length=10, description="Risk or dependency description entered by the PM."
    )
    severity: RiskSeverity = Field(..., description="Risk severity selected by the PM.")
    status: RiskStatus = Field(..., description="Current risk status within this WSR.")
    owner_contact: str = Field(..., description="Owner/contact recorded for accountability.")
    mitigation: str = Field(..., description="Mitigation or next action for the risk.")
    planned_closure_date: date = Field(..., description="Target closure date for the risk.")
    closure_remark: str | None = Field(None, description="Required when risk status is CLOSED.")
    source_risk_id: UUID | None = Field(
        None,
        description="Existing risk row ID when this risk is carried forward from a prior WSR.",
    )


class SprintSetupDTO(ApiDTO):
    """Sprint setup fields entered or prefetched for a Sprint-based WSR."""

    sprint_name: str = Field(
        ..., min_length=1, description="Sprint name or number.", examples=["Sprint 14"]
    )
    start_date: date = Field(..., description="Sprint start date.")
    end_date: date = Field(..., description="Sprint end date.")
    planned_stories: int = Field(
        ..., ge=0, description="Stories planned for the sprint.", examples=[18]
    )
    planned_story_points: int = Field(
        ..., ge=0, description="Story points planned for the sprint.", examples=[70]
    )
    planned_effort_hours: int = Field(
        ..., ge=0, description="Planned sprint effort in hours.", examples=[160]
    )
    dor_percent: int = Field(
        ..., ge=0, le=100, description="Definition-of-ready adherence percentage.", examples=[85]
    )


class SprintWeeklyProgressDTO(ApiDTO):
    """Current-week delivery progress for Sprint-based WSRs."""

    progress_update: str = Field(
        ..., min_length=20, description="PM-entered Sprint progress narrative."
    )
    stories_completed: int = Field(
        ..., ge=0, description="Stories completed during this reporting week."
    )
    story_points_completed: int = Field(
        ..., ge=0, description="Story points completed during this reporting week."
    )
    effort_burned_hours: int = Field(
        ..., ge=0, description="Effort burned during this reporting week."
    )
    unplanned_stories: int = Field(
        ..., ge=0, description="Unplanned stories added during this reporting week."
    )
    unplanned_story_points: int = Field(
        ..., ge=0, description="Unplanned story points added during this reporting week."
    )
    rag_status: RagStatus = Field(..., description="PM-selected customer-facing delivery status.")
    next_week_plan: str = Field(
        ..., min_length=10, description="Planned focus areas for next week."
    )
    remarks: str | None = Field(None, description="Additional stakeholder-safe remarks.")


class CalculatedSprintMetricsDTO(ApiDTO):
    """Backend-calculated Sprint metrics displayed to PM and customer-safe preview."""

    completion_percent: float = Field(
        ..., ge=0, le=100, description="Story-count completion percentage."
    )
    point_completion_percent: float = Field(
        ..., ge=0, le=100, description="Story-point completion percentage."
    )
    effort_usage_percent: float = Field(
        ..., ge=0, description="Effort burned as a percentage of planned effort."
    )


class PiWeeklyProgressDTO(ApiDTO):
    """Current-week delivery progress for PI-based WSRs."""

    current_sprint: int = Field(..., ge=1, description="Current sprint or iteration in the PI.")
    progress_update: str = Field(
        ..., min_length=20, description="PM-entered PI progress narrative."
    )
    story_points_completed_this_week: int = Field(
        ..., ge=0, description="Story points completed this week."
    )
    features_completed_this_week: int = Field(
        ..., ge=0, description="Features/objectives completed this week."
    )
    delayed_scope_items: int = Field(
        ..., ge=0, description="Scope items delayed or moved out this week."
    )
    blockers_dependencies_count: int = Field(
        ..., ge=0, description="Current blockers or dependencies count."
    )
    rag_status: RagStatus = Field(..., description="PM-selected customer-facing delivery status.")
    next_week_plan: str = Field(
        ..., min_length=10, description="Planned focus areas for next week."
    )
    remarks: str | None = Field(None, description="Additional stakeholder-safe remarks.")


class CalculatedPiMetricsDTO(ApiDTO):
    """Backend-calculated PI metrics displayed to PM and customer-safe preview."""

    completed_to_date_story_points: int = Field(
        ..., ge=0, description="Prior completed points plus current week points."
    )
    completion_percent: float = Field(..., ge=0, le=100, description="PI completion percentage.")
    remaining_story_points: int = Field(..., ge=0, description="Remaining planned story points.")
    required_velocity: float = Field(
        ..., ge=0, description="Velocity required to finish remaining points."
    )
    average_velocity: float = Field(
        ..., ge=0, description="Average velocity through the current sprint."
    )
    confidence: ConfidenceLevel = Field(
        ..., description="Confidence based on average vs required velocity."
    )


class WsrDraftSaveRequestDTO(ApiDTO):
    """PM-entered WSR draft payload saved before AI generation starts."""

    account_id: UUID = Field(..., description="Account boundary for the WSR draft.")
    project_id: UUID = Field(..., description="Project for the WSR draft.")
    prepared_by: UUID = Field(..., description="PM user creating or updating the draft.")
    reporting_week: date = Field(..., description="Week start date for this WSR.")
    delivery_model: DeliveryModel = Field(..., description="Selected delivery model.")
    model_setup: dict[str, Any] = Field(
        default_factory=dict, description="Delivery-model setup form values."
    )
    weekly_progress: dict[str, Any] = Field(
        default_factory=dict, description="Current-week delivery progress form values."
    )
    risks: list[RiskInputDTO] = Field(
        default_factory=list, description="Risk/dependency rows captured in the WSR."
    )
    overview: str | None = Field(None, description="Optional PM overview/context note.")
    key_achievements: str | None = Field(None, description="Optional PM achievements note.")
    next_week_focus: str | None = Field(None, description="Optional next-week focus note.")
    remarks: str | None = Field(None, description="Optional stakeholder-safe remarks.")


class WsrDraftResponseDTO(ApiDTO):
    """Saved WSR draft state returned to restore the full UI form."""

    wsr_id: UUID = Field(..., description="Saved WSR draft identifier.")
    account_id: UUID = Field(..., description="Account boundary for the WSR draft.")
    project_id: UUID = Field(..., description="Project for the WSR draft.")
    prepared_by: UUID = Field(..., description="PM user who owns the draft.")
    reporting_week: date = Field(..., description="Week start date for this WSR.")
    delivery_model: DeliveryModel = Field(..., description="Selected delivery model.")
    lifecycle_status: WsrLifecycleStatus = Field(..., description="Current report lifecycle state.")
    generation_status: WsrGenerationStatus = Field(
        ..., description="AI generation state; draft save keeps this NOT_STARTED."
    )
    schema_version: str = Field(..., description="Draft schema version.")
    version_number: int = Field(..., ge=1, description="Draft version number.")
    entered_data_snapshot: dict[str, Any] = Field(
        default_factory=dict, description="Full UI snapshot for form restore."
    )
    model_setup_snapshot: dict[str, Any] = Field(
        default_factory=dict, description="Delivery-model setup snapshot."
    )
    weekly_progress_snapshot: dict[str, Any] = Field(
        default_factory=dict, description="Weekly progress snapshot."
    )
    calculated_metrics_snapshot: dict[str, Any] = Field(
        default_factory=dict, description="Backend-calculated metrics snapshot."
    )
    risks: list[RiskInputDTO] = Field(
        default_factory=list, description="Risk/dependency rows restored into the UI."
    )


class FieldValidationErrorDTO(ApiDTO):
    """Field-level validation issue returned for WSR draft data."""

    field: str = Field(..., description="CamelCase field path that failed validation.")
    code: str = Field(..., description="Stable validation error code.")
    message: str = Field(..., description="PM-friendly validation message.")


class WsrDraftValidationResponseDTO(ApiDTO):
    """Validation result for PM-entered WSR draft data."""

    is_valid: bool = Field(..., description="Whether draft data can proceed to generation.")
    calculated_metrics: dict[str, Any] = Field(
        default_factory=dict,
        description="Backend recalculated metrics used during validation.",
    )
    errors: list[FieldValidationErrorDTO] = Field(
        default_factory=list,
        description="Field-level validation errors.",
    )
    warnings: list[FieldValidationErrorDTO] = Field(
        default_factory=list,
        description="Non-blocking field-level warnings used for UI highlights.",
    )


class WsrPrefillResponseDTO(ApiDTO):
    """Reusable WSR data copied from the latest approved report."""

    has_approved_history: bool = Field(
        ..., description="Whether a prior approved WSR was found for account/project."
    )
    source_wsr_id: UUID | None = Field(
        None, description="Approved WSR used as the prefill source."
    )
    delivery_model: DeliveryModel | None = Field(
        None, description="Delivery model from the source WSR."
    )
    model_setup: dict[str, Any] = Field(
        default_factory=dict,
        description="Reusable delivery-model setup values.",
    )
    previous_customer_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Customer-facing context safe to show in the next WSR.",
    )
    prior_pi_completed_story_points: int | None = Field(
        None,
        description="Prior completed PI points copied for PI-based projects.",
    )
    carry_forward_risks: list[RiskInputDTO] = Field(
        default_factory=list,
        description="Active risks copied from the latest approved WSR.",
    )
    read_only_fields: list[str] = Field(
        default_factory=list,
        description="Prefill response fields that should be rendered as read-only context.",
    )


class ReadyToShareReportMetadataDTO(ApiDTO):
    """Header metadata displayed in the customer-ready WSR."""

    account_name: str = Field(
        ..., description="Customer/account name displayed in the WSR.", examples=["TechCorp Inc."]
    )
    project_name: str = Field(
        ..., description="Project name displayed in the WSR.", examples=["TechCorp Portal Revamp"]
    )
    reporting_period: str = Field(
        ..., description="Human-readable reporting period.", examples=["Jun 23 - Jun 27, 2025"]
    )
    prepared_by_name: str = Field(
        ..., description="Display name of the PM preparing the WSR.", examples=["Arjun Kapoor"]
    )
    delivery_model: DeliveryModel = Field(..., description="Delivery model used for this WSR.")
    rag_status: RagStatus = Field(..., description="Customer-facing RAG status.")


class ReadyToShareMetricSummaryDTO(ApiDTO):
    """Customer-safe metric summary shown in the ready-to-share WSR."""

    story_completion_percent: float | None = Field(
        None, ge=0, le=100, description="Sprint story-count completion percentage."
    )
    story_point_completion_percent: float | None = Field(
        None, ge=0, le=100, description="Sprint point completion percentage."
    )
    effort_usage_percent: float | None = Field(
        None, ge=0, description="Sprint effort usage percentage."
    )
    pi_completion_percent: float | None = Field(
        None, ge=0, le=100, description="PI completion percentage."
    )
    open_high_risk_count: int = Field(
        ..., ge=0, description="Open high-severity risks included in the WSR summary."
    )


class ReadyToShareWsrContentSectionsDTO(ApiDTO):
    """Editable customer-facing WSR content reviewed before approval/export."""

    schema_version: str = Field(
        ..., description="Content schema version for approval/export.", examples=["1.0.0"]
    )
    report_metadata: ReadyToShareReportMetadataDTO = Field(
        ..., description="Display metadata for the report header."
    )
    metric_summary: ReadyToShareMetricSummaryDTO = Field(
        ..., description="Customer-safe summary metrics."
    )
    executive_summary: str = Field(
        ..., min_length=20, description="Customer-facing executive summary."
    )
    delivery_progress: str = Field(
        ..., min_length=20, description="Customer-facing delivery progress narrative."
    )
    key_achievements: str = Field(..., min_length=10, description="Customer-facing achievements.")
    risks_and_dependencies_summary: str = Field(
        ..., min_length=10, description="Customer-facing risk/dependency summary."
    )
    next_week_focus_and_actions: str = Field(
        ..., min_length=10, description="Customer-facing next week focus narrative."
    )
    customer_facing_remarks: str | None = Field(
        None, description="Optional customer-facing remarks."
    )


class WsrReviewRequestDTO(ApiDTO):
    """PM request to save or submit the edited ready-to-share WSR preview."""

    content_sections: ReadyToShareWsrContentSectionsDTO = Field(
        ..., description="PM-edited ready-to-share WSR content."
    )
    review_note: str | None = Field(
        None, description="Optional internal PM note for the review event."
    )
    decision: WsrReviewDecision = Field(
        ..., description="Whether to save preview or submit for approval."
    )


class WsrReviewResponseDTO(ApiDTO):
    """Response returned after WSR preview review is persisted."""

    wsr_id: UUID = Field(..., description="WSR ID associated with this review.")
    content_version_id: UUID = Field(
        ..., description="Persisted WSR content version created from the review."
    )
    generation_status: str = Field(
        ..., description="Generation workflow status after review persistence."
    )
    lifecycle_status: str = Field(..., description="WSR lifecycle status after review persistence.")


class WsrApprovalRequestDTO(ApiDTO):
    """PM request to approve one reviewed customer-facing content version."""

    content_version_id: UUID = Field(
        ..., description="Reviewed content version selected for formal approval."
    )
    decision: WsrApprovalDecision = Field(
        WsrApprovalDecision.APPROVE, description="Formal approval decision."
    )
    approval_note: str | None = Field(
        None, description="Optional PM note stored on the approval event."
    )


class WsrApprovalResponseDTO(ApiDTO):
    """Response returned after a reviewed WSR content version is approved."""

    wsr_id: UUID = Field(..., description="Approved WSR report ID.")
    content_version_id: UUID = Field(..., description="Approved content version ID.")
    approval_event_id: UUID = Field(..., description="Audit event recording the approval.")
    lifecycle_status: WsrLifecycleStatus = Field(..., description="WSR lifecycle after approval.")
    content_version_status: WsrLifecycleStatus = Field(
        ..., description="Approved content version status."
    )
