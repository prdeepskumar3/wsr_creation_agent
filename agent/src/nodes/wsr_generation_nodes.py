"""Named LangGraph node functions for WSR generation."""

import json
from datetime import date
from typing import Protocol

from chains.provider_adapter import ProviderRouter
from evaluators.insight_signals import generate_quality_insights
from retrieval.approved_history import ApprovedHistoryRetriever
from state.checkpoint_store import WorkflowCheckpointStore
from state.generation_state import WeeklyStatusReportGenerationState


class DraftLoader(Protocol):
    """Loads persisted draft data by WSR ID."""

    def load(self, wsr_id: str) -> dict[str, object]:
        """Return a saved draft snapshot."""


class DictDraftLoader:
    """Draft loader backed by an in-memory dictionary for tests/local runs."""

    def __init__(self, drafts: dict[str, dict[str, object]]) -> None:
        """Create a loader over saved draft snapshots."""
        self._drafts = drafts

    def load(self, wsr_id: str) -> dict[str, object]:
        """Return the requested draft snapshot."""
        return self._drafts[wsr_id]


def load_saved_draft_node(
    state: WeeklyStatusReportGenerationState,
    draft_loader: DraftLoader,
) -> WeeklyStatusReportGenerationState:
    """Load persisted draft by `wsr_id`; browser state is never trusted."""
    return {**state, "draft": draft_loader.load(state["wsr_id"])}


def retrieve_approved_history_node(
    state: WeeklyStatusReportGenerationState,
    retriever: ApprovedHistoryRetriever,
) -> WeeklyStatusReportGenerationState:
    """Retrieve account/project approved history and store source IDs."""
    history, source_ids = retriever.retrieve(state["account_id"], state["project_id"])
    return {**state, "retrieved_history": history, "retrieved_source_ids": source_ids}


def generate_quality_insights_node(
    state: WeeklyStatusReportGenerationState,
    today: date,
) -> WeeklyStatusReportGenerationState:
    """Generate deterministic PM-only insight signals from draft facts."""
    insights = generate_quality_insights(state["draft"], today)
    return {**state, "insights": insights}


def draft_customer_sections_node(
    state: WeeklyStatusReportGenerationState,
    provider_router: ProviderRouter,
) -> WeeklyStatusReportGenerationState:
    """Generate customer-facing draft sections through provider-neutral adapter."""
    prompt = _customer_draft_prompt(state)
    result = provider_router.invoke_with_fallback(prompt)
    return {
        **state,
        "draft_sections": _customer_ready_sections(state, result.text),
        "provider_metadata": result.metadata,
    }


def quality_review_node(
    state: WeeklyStatusReportGenerationState,
) -> WeeklyStatusReportGenerationState:
    """Produce a lightweight quality review summary for HITL display."""
    return {
        **state,
        "quality_review": {
            "insightCount": len(state.get("insights", [])),
            "customerDraftReady": bool(state.get("draft_sections")),
        },
    }


def checkpoint_state_node(
    state: WeeklyStatusReportGenerationState,
    checkpoint_store: WorkflowCheckpointStore,
    checkpoint_name: str,
) -> WeeklyStatusReportGenerationState:
    """Persist state by workflow run ID for resumable execution."""
    next_state: WeeklyStatusReportGenerationState = {**state, "checkpoint_name": checkpoint_name}
    checkpoint_store.save(state["workflow_run_id"], dict(next_state))
    return next_state


def wait_for_pm_review_node(
    state: WeeklyStatusReportGenerationState,
) -> WeeklyStatusReportGenerationState:
    """Mark graph state as waiting for human-in-the-loop PM review."""
    return {**state, "human_review_required": True}


def _customer_draft_prompt(state: WeeklyStatusReportGenerationState) -> str:
    """Build the grounded prompt sent to the configured provider."""
    prompt_payload = {
        "draft": state.get("draft", {}),
        "approvedHistory": state.get("retrieved_history", []),
        "pmOnlyInsights": state.get("insights", []),
    }
    return (
        "Create customer-ready weekly status report sections from this JSON. "
        "Use stakeholder-safe wording and do not expose internal-only insight labels.\n"
        f"{json.dumps(prompt_payload, sort_keys=True)}"
    )


def _customer_ready_sections(
    state: WeeklyStatusReportGenerationState,
    provider_text: str,
) -> dict[str, object]:
    """Compose all customer-facing draft sections from saved draft facts."""
    draft = state.get("draft", {})
    weekly_progress = _dict_value(draft, "weeklyProgress")
    entered_data = _dict_value(draft, "enteredData")
    risks = draft.get("risks", [])
    risk_summary = _summarize_risks(risks if isinstance(risks, list) else [])

    return {
        "executiveSummary": _first_non_empty(
            provider_text,
            entered_data.get("overview"),
            weekly_progress.get("progressUpdate"),
        ),
        "deliveryProgress": _first_non_empty(
            weekly_progress.get("progressUpdate"),
            "Delivery progress is captured in the submitted weekly data.",
        ),
        "keyAchievements": _first_non_empty(
            entered_data.get("keyAchievements"),
            "Key achievements are captured in the submitted weekly data.",
        ),
        "risksAndDependenciesSummary": risk_summary,
        "nextWeekFocusAndActions": _first_non_empty(
            entered_data.get("nextWeekFocus"),
            weekly_progress.get("nextWeekPlan"),
            "Next week focus is captured in the submitted weekly data.",
        ),
        "customerFacingRemarks": _first_non_empty(entered_data.get("remarks"), ""),
    }


def _dict_value(source: dict[str, object], key: str) -> dict[str, object]:
    """Return a nested dictionary value without coercing invalid data."""
    value = source.get(key)
    return value if isinstance(value, dict) else {}


def _first_non_empty(*values: object) -> str:
    """Return the first non-empty string value."""
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _summarize_risks(risks: list[object]) -> str:
    """Create a concise customer-safe risk/dependency summary."""
    if not risks:
        return "No active risks or dependencies were reported for this period."
    summaries: list[str] = []
    for risk in risks:
        if not isinstance(risk, dict):
            continue
        description = _first_non_empty(risk.get("description"), "Risk/dependency")
        mitigation = _first_non_empty(risk.get("mitigation"), "Mitigation is being tracked.")
        summaries.append(f"{description}: {mitigation}")
    return " ".join(summaries)
