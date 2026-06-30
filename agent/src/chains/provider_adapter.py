"""Provider-neutral LLM adapters for WSR generation."""

import os
from collections.abc import Callable
from dataclasses import dataclass, field


class ProviderInvocationError(Exception):
    """Normalized provider error raised by Grok and DeepSeek adapters."""

    def __init__(self, message: str, retryable: bool) -> None:
        """Create a provider error with retry classification."""
        super().__init__(message)
        self.retryable = retryable


@dataclass(frozen=True)
class ProviderPolicy:
    """Provider policy resolved before model invocation."""

    primary_provider: str = "grok"
    fallback_provider: str | None = "deepseek"
    primary_model_id: str = "grok-4"
    fallback_model_id: str = "deepseek-chat"

    @classmethod
    def from_environment(cls) -> "ProviderPolicy":
        """Resolve provider policy from environment defaults."""
        fallback_provider = os.getenv("WSR_LLM_FALLBACK_PROVIDER", "deepseek")
        return cls(
            primary_provider=os.getenv("WSR_LLM_PRIMARY_PROVIDER", "grok"),
            fallback_provider=fallback_provider or None,
            primary_model_id=os.getenv("WSR_LLM_PRIMARY_MODEL", "grok-4"),
            fallback_model_id=os.getenv("WSR_LLM_FALLBACK_MODEL", "deepseek-chat"),
        )

    @property
    def requires_real_credentials(self) -> bool:
        """Return whether this policy needs real provider credentials."""
        return self.primary_provider != "stub"


@dataclass
class ProviderCallResult:
    """Provider-neutral response returned to graph nodes."""

    text: str
    provider: str
    model_id: str
    metadata: dict[str, object] = field(default_factory=dict)


class ChatProvider:
    """Provider-neutral interface used by graph nodes."""

    provider_name: str

    def invoke(self, prompt: str, model_id: str) -> ProviderCallResult:
        """Return a provider response for a prompt."""
        raise NotImplementedError


class FunctionChatProvider(ChatProvider):
    """Test-friendly provider backed by a Python callable."""

    def __init__(
        self,
        provider_name: str,
        responder: Callable[[str, str], str],
        retryable_error: bool | None = None,
    ) -> None:
        """Create a deterministic provider for tests/local runs."""
        self.provider_name = provider_name
        self._responder = responder
        self._retryable_error = retryable_error

    def invoke(self, prompt: str, model_id: str) -> ProviderCallResult:
        """Return callable output or raise a normalized provider error."""
        if self._retryable_error is not None:
            raise ProviderInvocationError(
                f"{self.provider_name} failed",
                retryable=self._retryable_error,
            )
        return ProviderCallResult(
            text=self._responder(prompt, model_id),
            provider=self.provider_name,
            model_id=model_id,
            metadata={"provider": self.provider_name, "modelId": model_id},
        )


class LangChainChatProvider(ChatProvider):
    """LangChain-backed chat provider used for real model calls."""

    def __init__(
        self,
        provider_name: str,
        model_provider: str,
        api_key_env_name: str,
        api_key: str | None = None,
    ) -> None:
        """Create a provider adapter without storing secrets in metadata."""
        self.provider_name = provider_name
        self._model_provider = model_provider
        if api_key:
            os.environ[api_key_env_name] = api_key

    def invoke(self, prompt: str, model_id: str) -> ProviderCallResult:
        """Invoke the configured model through LangChain."""
        try:
            from langchain.chat_models import init_chat_model
            from langchain_core.messages import HumanMessage

            model = init_chat_model(model_id, model_provider=self._model_provider)
            response = model.invoke([HumanMessage(content=prompt)])
        except Exception as exc:
            raise ProviderInvocationError(str(exc), retryable=True) from exc

        text = getattr(response, "content", response)
        return ProviderCallResult(
            text=str(text),
            provider=self.provider_name,
            model_id=model_id,
            metadata={"provider": self.provider_name, "modelId": model_id},
        )


class GrokProvider(LangChainChatProvider):
    """Grok provider adapter using LangChain 1.x chat model initialization."""

    def __init__(self, api_key: str | None = None) -> None:
        """Create a Grok adapter using XAI-compatible credentials."""
        super().__init__("grok", "xai", "XAI_API_KEY", api_key)


class DeepSeekProvider(LangChainChatProvider):
    """DeepSeek provider adapter using LangChain 1.x chat model initialization."""

    def __init__(self, api_key: str | None = None) -> None:
        """Create a DeepSeek adapter using DeepSeek credentials."""
        super().__init__("deepseek", "deepseek", "DEEPSEEK_API_KEY", api_key)


class ProviderRouter:
    """Selects primary/fallback providers and redacts secret-safe metadata."""

    def __init__(self, providers: dict[str, ChatProvider], policy: ProviderPolicy) -> None:
        """Create a router from configured providers and runtime policy."""
        self._providers = providers
        self._policy = policy

    def invoke_with_fallback(self, prompt: str) -> ProviderCallResult:
        """Invoke primary provider and fallback on retryable failures."""
        primary = self._provider_for(self._policy.primary_provider)
        try:
            return primary.invoke(prompt, self._policy.primary_model_id)
        except ProviderInvocationError as exc:
            if not exc.retryable or self._policy.fallback_provider is None:
                raise
            fallback = self._provider_for(self._policy.fallback_provider)
            return fallback.invoke(prompt, self._policy.fallback_model_id)

    def _provider_for(self, provider_name: str) -> ChatProvider:
        """Return a configured provider or raise a normalized configuration error."""
        provider = self._providers.get(provider_name)
        if provider is None:
            raise ProviderInvocationError(
                f"LLM provider is not configured: {provider_name}",
                retryable=False,
            )
        return provider
