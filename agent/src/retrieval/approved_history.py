"""Approved account/project history retrieval for WSR generation."""

from dataclasses import dataclass

CUSTOMER_SAFE_HISTORY_KEYS = {
    "executiveSummary",
    "deliveryProgress",
    "keyAchievements",
    "risksAndDependenciesSummary",
    "nextWeekFocusAndActions",
    "customerFacingRemarks",
}


@dataclass(frozen=True)
class ApprovedHistoryRecord:
    """Approved WSR history record available to retrieval."""

    source_id: str
    account_id: str
    project_id: str
    lifecycle_status: str
    content_sections: dict[str, object]


class ApprovedHistoryRetriever:
    """Retrieves only approved, customer-safe WSR history for one account/project."""

    def __init__(self, records: list[ApprovedHistoryRecord]) -> None:
        """Create a retriever over already-loaded history records."""
        self._records = records

    def retrieve(
        self,
        account_id: str,
        project_id: str,
    ) -> tuple[list[dict[str, object]], list[str]]:
        """Return safe content and source IDs for matching approved records."""
        matching_records = [
            record
            for record in self._records
            if record.account_id == account_id
            and record.project_id == project_id
            and record.lifecycle_status == "APPROVED"
        ]
        return (
            [
                {
                    key: value
                    for key, value in record.content_sections.items()
                    if key in CUSTOMER_SAFE_HISTORY_KEYS
                }
                for record in matching_records
            ],
            [record.source_id for record in matching_records],
        )
