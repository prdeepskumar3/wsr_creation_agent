from datetime import date
from uuid import UUID

from db.models import Project, ProjectAssignment, WsrReport, WsrRisk
from sqlalchemy import delete, select
from sqlalchemy.orm import Session


class WsrDraftRepository:
    """Handles database access for WSR draft persistence."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def has_project_access(self, account_id: UUID, project_id: UUID, user_id: UUID) -> bool:
        """Return whether the user is assigned to the account/project."""
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
        """Find the current editable draft for one account/project/reporting week."""
        statement = select(WsrReport).where(
            WsrReport.account_id == account_id,
            WsrReport.project_id == project_id,
            WsrReport.reporting_week == reporting_week,
            WsrReport.lifecycle_status == "DRAFT",
            WsrReport.version_number == 1,
        )
        return self._session.scalar(statement)

    def get_draft(self, wsr_id: UUID) -> WsrReport | None:
        """Return a WSR draft by id."""
        statement = select(WsrReport).where(
            WsrReport.id == wsr_id,
            WsrReport.lifecycle_status == "DRAFT",
        )
        return self._session.scalar(statement)

    def replace_risks(self, wsr_report: WsrReport, risks: list[WsrRisk]) -> None:
        """Replace all risk rows for a draft with the latest UI state."""
        self._session.execute(delete(WsrRisk).where(WsrRisk.wsr_report_id == wsr_report.id))
        for risk in risks:
            self._session.add(risk)

    def list_risks(self, wsr_report_id: UUID) -> list[WsrRisk]:
        """Return risks for a draft in stable creation order."""
        statement = select(WsrRisk).where(WsrRisk.wsr_report_id == wsr_report_id).order_by(
            WsrRisk.created_at,
            WsrRisk.id,
        )
        return list(self._session.scalars(statement).all())

    def save(self, wsr_report: WsrReport) -> WsrReport:
        """Persist a draft report and flush generated identifiers."""
        self._session.add(wsr_report)
        self._session.flush()
        return wsr_report
