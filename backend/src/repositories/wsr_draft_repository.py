"""Database queries used by the WSR draft service."""

from datetime import date
from uuid import UUID

from db.models import Project, ProjectAssignment, WsrReport, WsrRisk
from sqlalchemy import delete, select
from sqlalchemy.orm import Session


class WsrDraftRepository:
    """Small persistence boundary for WSR draft reports and risk rows.

    This class intentionally contains query logic only. Business rules stay in the
    service and domain validators so repository methods remain predictable and easy to
    test with an in-memory database.
    """

    def __init__(self, session: Session) -> None:
        """Create a repository backed by the caller-managed SQLAlchemy session."""
        self._session = session

    def has_project_access(self, account_id: UUID, project_id: UUID, user_id: UUID) -> bool:
        """Return whether a user assignment exists for the account/project pair."""
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

    def find_current_draft(
        self,
        account_id: UUID,
        project_id: UUID,
        reporting_week: date,
    ) -> WsrReport | None:
        """Find the editable version-one draft for one reporting week."""
        statement = select(WsrReport).where(
            WsrReport.account_id == account_id,
            WsrReport.project_id == project_id,
            WsrReport.reporting_week == reporting_week,
            WsrReport.lifecycle_status == "DRAFT",
            WsrReport.version_number == 1,
        )
        return self._session.scalar(statement)

    def get_draft(self, wsr_id: UUID) -> WsrReport | None:
        """Return an editable draft report by id, excluding generated/approved reports."""
        statement = select(WsrReport).where(
            WsrReport.id == wsr_id,
            WsrReport.lifecycle_status == "DRAFT",
        )
        return self._session.scalar(statement)

    def replace_risks(self, wsr_report: WsrReport, risks: list[WsrRisk]) -> None:
        """Replace draft risk rows so persistence mirrors the latest submitted form."""
        self._session.execute(delete(WsrRisk).where(WsrRisk.wsr_report_id == wsr_report.id))
        for risk in risks:
            self._session.add(risk)

    def list_risks(self, wsr_report_id: UUID) -> list[WsrRisk]:
        """Return persisted draft risk rows in stable creation order."""
        statement = select(WsrRisk).where(WsrRisk.wsr_report_id == wsr_report_id).order_by(
            WsrRisk.created_at,
            WsrRisk.id,
        )
        return list(self._session.scalars(statement).all())

    def save(self, wsr_report: WsrReport) -> WsrReport:
        """Attach a report to the session and flush UUIDs needed by child rows."""
        self._session.add(wsr_report)
        self._session.flush()
        return wsr_report
