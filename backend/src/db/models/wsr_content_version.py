from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Text, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from db.models.wsr_report import WsrReport


class WsrContentVersion(UuidPrimaryKeyMixin, Base):
    """PM-editable customer-facing report content version."""

    __tablename__ = "wsr_content_versions"
    __table_args__ = (
        UniqueConstraint(
            "wsr_report_id",
            "version_number",
            name="uq_wsr_content_versions_report_version",
        ),
        Index(
            "uq_wsr_content_versions_one_approved",
            "wsr_report_id",
            unique=True,
            sqlite_where=text("status = 'APPROVED'"),
            postgresql_where=text("status = 'APPROVED'"),
        ),
    )

    account_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("accounts.id", ondelete="RESTRICT"))
    project_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("projects.id", ondelete="RESTRICT"))
    wsr_report_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("wsr_reports.id", ondelete="RESTRICT")
    )
    source_ai_draft_id: Mapped[UUID | None] = mapped_column(
        Uuid,
        ForeignKey("ai_drafts.id", ondelete="RESTRICT"),
    )
    edited_by: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"))
    version_number: Mapped[int]
    status: Mapped[str] = mapped_column(Text)
    content_sections: Mapped[dict[str, object]] = mapped_column(JSON)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    wsr_report: Mapped[WsrReport] = relationship(back_populates="content_versions")
