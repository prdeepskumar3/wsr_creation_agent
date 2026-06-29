from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from db.models.project import Project
    from db.models.user import User


class ProjectAssignment(UuidPrimaryKeyMixin, TimestampMixin, Base):
    """Role mapping used for account/project authorization."""

    __tablename__ = "project_assignments"
    __table_args__ = (
        UniqueConstraint("user_id", "project_id", name="uq_project_assignments_user_project"),
    )

    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"))
    project_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("projects.id", ondelete="RESTRICT"))
    role: Mapped[str] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="project_assignments")
    project: Mapped[Project] = relationship(back_populates="assignments")
