from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import JSON, DateTime, ForeignKey, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base, UuidPrimaryKeyMixin


class AdminSetting(UuidPrimaryKeyMixin, Base):
    """Runtime configuration value; secrets are stored outside the database."""

    __tablename__ = "admin_settings"

    setting_key: Mapped[str] = mapped_column(Text, unique=True)
    value: Mapped[dict[str, object]] = mapped_column(JSON)
    updated_by: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="RESTRICT"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
