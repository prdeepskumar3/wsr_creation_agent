from chains.provider_adapter import ProviderPolicy
from graphs.wsr_generation_graph import graph_name


def test_agent_graph_module_imports() -> None:
    assert graph_name() == "weekly_status_report_generation"


def test_provider_policy_defaults_to_stub() -> None:
    policy = ProviderPolicy()

    assert policy.requires_real_credentials is False

