from enum import StrEnum


class DeliveryModel(StrEnum):
    """MVP delivery models supported by WSR creation."""

    SPRINT = "SPRINT"
    PI = "PI"


class RagStatus(StrEnum):
    """Customer-facing delivery health selected by the PM."""

    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"


class RiskStatus(StrEnum):
    """Risk state inside WSR preparation."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"


class RiskSeverity(StrEnum):
    """Risk severity selected by the PM."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ConfidenceLevel(StrEnum):
    """Calculated confidence signal for delivery completion."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class FieldInputType(StrEnum):
    """Frontend control type for delivery-model metadata fields."""

    TEXT = "TEXT"
    TEXTAREA = "TEXTAREA"
    NUMBER = "NUMBER"
    DATE = "DATE"
    SELECT = "SELECT"
    READONLY_METRIC = "READONLY_METRIC"


class DeliveryModelSection(StrEnum):
    """Logical form section for delivery-model-specific fields."""

    SETUP = "SETUP"
    WEEKLY_PROGRESS = "WEEKLY_PROGRESS"
    CALCULATED_METRICS = "CALCULATED_METRICS"


class WsrReviewDecision(StrEnum):
    """PM decision after reviewing the ready-to-share WSR preview."""

    SAVE_WSR_PREVIEW = "SAVE_WSR_PREVIEW"
    SUBMIT_FOR_APPROVAL = "SUBMIT_FOR_APPROVAL"
