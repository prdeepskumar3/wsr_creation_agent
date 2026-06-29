from wsr_shared import DeliveryModel

from domain.delivery_models.metadata_registry import DeliveryModelRegistry


class DeliveryModelPayloadValidator:
    """Validates selected delivery-model payloads against registry-required fields."""

    def __init__(self, registry: DeliveryModelRegistry | None = None) -> None:
        self._registry = registry or DeliveryModelRegistry()

    def missing_required_fields(
        self,
        delivery_model: DeliveryModel,
        payload: dict[str, object],
    ) -> set[str]:
        """Return required fields missing for the selected delivery model only."""
        required_keys = self._registry.required_field_keys_for(delivery_model)
        return {key for key in required_keys if payload.get(key) in (None, "")}
