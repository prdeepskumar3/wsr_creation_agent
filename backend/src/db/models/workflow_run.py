from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from db.models.workflow_checkpoint import WorkflowCheckpoint


class WorkflowRun(UuidPrimaryKeyMixin, TimestampMixin, Base):
    """LangGraph execution tracking and resumable checkpoint metadata."""

    __tablename__ = "workflow_runs"

    account_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("accounts.id", ondelete="RESTRICT"))
    project_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("projects.id", ondelete="RESTRICT"))
    wsr_report_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("wsr_reports.id", ondelete="RESTRICT")
    )
    requested_by: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"))
    status: Mapped[str] = mapped_column(Text)
    checkpoint_id: Mapped[str | None] = mapped_column(Text)
    retrieval_metadata: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    workflow_error_summary: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)

    checkpoints: Mapped[list[WorkflowCheckpoint]] = relationship(back_populates="workflow_run")
