from uuid import UUID

import pytest
from pydantic import ValidationError
from wsr_shared import (
    DeliveryModel,
    DeliveryModelFieldMetadataDTO,
    DeliveryModelMetadataDTO,
    DeliveryModelSection,
    FieldInputType,
    RagStatus,
    ReadyToShareMetricSummaryDTO,
    ReadyToShareReportMetadataDTO,
    ReadyToShareWsrContentSectionsDTO,
    WsrApprovalDecision,
    WsrApprovalRequestDTO,
    WsrApprovalResponseDTO,
    WsrExportRequestDTO,
    WsrExportResponseDTO,
    WsrExportStatus,
    WsrLifecycleStatus,
    WsrReviewDecision,
    WsrReviewRequestDTO,
    WsrReviewResponseDTO,
)


def build_ready_to_share_content() -> ReadyToShareWsrContentSectionsDTO:
    return ReadyToShareWsrContentSectionsDTO(
        schema_version="1.0.0",
        report_metadata=ReadyToShareReportMetadataDTO(
            account_name="TechCorp Inc.",
            project_name="TechCorp Portal Revamp",
            reporting_period="Jun 23 - Jun 27, 2025",
            prepared_by_name="Arjun Kapoor",
            delivery_model=DeliveryModel.SPRINT,
            rag_status=RagStatus.AMBER,
        ),
        metric_summary=ReadyToShareMetricSummaryDTO(
            story_completion_percent=67,
            story_point_completion_percent=69,
            effort_usage_percent=85,
            open_high_risk_count=1,
        ),
        executive_summary=(
            "Authentication module completed while API integration dependency remains controlled."
        ),
        delivery_progress=(
            "Current completion is tracking below plan because vendor clarification is pending."
        ),
        key_achievements="Completed authentication module and created the API test interface.",
        risks_and_dependencies_summary=(
            "API documentation dependency is being mitigated through parallel testing."
        ),
        next_week_focus_and_actions=(
            "Complete integration validation and publish stakeholder review outcome."
        ),
    )


def test_dto_camel_case_serialization() -> None:
    request = WsrReviewRequestDTO(
        content_sections=build_ready_to_share_content(),
        decision=WsrReviewDecision.SUBMIT_FOR_APPROVAL,
        review_note="Ready for approval.",
    )

    payload = request.model_dump(mode="json", by_alias=True)

    assert "contentSections" in payload
    assert "content_sections" not in payload
    assert payload["contentSections"]["schemaVersion"] == "1.0.0"
    assert "pmQualityInsights" not in payload["contentSections"]


def test_delivery_model_enum_exposes_only_mvp_values() -> None:
    assert [model.value for model in DeliveryModel] == ["SPRINT", "PI"]

    with pytest.raises(ValueError):
        DeliveryModel("KANBAN")


def test_ready_to_share_wsr_content_schema_validation() -> None:
    content = build_ready_to_share_content()

    assert content.report_metadata.delivery_model is DeliveryModel.SPRINT
    assert content.metric_summary.open_high_risk_count == 1


def test_wsr_review_request_rejects_missing_required_content_sections() -> None:
    with pytest.raises(ValidationError, match="contentSections"):
        WsrReviewRequestDTO.model_validate(
            {
                "decision": "SAVE_WSR_PREVIEW",
                "reviewNote": "Missing content should fail.",
            }
        )


def test_delivery_model_metadata_dto_shape() -> None:
    metadata = DeliveryModelMetadataDTO(
        delivery_model=DeliveryModel.SPRINT,
        metadata_version="1.0.0",
        fields=[
            DeliveryModelFieldMetadataDTO(
                key="plannedStoryPoints",
                label="Planned Story Points",
                input_type=FieldInputType.NUMBER,
                section=DeliveryModelSection.SETUP,
                required=True,
                formula_key=None,
            )
        ],
    )

    payload = metadata.model_dump(mode="json", by_alias=True)

    assert payload["deliveryModel"] == "SPRINT"
    assert payload["fields"][0]["inputType"] == "NUMBER"
    assert payload["fields"][0]["section"] == "SETUP"


def test_wsr_review_response_serializes_uuid_aliases() -> None:
    response = WsrReviewResponseDTO(
        wsr_id=UUID("11111111-1111-1111-1111-111111111111"),
        content_version_id=UUID("22222222-2222-2222-2222-222222222222"),
        generation_status="HUMAN_REVIEWED",
        lifecycle_status="IN_REVIEW",
    )

    payload = response.model_dump(mode="json", by_alias=True)

    assert payload["wsrId"] == "11111111-1111-1111-1111-111111111111"
    assert payload["contentVersionId"] == "22222222-2222-2222-2222-222222222222"


def test_wsr_approval_contract_serializes_uuid_aliases() -> None:
    request = WsrApprovalRequestDTO(
        content_version_id=UUID("22222222-2222-2222-2222-222222222222"),
        decision=WsrApprovalDecision.APPROVE,
        approval_note="Approved for customer sharing.",
    )
    response = WsrApprovalResponseDTO(
        wsr_id=UUID("11111111-1111-1111-1111-111111111111"),
        content_version_id=UUID("22222222-2222-2222-2222-222222222222"),
        approval_event_id=UUID("33333333-3333-3333-3333-333333333333"),
        lifecycle_status=WsrLifecycleStatus.APPROVED,
        content_version_status=WsrLifecycleStatus.APPROVED,
    )

    request_payload = request.model_dump(mode="json", by_alias=True)
    response_payload = response.model_dump(mode="json", by_alias=True)

    assert request_payload["contentVersionId"] == "22222222-2222-2222-2222-222222222222"
    assert request_payload["decision"] == "APPROVE"
    assert response_payload["approvalEventId"] == "33333333-3333-3333-3333-333333333333"


def test_wsr_export_contract_serializes_status_metadata() -> None:
    request = WsrExportRequestDTO(
        content_version_id=UUID("22222222-2222-2222-2222-222222222222")
    )
    response = WsrExportResponseDTO(
        export_attempt_id=UUID("44444444-4444-4444-4444-444444444444"),
        wsr_id=UUID("11111111-1111-1111-1111-111111111111"),
        content_version_id=UUID("22222222-2222-2222-2222-222222222222"),
        status=WsrExportStatus.QUEUED,
        object_key="exports/report.pptx",
        error_code=None,
    )

    request_payload = request.model_dump(mode="json", by_alias=True)
    response_payload = response.model_dump(mode="json", by_alias=True)

    assert request_payload["contentVersionId"] == "22222222-2222-2222-2222-222222222222"
    assert response_payload["exportAttemptId"] == "44444444-4444-4444-4444-444444444444"
    assert response_payload["status"] == "QUEUED"
