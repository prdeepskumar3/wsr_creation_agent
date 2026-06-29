from __future__ import annotations

from uuid import UUID

from sqlalchemy import JSON, ForeignKey, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base, TimestampMixin, UuidPrimaryKeyMixin


class AiDraft(UuidPrimaryKeyMixin, TimestampMixin, Base):
    """Generated customer-facing draft sections from one workflow run."""

    __tablename__ = "ai_drafts"

    account_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("accounts.id", ondelete="RESTRICT"))
    project_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("projects.id", ondelete="RESTRICT"))
    wsr_report_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("wsr_reports.id", ondelete="RESTRICT")
    )
    workflow_run_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("workflow_runs.id", ondelete="RESTRICT")
    )
    draft_sections: Mapped[dict[str, object]] = mapped_column(JSON)
    qa_warnings: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
