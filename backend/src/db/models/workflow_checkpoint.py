from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from db.models.workflow_run import WorkflowRun


class WorkflowCheckpoint(UuidPrimaryKeyMixin, Base):
    """Durable graph checkpoint fallback when LangGraph checkpointer is unavailable."""

    __tablename__ = "workflow_checkpoints"

    workflow_run_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("workflow_runs.id", ondelete="RESTRICT"),
    )
    checkpoint_name: Mapped[str] = mapped_column(Text)
    state_payload: Mapped[dict[str, object]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    workflow_run: Mapped[WorkflowRun] = relationship(back_populates="checkpoints")
