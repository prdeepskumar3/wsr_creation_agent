from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base, UuidPrimaryKeyMixin


class AuditLog(UuidPrimaryKeyMixin, Base):
    """Append-only audit event for compliance and troubleshooting."""

    __tablename__ = "audit_logs"

    actor_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"))
    account_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("accounts.id", ondelete="RESTRICT")
    )
    project_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("projects.id", ondelete="RESTRICT")
    )
    wsr_report_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("wsr_reports.id", ondelete="RESTRICT"),
    )
    event_type: Mapped[str] = mapped_column(Text)
    field_path: Mapped[str | None] = mapped_column(Text)
    before_value: Mapped[dict[str, object] | None] = mapped_column(JSON)
    after_value: Mapped[dict[str, object] | None] = mapped_column(JSON)
    correlation_id: Mapped[UUID] = mapped_column(Uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
