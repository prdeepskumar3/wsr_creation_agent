from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base, UuidPrimaryKeyMixin


class ApprovalEvent(UuidPrimaryKeyMixin, Base):
    """Submit, approve, reject, and re-approval history."""

    __tablename__ = "approval_events"

    account_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("accounts.id", ondelete="RESTRICT"))
    project_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("projects.id", ondelete="RESTRICT"))
    wsr_report_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("wsr_reports.id", ondelete="RESTRICT")
    )
    content_version_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("wsr_content_versions.id", ondelete="RESTRICT"),
    )
    actor_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"))
    decision: Mapped[str] = mapped_column(Text)
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
