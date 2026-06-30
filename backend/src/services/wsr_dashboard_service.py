"""Application service for executive WSR dashboard summaries."""

from datetime import date
from uuid import UUID

from repositories.wsr_dashboard_repository import WsrDashboardRepository, is_open_high_risk
from sqlalchemy.orm import Session
from wsr_shared.dtos import WsrDashboardItemDTO, WsrDashboardResponseDTO
from wsr_shared.enums import (
    DeliveryModel,
    RagStatus,
    RiskStatus,
    WsrExportStatus,
    WsrLifecycleStatus,
)


class WsrDashboardService:
    """Builds authorized dashboard rows from approved customer-facing WSR data."""

    def __init__(self, session: Session) -> None:
        """Create a service bound to one SQLAlchemy session."""
        self._repository = WsrDashboardRepository(session)

    def get_dashboard(
        self,
        requested_by: UUID,
        account_id: UUID | None = None,
        today: date | None = None,
    ) -> WsrDashboardResponseDTO:
        """Return latest approved WSR health for projects visible to a requester."""
        current_date = today or date.today()
        items: list[WsrDashboardItemDTO] = []
        for project in self._repository.list_authorized_projects(requested_by, account_id):
            report = self._repository.get_latest_approved_report(project.id)
            if report is None:
                items.append(
                    WsrDashboardItemDTO(
                        account_id=project.account_id,
                        account_name=project.account.name,
                        project_id=project.id,
                        project_name=project.name,
                        latest_wsr_id=None,
                        reporting_week=None,
                        delivery_model=None,
                        lifecycle_status=None,
                        rag_status=None,
                        open_high_risk_count=0,
                        overdue_risk_count=0,
                        latest_export_status=None,
                    )
                )
                continue

            risks = self._repository.list_report_risks(report.id)
            latest_export = self._repository.get_latest_export_attempt(report.id)
            rag_status = self._extract_rag_status(report.weekly_progress_snapshot)
            items.append(
                WsrDashboardItemDTO(
                    account_id=project.account_id,
                    account_name=project.account.name,
                    project_id=project.id,
                    project_name=project.name,
                    latest_wsr_id=report.id,
                    reporting_week=report.reporting_week,
                    delivery_model=DeliveryModel(report.delivery_model),
                    lifecycle_status=WsrLifecycleStatus(report.lifecycle_status),
                    rag_status=rag_status,
                    open_high_risk_count=sum(1 for risk in risks if is_open_high_risk(risk)),
                    overdue_risk_count=sum(
                        1
                        for risk in risks
                        if risk.status in {RiskStatus.OPEN.value, RiskStatus.IN_PROGRESS.value}
                        and risk.planned_closure_date < current_date
                    ),
                    latest_export_status=(
                        WsrExportStatus(latest_export.status) if latest_export is not None else None
                    ),
                )
            )

        return WsrDashboardResponseDTO(
            items=items,
            total_projects=len(items),
            projects_with_high_risks=sum(1 for item in items if item.open_high_risk_count > 0),
            pending_approval_count=self._repository.count_pending_approvals(requested_by),
        )

    def _extract_rag_status(self, weekly_progress: dict[str, object]) -> RagStatus | None:
        """Read customer-facing RAG status from stored weekly progress."""
        rag_status = weekly_progress.get("ragStatus")
        if isinstance(rag_status, str) and rag_status in {status.value for status in RagStatus}:
            return RagStatus(rag_status)
        return None
