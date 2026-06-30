"""Application service for customer-safe WSR export requests."""

from datetime import UTC, datetime
from uuid import UUID

from db.models import ExportAttempt, WsrContentVersion
from repositories.wsr_export_repository import WsrExportRepository
from sqlalchemy.orm import Session
from wsr_shared.dtos import WsrExportRequestDTO, WsrExportResponseDTO
from wsr_shared.enums import WsrExportStatus, WsrLifecycleStatus

from services.pptx_export_renderer import PptxRenderError, render_wsr_pptx

CUSTOMER_EXPORT_SECTION_KEYS = {
    "schemaVersion",
    "reportMetadata",
    "metricSummary",
    "executiveSummary",
    "deliveryProgress",
    "keyAchievements",
    "risksAndDependenciesSummary",
    "nextWeekFocusAndActions",
    "customerFacingRemarks",
}


class WsrExportAuthorizationError(Exception):
    """Raised when a user is not authorized to export a report."""


class WsrExportNotFoundError(Exception):
    """Raised when the WSR or selected content version does not exist."""


class WsrExportStateError(Exception):
    """Raised when export is requested before approval."""


class WsrExportService:
    """Coordinates customer-facing export attempts from approved content versions."""

    def __init__(self, session: Session) -> None:
        """Create a service bound to one SQLAlchemy session."""
        self._session = session
        self._repository = WsrExportRepository(session)

    def request_pptx_export(
        self,
        wsr_id: UUID,
        requested_by: UUID,
        payload: WsrExportRequestDTO,
    ) -> WsrExportResponseDTO:
        """Create a queued PPTX export attempt for an approved WSR."""
        report = self._repository.get_report(wsr_id)
        if report is None:
            raise WsrExportNotFoundError("WSR report was not found.")
        if not self._repository.has_project_access(
            report.account_id,
            report.project_id,
            requested_by,
        ):
            raise WsrExportAuthorizationError("User is not authorized for this account/project.")
        if report.lifecycle_status != WsrLifecycleStatus.APPROVED.value:
            raise WsrExportStateError("WSR must be approved before export.")

        content_version = self._repository.get_content_version(
            report.id,
            payload.content_version_id,
        )
        if content_version is None:
            raise WsrExportNotFoundError("WSR content version was not found.")
        if content_version.status != WsrLifecycleStatus.APPROVED.value:
            raise WsrExportStateError("Content version must be approved before export.")

        safe_sections = build_customer_safe_export_sections(content_version)
        object_key = (
            f"exports/{report.account_id}/{report.project_id}/{report.id}/"
            f"content-version-{content_version.version_number}.pptx"
        )
        try:
            render_wsr_pptx(safe_sections)
            export_status = WsrExportStatus.SUCCEEDED
            error_code = None
        except PptxRenderError:
            export_status = WsrExportStatus.FAILED
            error_code = "PPTX_RENDER_FAILED"

        export_attempt = self._repository.save_export_attempt(
            ExportAttempt(
                account_id=report.account_id,
                project_id=report.project_id,
                wsr_report_id=report.id,
                content_version_id=content_version.id,
                requested_by=requested_by,
                status=export_status.value,
                object_key=object_key,
                error_code=error_code,
                created_at=datetime.now(UTC),
            )
        )
        self._session.commit()

        return WsrExportResponseDTO(
            export_attempt_id=export_attempt.id,
            wsr_id=report.id,
            content_version_id=content_version.id,
            status=WsrExportStatus(export_attempt.status),
            object_key=export_attempt.object_key,
            error_code=export_attempt.error_code,
        )


def build_customer_safe_export_sections(
    content_version: WsrContentVersion,
) -> dict[str, object]:
    """Return only customer-facing sections allowed to reach export generation."""
    return {
        key: value
        for key, value in content_version.content_sections.items()
        if key in CUSTOMER_EXPORT_SECTION_KEYS
    }
