from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, ForeignKey, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from db.models.project import Project
    from db.models.wsr_content_version import WsrContentVersion


class WsrReport(UuidPrimaryKeyMixin, TimestampMixin, Base):
    """Weekly status report header and PM-entered snapshots."""

    __tablename__ = "wsr_reports"
    __table_args__ = (
        UniqueConstraint(
            "account_id",
            "project_id",
            "reporting_week",
            "version_number",
            name="uq_wsr_reports_account_project_week_version",
        ),
    )

    account_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("accounts.id", ondelete="RESTRICT"))
    project_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("projects.id", ondelete="RESTRICT"))
    prepared_by: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"))
    lifecycle_status: Mapped[str] = mapped_column(Text)
    generation_status: Mapped[str] = mapped_column(Text)
    reporting_week: Mapped[date]
    delivery_model: Mapped[str] = mapped_column(Text)
    schema_version: Mapped[str] = mapped_column(Text)
    version_number: Mapped[int] = mapped_column(default=1)
    entered_data_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    model_setup_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    weekly_progress_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    calculated_metrics_snapshot: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)

    project: Mapped[Project] = relationship(back_populates="reports")
    content_versions: Mapped[list[WsrContentVersion]] = relationship(back_populates="wsr_report")
