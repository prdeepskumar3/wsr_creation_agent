from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from db.models.project_assignment import ProjectAssignment


class User(UuidPrimaryKeyMixin, TimestampMixin, Base):
    """Authenticated person using the product."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(Text, unique=True)
    display_name: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)

    project_assignments: Mapped[list[ProjectAssignment]] = relationship(back_populates="user")
