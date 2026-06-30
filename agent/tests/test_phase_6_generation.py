from datetime import date

import pytest
from chains.provider_adapter import (
    FunctionChatProvider,
    ProviderInvocationError,
    ProviderPolicy,
    ProviderRouter,
)
from evaluators.insight_signals import generate_quality_insights
from graphs.wsr_generation_graph import build_wsr_generation_graph, graph_edges
from nodes.wsr_generation_nodes import DictDraftLoader
from retrieval.approved_history import ApprovedHistoryRecord, ApprovedHistoryRetriever
from state.checkpoint_store import InMemoryWorkflowCheckpointStore


def test_graph_edges_are_named_for_phase_6_traceability() -> None:
    assert graph_edges() == [
        ("load_saved_draft", "retrieve_approved_history"),
        ("retrieve_approved_history", "generate_quality_insights"),
        ("generate_quality_insights", "draft_customer_sections"),
        ("draft_customer_sections", "quality_review"),
        ("quality_review", "checkpoint_before_human_review"),
        ("checkpoint_before_human_review", "wait_for_pm_review"),
    ]


def test_approved_history_retrieval_filters_account_project_and_pm_only_fields() -> None:
    retriever = ApprovedHistoryRetriever(
        [
            ApprovedHistoryRecord(
                source_id="wsr-1",
                account_id="account-1",
                project_id="project-1",
                lifecycle_status="APPROVED",
                content_sections={
                    "executiveSummary": "Approved summary.",
                    "pmQualityInsights": "Never retrieve this.",
                },
            ),
            ApprovedHistoryRecord(
                source_id="wsr-2",
                account_id="account-1",
                project_id="project-2",
                lifecycle_status="APPROVED",
                content_sections={"executiveSummary": "Wrong project."},
            ),
            ApprovedHistoryRecord(
                source_id="wsr-3",
                account_id="account-1",
                project_id="project-1",
                lifecycle_status="REJECTED",
                content_sections={"executiveSummary": "Rejected draft."},
            ),
        ]
    )

    history, source_ids = retriever.retrieve("account-1", "project-1")

    assert history == [{"executiveSummary": "Approved summary."}]
    assert source_ids == ["wsr-1"]


def test_provider_router_falls_back_from_grok_to_deepseek_on_retryable_failure() -> None:
    router = ProviderRouter(
        providers={
            "grok": FunctionChatProvider("grok", lambda _prompt, _model: "", retryable_error=True),
            "deepseek": FunctionChatProvider(
                "deepseek",
                lambda _prompt, model: f"{model}: fallback draft",
            ),
        },
        policy=ProviderPolicy(
            primary_provider="grok",
            fallback_provider="deepseek",
            primary_model_id="grok-4",
            fallback_model_id="deepseek-chat",
        ),
    )

    result = router.invoke_with_fallback("draft")

    assert result.provider == "deepseek"
    assert result.model_id == "deepseek-chat"
    assert "fallback draft" in result.text


def test_provider_router_does_not_fallback_on_non_retryable_error() -> None:
    router = ProviderRouter(
        providers={
            "grok": FunctionChatProvider("grok", lambda _prompt, _model: "", retryable_error=False),
            "deepseek": FunctionChatProvider("deepseek", lambda _prompt, _model: "unused"),
        },
        policy=ProviderPolicy(primary_provider="grok", fallback_provider="deepseek"),
    )

    with pytest.raises(ProviderInvocationError):
        router.invoke_with_fallback("draft")


def test_provider_router_normalizes_missing_provider_configuration() -> None:
    router = ProviderRouter(
        providers={},
        policy=ProviderPolicy(primary_provider="grok", fallback_provider=None),
    )

    with pytest.raises(ProviderInvocationError) as exc_info:
        router.invoke_with_fallback("draft")

    assert exc_info.value.retryable is False
    assert "grok" in str(exc_info.value)


def test_quality_insights_include_required_schema_and_discrepancy_signals() -> None:
    insights = generate_quality_insights(
        {
            "modelSetup": {"plannedStoryPoints": 100},
            "weeklyProgress": {
                "ragStatus": "GREEN",
                "unplannedStoryPoints": 25,
                "progressUpdate": "Done.",
            },
            "calculatedMetrics": {"completionPercent": 60},
            "enteredData": {
                "keyAchievements": "Completed authentication module",
                "nextWeekFocus": "Complete integration validation",
                "remarks": "Internal workaround is active.",
            },
            "risks": [
                {
                    "description": "Vendor API dependency.",
                    "severity": "HIGH",
                    "status": "IN_PROGRESS",
                    "mitigation": "TBD",
                    "plannedClosureDate": "2025-06-20",
                }
            ],
        },
        today=date(2025, 6, 30),
    )

    insight_types = {insight["type"] for insight in insights}
    assert {"DISCREPANCY", "RISK", "QUALITY", "CUSTOMER_SAFETY"} <= insight_types
    required_keys = {
        "type",
        "severity",
        "description",
        "evidence",
        "recommendation",
        "suggestedEdit",
    }
    for insight in insights:
        assert required_keys <= set(insight)


def test_langgraph_execution_checkpoints_state_by_workflow_run_id() -> None:
    checkpoint_store = InMemoryWorkflowCheckpointStore()
    graph = build_wsr_generation_graph(
        draft_loader=DictDraftLoader(
            {
                "wsr-1": {
                    "modelSetup": {},
                    "weeklyProgress": {"ragStatus": "AMBER", "progressUpdate": "Progress update."},
                    "calculatedMetrics": {},
                    "enteredData": {},
                    "risks": [],
                }
            }
        ),
        history_retriever=ApprovedHistoryRetriever([]),
        provider_router=ProviderRouter(
            providers={"grok": FunctionChatProvider("grok", lambda _prompt, model: model)},
            policy=ProviderPolicy(primary_provider="grok", fallback_provider=None),
        ),
        checkpoint_store=checkpoint_store,
        today=date(2025, 6, 30),
    )

    final_state = graph.invoke(
        {
            "workflow_run_id": "run-1",
            "wsr_id": "wsr-1",
            "account_id": "account-1",
            "project_id": "project-1",
            "requested_by": "pm-1",
            "correlation_id": "corr-1",
        }
    )

    checkpoint = checkpoint_store.load("run-1")
    assert final_state["human_review_required"] is True
    assert checkpoint is not None
    assert checkpoint["checkpoint_name"] == "before_human_review"
    assert checkpoint["draft_sections"]["executiveSummary"] == "grok-4"
    assert checkpoint["draft_sections"]["deliveryProgress"] == "Progress update."
    assert "nextWeekFocusAndActions" in checkpoint["draft_sections"]
