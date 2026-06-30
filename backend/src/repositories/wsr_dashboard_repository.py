"""Database boundary for executive WSR dashboard queries."""

from uuid import UUID

from db.models import ExportAttempt, Project, ProjectAssignment, WsrReport, WsrRisk
from sqlalchemy import select
from sqlalchemy.orm import Session
from wsr_shared.enums import RiskSeverity, RiskStatus, WsrLifecycleStatus


class WsrDashboardRepository:
    """Loads authorized project health data for dashboard summaries."""

    def __init__(self, session: Session) -> None:
        """Create a repository backed by the caller-managed database session."""
        self._session = session

    def list_authorized_projects(
        self,
        requested_by: UUID,
        account_id: UUID | None = None,
    ) -> list[Project]:
        """Return projects visible to the requester, optionally filtered by account."""
        statement = (
            select(Project)
            .join(ProjectAssignment, ProjectAssignment.project_id == Project.id)
            .where(ProjectAssignment.user_id == requested_by)
            .order_by(Project.name)
        )
        if account_id is not None:
            statement = statement.where(Project.account_id == account_id)
        return list(self._session.scalars(statement).all())

    def get_latest_approved_report(self, project_id: UUID) -> WsrReport | None:
        """Return the latest approved WSR for one project."""
        return self._session.scalar(
            select(WsrReport)
            .where(
                WsrReport.project_id == project_id,
                WsrReport.lifecycle_status == WsrLifecycleStatus.APPROVED.value,
            )
            .order_by(WsrReport.reporting_week.desc(), WsrReport.created_at.desc())
            .limit(1)
        )

    def count_pending_approvals(self, requested_by: UUID) -> int:
        """Count reviewed reports assigned to the requester that still need approval."""
        statement = (
            select(WsrReport)
            .join(Project, Project.id == WsrReport.project_id)
            .join(ProjectAssignment, ProjectAssignment.project_id == Project.id)
            .where(
                ProjectAssignment.user_id == requested_by,
                WsrReport.lifecycle_status == WsrLifecycleStatus.REVIEWED.value,
            )
        )
        return len(list(self._session.scalars(statement).all()))

    def list_report_risks(self, wsr_report_id: UUID) -> list[WsrRisk]:
        """Return all risks for the selected report."""
        return list(
            self._session.scalars(
                select(WsrRisk).where(WsrRisk.wsr_report_id == wsr_report_id)
            ).all()
        )

    def get_latest_export_attempt(self, wsr_report_id: UUID) -> ExportAttempt | None:
        """Return the latest export attempt for one WSR report."""
        return self._session.scalar(
            select(ExportAttempt)
            .where(ExportAttempt.wsr_report_id == wsr_report_id)
            .order_by(ExportAttempt.created_at.desc(), ExportAttempt.id.desc())
            .limit(1)
        )


def is_open_high_risk(risk: WsrRisk) -> bool:
    """Return whether a risk is active and high severity."""
    return risk.severity == RiskSeverity.HIGH.value and risk.status in {
        RiskStatus.OPEN.value,
        RiskStatus.IN_PROGRESS.value,
    }
