from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from db.models.account import Account
    from db.models.project_assignment import ProjectAssignment
    from db.models.wsr_report import WsrReport


class Project(UuidPrimaryKeyMixin, TimestampMixin, Base):
    """Delivery project under an account."""

    __tablename__ = "projects"
    __table_args__ = (Index("ix_projects_account_id_id", "account_id", "id"),)

    account_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("accounts.id", ondelete="RESTRICT"))
    name: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)

    account: Mapped[Account] = relationship(back_populates="projects")
    assignments: Mapped[list[ProjectAssignment]] = relationship(back_populates="project")
    reports: Mapped[list[WsrReport]] = relationship(back_populates="project")
