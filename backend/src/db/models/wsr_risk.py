from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base, TimestampMixin, UuidPrimaryKeyMixin


class WsrRisk(UuidPrimaryKeyMixin, TimestampMixin, Base):
    """Risk/dependency row captured inside one WSR."""

    __tablename__ = "wsr_risks"
    __table_args__ = (
        Index(
            "ix_wsr_risks_report_status_severity_closure",
            "wsr_report_id",
            "status",
            "severity",
            "planned_closure_date",
        ),
    )

    account_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("accounts.id", ondelete="RESTRICT"))
    project_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("projects.id", ondelete="RESTRICT"))
    wsr_report_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("wsr_reports.id", ondelete="RESTRICT")
    )
    description: Mapped[str] = mapped_column(Text)
    severity: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)
    owner_contact: Mapped[str] = mapped_column(Text)
    mitigation: Mapped[str] = mapped_column(Text)
    planned_closure_date: Mapped[date]
    closure_remark: Mapped[str | None] = mapped_column(Text)
    source_risk_id: Mapped[UUID | None] = mapped_column(Uuid)
