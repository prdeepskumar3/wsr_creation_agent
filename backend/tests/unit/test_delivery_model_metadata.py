from api.v1.delivery_models import get_delivery_model_metadata, list_delivery_model_metadata
from app.create_app import create_app
from domain.delivery_models import DeliveryModelPayloadValidator, DeliveryModelRegistry
from domain.delivery_models.metadata_registry import METADATA_VERSION
from wsr_shared import DeliveryModel, DeliveryModelSection


def field_by_key(metadata_key: DeliveryModel, field_key: str):
    metadata = DeliveryModelRegistry().get_metadata(metadata_key)
    return next(field for field in metadata.fields if field.key == field_key)


def test_sprint_metadata_shape() -> None:
    metadata = DeliveryModelRegistry().get_metadata(DeliveryModel.SPRINT)
    field_keys = {field.key for field in metadata.fields}

    assert metadata.delivery_model == DeliveryModel.SPRINT
    assert metadata.metadata_version == METADATA_VERSION
    assert {"sprintName", "plannedStoryPoints", "progressUpdate", "ragStatus"} <= field_keys
    assert any(
        field.section == DeliveryModelSection.CALCULATED_METRICS for field in metadata.fields
    )


def test_pi_metadata_shape() -> None:
    metadata = DeliveryModelRegistry().get_metadata(DeliveryModel.PI)
    field_keys = {field.key for field in metadata.fields}

    assert metadata.delivery_model == DeliveryModel.PI
    assert {"piName", "totalSprints", "currentSprint", "plannedStoryPoints"} <= field_keys
    assert "sprintName" not in field_keys


def test_metadata_api_is_generated_from_registry() -> None:
    from_api = list_delivery_model_metadata()
    from_registry = DeliveryModelRegistry().list_metadata()

    assert from_api == from_registry


def test_single_metadata_api_returns_camel_case_payload() -> None:
    metadata = get_delivery_model_metadata(DeliveryModel.SPRINT)
    payload = metadata.model_dump(mode="json", by_alias=True)

    assert payload["deliveryModel"] == "SPRINT"
    assert payload["metadataVersion"] == METADATA_VERSION
    assert "inputType" in payload["fields"][0]


def test_fastapi_openapi_exposes_metadata_routes() -> None:
    paths = create_app().openapi()["paths"]

    assert "/api/v1/delivery-models/metadata" in paths
    assert "/api/v1/delivery-models/{delivery_model}/metadata" in paths


def test_each_metadata_field_contains_required_ui_attributes() -> None:
    required_keys = {
        "key",
        "label",
        "inputType",
        "section",
        "required",
        "helpText",
        "options",
        "defaultValue",
        "readOnly",
        "calculated",
        "formulaKey",
        "validationHints",
        "visibleWhen",
    }

    for metadata in DeliveryModelRegistry().list_metadata():
        for field in metadata.fields:
            payload = field.model_dump(mode="json", by_alias=True)
            assert required_keys <= payload.keys()


def test_formula_key_mapping_for_sprint_metrics() -> None:
    point_completion = field_by_key(DeliveryModel.SPRINT, "pointCompletionPercent")
    effort_usage = field_by_key(DeliveryModel.SPRINT, "effortUsagePercent")

    assert point_completion.read_only is True
    assert point_completion.calculated is True
    assert point_completion.formula_key == "sprint_point_completion_percent"
    assert effort_usage.formula_key == "sprint_effort_usage_percent"


def test_hidden_non_selected_model_fields_are_not_required() -> None:
    validator = DeliveryModelPayloadValidator()
    payload = {
        "piName": "PI 2025 Q3",
        "piStartDate": "2025-07-01",
        "piEndDate": "2025-09-30",
        "totalSprints": 6,
        "currentSprint": 2,
        "plannedStoryPoints": 280,
        "completedToDateStoryPoints": 90,
        "progressUpdate": "PI objectives are progressing with manageable dependency risk.",
        "storyPointsCompletedThisWeek": 24,
        "featuresCompletedThisWeek": 2,
        "delayedScopeItems": 0,
        "blockersDependenciesCount": 1,
        "ragStatus": "AMBER",
        "nextWeekPlan": "Close dependencies and complete feature validation.",
    }

    missing_fields = validator.missing_required_fields(DeliveryModel.PI, payload)

    assert missing_fields == set()
    assert "sprintName" not in missing_fields
