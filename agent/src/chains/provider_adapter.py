from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderPolicy:
    """Provider policy resolved before model invocation."""

    primary_provider: str = "stub"
    fallback_provider: str | None = None

    @property
    def requires_real_credentials(self) -> bool:
        """Return whether this policy needs real provider credentials."""
        return self.primary_provider != "stub"

