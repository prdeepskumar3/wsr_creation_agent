from typing import cast

from domain.delivery_models.metadata_registry import DeliveryModelRegistry
from fastapi import APIRouter
from wsr_shared import DeliveryModel, DeliveryModelMetadataDTO

router = APIRouter(prefix="/delivery-models", tags=["delivery-models"])


@router.get("/metadata", response_model=list[DeliveryModelMetadataDTO])
def list_delivery_model_metadata() -> list[DeliveryModelMetadataDTO]:
    """Return field metadata for all enabled MVP delivery models."""
    return cast(list[DeliveryModelMetadataDTO], DeliveryModelRegistry().list_metadata())


@router.get("/{delivery_model}/metadata", response_model=DeliveryModelMetadataDTO)
def get_delivery_model_metadata(delivery_model: DeliveryModel) -> DeliveryModelMetadataDTO:
    """Return field metadata for one enabled delivery model."""
    return DeliveryModelRegistry().get_metadata(delivery_model)
