"""State contract passed between WSR LangGraph nodes."""

from typing import Any, TypedDict


class WeeklyStatusReportGenerationState(TypedDict, total=False):
    """State keys owned by the WSR generation graph.

    Each node writes explicit keys so checkpoint payloads stay understandable and
    resumable by `workflow_run_id`.
    """

    workflow_run_id: str
    wsr_id: str
    account_id: str
    project_id: str
    requested_by: str
    correlation_id: str
    draft: dict[str, Any]
    retrieved_history: list[dict[str, Any]]
    retrieved_source_ids: list[str]
    insights: list[dict[str, Any]]
    draft_sections: dict[str, Any]
    quality_review: dict[str, Any]
    provider_metadata: dict[str, Any]
    checkpoint_name: str
    human_review_required: bool
