"""LangGraph assembly for WSR generation."""

from datetime import date
from typing import Protocol

from chains.provider_adapter import ProviderRouter
from langgraph.graph import END, START, StateGraph
from nodes.wsr_generation_nodes import (
    DraftLoader,
    checkpoint_state_node,
    draft_customer_sections_node,
    generate_quality_insights_node,
    load_saved_draft_node,
    quality_review_node,
    retrieve_approved_history_node,
    wait_for_pm_review_node,
)
from retrieval.approved_history import ApprovedHistoryRetriever
from state.checkpoint_store import WorkflowCheckpointStore
from state.generation_state import WeeklyStatusReportGenerationState


class RunnableWsrGenerationGraph(Protocol):
    """Compiled graph interface used by tests and callers."""

    def invoke(
        self,
        input: WeeklyStatusReportGenerationState,
    ) -> WeeklyStatusReportGenerationState:
        """Run the graph and return final state."""


def graph_name() -> str:
    """Return the canonical WSR generation graph name."""
    return "weekly_status_report_generation"


def graph_edges() -> list[tuple[str, str]]:
    """Return the named graph edges for architecture traceability."""
    return [
        ("load_saved_draft", "retrieve_approved_history"),
        ("retrieve_approved_history", "generate_quality_insights"),
        ("generate_quality_insights", "draft_customer_sections"),
        ("draft_customer_sections", "quality_review"),
        ("quality_review", "checkpoint_before_human_review"),
        ("checkpoint_before_human_review", "wait_for_pm_review"),
    ]


def build_wsr_generation_graph(
    draft_loader: DraftLoader,
    history_retriever: ApprovedHistoryRetriever,
    provider_router: ProviderRouter,
    checkpoint_store: WorkflowCheckpointStore,
    today: date,
) -> RunnableWsrGenerationGraph:
    """Build the stateful LangGraph workflow for WSR generation."""
    graph = StateGraph(WeeklyStatusReportGenerationState)
    graph.add_node(
        "load_saved_draft",
        lambda state: load_saved_draft_node(state, draft_loader),
    )
    graph.add_node(
        "retrieve_approved_history",
        lambda state: retrieve_approved_history_node(state, history_retriever),
    )
    graph.add_node(
        "generate_quality_insights",
        lambda state: generate_quality_insights_node(state, today),
    )
    graph.add_node(
        "draft_customer_sections",
        lambda state: draft_customer_sections_node(state, provider_router),
    )
    graph.add_node("quality_review", quality_review_node)
    graph.add_node(
        "checkpoint_before_human_review",
        lambda state: checkpoint_state_node(
            state,
            checkpoint_store,
            "before_human_review",
        ),
    )
    graph.add_node("wait_for_pm_review", wait_for_pm_review_node)

    graph.add_edge(START, "load_saved_draft")
    for source, target in graph_edges():
        graph.add_edge(source, target)
    graph.add_edge("wait_for_pm_review", END)
    return graph.compile()
