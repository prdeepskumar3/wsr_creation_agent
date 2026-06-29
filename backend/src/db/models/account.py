from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base, TimestampMixin, UuidPrimaryKeyMixin

if TYPE_CHECKING:
    from db.models.project import Project


class Account(UuidPrimaryKeyMixin, TimestampMixin, Base):
    """Customer/account boundary."""

    __tablename__ = "accounts"

    name: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text)

    projects: Mapped[list[Project]] = relationship(back_populates="account")
