from __future__ import annotations

from uuid import UUID

from sqlalchemy import JSON, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base, TimestampMixin, UuidPrimaryKeyMixin


class AiInsight(UuidPrimaryKeyMixin, TimestampMixin, Base):
    """PM-only AI insight record."""

    __tablename__ = "ai_insights"

    account_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("accounts.id", ondelete="RESTRICT"))
    project_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("projects.id", ondelete="RESTRICT"))
    wsr_report_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("wsr_reports.id", ondelete="RESTRICT")
    )
    workflow_run_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("workflow_runs.id", ondelete="RESTRICT")
    )
    type: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(Text)
    evidence: Mapped[list[dict[str, object]]] = mapped_column(JSON, default=list)
    recommendation: Mapped[str] = mapped_column(Text)
    suggested_edit: Mapped[str | None] = mapped_column(Text)
    target_field: Mapped[str | None] = mapped_column(Text)
