"""Database queries used by the WSR draft service."""

from datetime import date
from uuid import UUID

from db.models import Project, ProjectAssignment, WsrContentVersion, WsrReport, WsrRisk
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from wsr_shared.enums import RiskStatus, WsrLifecycleStatus


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

    def list_carry_forward_risks(self, account_id: UUID, project_id: UUID) -> list[WsrRisk]:
        """Return active risks from the latest approved WSR for the same project."""
        latest_approved_report = self.get_latest_approved_report(account_id, project_id)
        if latest_approved_report is None:
            return []
        return self.list_active_risks_for_report(latest_approved_report.id)

    def get_latest_approved_report(self, account_id: UUID, project_id: UUID) -> WsrReport | None:
        """Return the most recent approved WSR for an account/project pair."""
        return self._session.scalar(
            select(WsrReport)
            .where(
                WsrReport.account_id == account_id,
                WsrReport.project_id == project_id,
                WsrReport.lifecycle_status == WsrLifecycleStatus.APPROVED.value,
            )
            .order_by(WsrReport.reporting_week.desc(), WsrReport.created_at.desc())
            .limit(1)
        )

    def get_approved_content_version(self, wsr_report_id: UUID) -> WsrContentVersion | None:
        """Return the approved customer-facing content version for one WSR."""
        return self._session.scalar(
            select(WsrContentVersion)
            .where(
                WsrContentVersion.wsr_report_id == wsr_report_id,
                WsrContentVersion.status == WsrLifecycleStatus.APPROVED.value,
            )
            .order_by(WsrContentVersion.version_number.desc(), WsrContentVersion.created_at.desc())
            .limit(1)
        )

    def list_active_risks_for_report(self, wsr_report_id: UUID) -> list[WsrRisk]:
        """Return active risk rows for one WSR report."""
        statement = (
            select(WsrRisk)
            .where(
                WsrRisk.wsr_report_id == wsr_report_id,
                WsrRisk.status.in_([RiskStatus.OPEN.value, RiskStatus.IN_PROGRESS.value]),
            )
            .order_by(WsrRisk.created_at, WsrRisk.id)
        )
        return list(self._session.scalars(statement).all())

    def list_active_project_risks(
        self,
        account_id: UUID,
        project_id: UUID,
        exclude_report_id: UUID | None = None,
    ) -> list[WsrRisk]:
        """Return active risks already persisted for duplicate checks."""
        statement = select(WsrRisk).where(
            WsrRisk.account_id == account_id,
            WsrRisk.project_id == project_id,
            WsrRisk.status.in_([RiskStatus.OPEN.value, RiskStatus.IN_PROGRESS.value]),
        )
        if exclude_report_id is not None:
            statement = statement.where(WsrRisk.wsr_report_id != exclude_report_id)
        return list(self._session.scalars(statement).all())

    def list_project_risks_for_validation(
        self,
        account_id: UUID,
        project_id: UUID,
        exclude_report_id: UUID | None = None,
    ) -> list[WsrRisk]:
        """Return project risks needed for duplicate and lifecycle validation."""
        statement = select(WsrRisk).where(
            WsrRisk.account_id == account_id,
            WsrRisk.project_id == project_id,
        )
        if exclude_report_id is not None:
            statement = statement.where(WsrRisk.wsr_report_id != exclude_report_id)
        return list(self._session.scalars(statement).all())

    def save(self, wsr_report: WsrReport) -> WsrReport:
        """Attach a report to the session and flush UUIDs needed by child rows."""
        self._session.add(wsr_report)
        self._session.flush()
        return wsr_report
