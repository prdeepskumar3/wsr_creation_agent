"""Checkpoint storage adapters for resumable graph execution."""

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any, Protocol


class WorkflowCheckpointStore(Protocol):
    """Persistence interface used by graph nodes to save resumable state."""

    def save(self, workflow_run_id: str, state: dict[str, Any]) -> None:
        """Persist a state snapshot by workflow run ID."""


@dataclass
class InMemoryWorkflowCheckpointStore:
    """Small checkpointer used by tests and local graph execution."""

    checkpoints: dict[str, dict[str, Any]] = field(default_factory=dict)

    def save(self, workflow_run_id: str, state: dict[str, Any]) -> None:
        """Persist a state snapshot by workflow run ID."""
        self.checkpoints[workflow_run_id] = deepcopy(state)

    def load(self, workflow_run_id: str) -> dict[str, Any] | None:
        """Return a previously saved state snapshot."""
        checkpoint = self.checkpoints.get(workflow_run_id)
        return deepcopy(checkpoint) if checkpoint is not None else None
