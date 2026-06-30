"""Database boundary for WSR export attempts."""

from uuid import UUID

from db.models import ExportAttempt, Project, ProjectAssignment, WsrContentVersion, WsrReport
from sqlalchemy import select
from sqlalchemy.orm import Session


class WsrExportRepository:
    """Loads approved WSR content and persists export attempt records."""

    def __init__(self, session: Session) -> None:
        """Create a repository backed by the caller-managed database session."""
        self._session = session

    def has_project_access(self, account_id: UUID, project_id: UUID, user_id: UUID) -> bool:
        """Return whether the user can export for the report account/project."""
        statement = (
            select(ProjectAssignment.id)
            .join(Project, Project.id == ProjectAssignment.project_id)
            .where(
                Project.account_id == account_id,
                Project.id == project_id,
                ProjectAssignment.user_id == user_id,
            )
        )
        return self._session.scalar(statement) is not None

    def get_report(self, wsr_id: UUID) -> WsrReport | None:
        """Return a WSR report by id."""
        return self._session.get(WsrReport, wsr_id)

    def get_content_version(
        self,
        wsr_report_id: UUID,
        content_version_id: UUID,
    ) -> WsrContentVersion | None:
        """Return the selected content version when it belongs to the WSR."""
        statement = select(WsrContentVersion).where(
            WsrContentVersion.id == content_version_id,
            WsrContentVersion.wsr_report_id == wsr_report_id,
        )
        return self._session.scalar(statement)

    def save_export_attempt(self, export_attempt: ExportAttempt) -> ExportAttempt:
        """Persist an export attempt and flush its UUID."""
        self._session.add(export_attempt)
        self._session.flush()
        return export_attempt
