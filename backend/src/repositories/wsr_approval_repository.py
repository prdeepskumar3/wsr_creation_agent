"""Database boundary for WSR approval workflows."""

from uuid import UUID

from db.models import ApprovalEvent, Project, ProjectAssignment, WsrContentVersion, WsrReport
from sqlalchemy import select
from sqlalchemy.orm import Session


class WsrApprovalRepository:
    """Persists and loads records needed for formal WSR approval."""

    def __init__(self, session: Session) -> None:
        """Create a repository backed by the caller-managed database session."""
        self._session = session

    def has_project_access(self, account_id: UUID, project_id: UUID, user_id: UUID) -> bool:
        """Return whether the user is assigned to the report account/project."""
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
        """Return a content version that belongs to the requested WSR."""
        statement = select(WsrContentVersion).where(
            WsrContentVersion.id == content_version_id,
            WsrContentVersion.wsr_report_id == wsr_report_id,
        )
        return self._session.scalar(statement)

    def save_approval_event(self, approval_event: ApprovalEvent) -> ApprovalEvent:
        """Persist an approval event and flush its UUID for the API response."""
        self._session.add(approval_event)
        self._session.flush()
        return approval_event
