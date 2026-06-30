"""Application service for formal WSR approval decisions."""

from datetime import UTC, datetime
from uuid import UUID

from db.models import ApprovalEvent, WsrContentVersion, WsrReport
from repositories.wsr_approval_repository import WsrApprovalRepository
from sqlalchemy.orm import Session
from wsr_shared.dtos import WsrApprovalRequestDTO, WsrApprovalResponseDTO
from wsr_shared.enums import WsrApprovalDecision, WsrLifecycleStatus


class WsrApprovalAuthorizationError(Exception):
    """Raised when a user is not authorized to approve a report."""


class WsrApprovalNotFoundError(Exception):
    """Raised when the WSR or selected content version does not exist."""


class WsrApprovalStateError(Exception):
    """Raised when approval is requested before the WSR is ready."""


class WsrApprovalService:
    """Coordinates approval of reviewed customer-facing WSR content."""

    def __init__(self, session: Session) -> None:
        """Create a service bound to one SQLAlchemy session."""
        self._session = session
        self._repository = WsrApprovalRepository(session)

    def approve_content_version(
        self,
        wsr_id: UUID,
        requested_by: UUID,
        payload: WsrApprovalRequestDTO,
    ) -> WsrApprovalResponseDTO:
        """Apply a formal approve, approve-with-edits, or reject decision."""
        report = self._repository.get_report(wsr_id)
        if report is None:
            raise WsrApprovalNotFoundError("WSR report was not found.")
        if not self._repository.has_project_access(
            report.account_id,
            report.project_id,
            requested_by,
        ):
            raise WsrApprovalAuthorizationError(
                "User is not authorized for this account/project."
            )
        if report.lifecycle_status != WsrLifecycleStatus.REVIEWED.value:
            raise WsrApprovalStateError("WSR must be reviewed before approval.")

        if payload.decision == WsrApprovalDecision.REJECT:
            return self._reject_report(report, requested_by, payload)

        if not payload.confirm_approval:
            raise WsrApprovalStateError("Approval requires explicit confirmation.")

        if payload.decision == WsrApprovalDecision.APPROVE_WITH_EDITS:
            return self._approve_with_edits(report, requested_by, payload)

        if payload.content_version_id is None:
            raise WsrApprovalNotFoundError("WSR content version was not found.")
        content_version = self._repository.get_content_version(
            report.id,
            payload.content_version_id,
        )
        if content_version is None:
            raise WsrApprovalNotFoundError("WSR content version was not found.")
        if content_version.status != WsrLifecycleStatus.REVIEWED.value:
            raise WsrApprovalStateError("Content version must be reviewed before approval.")

        now = datetime.now(UTC)
        content_version.status = WsrLifecycleStatus.APPROVED.value
        content_version.approved_at = now
        report.lifecycle_status = WsrLifecycleStatus.APPROVED.value

        approval_event = self._repository.save_approval_event(
            ApprovalEvent(
                account_id=report.account_id,
                project_id=report.project_id,
                wsr_report_id=report.id,
                content_version_id=content_version.id,
                actor_id=requested_by,
                decision=payload.decision.value,
                reason=payload.approval_note,
                created_at=now,
            )
        )
        self._session.commit()

        return WsrApprovalResponseDTO(
            wsr_id=report.id,
            content_version_id=content_version.id,
            approval_event_id=approval_event.id,
            lifecycle_status=WsrLifecycleStatus(report.lifecycle_status),
            content_version_status=WsrLifecycleStatus(content_version.status),
        )

    def _approve_with_edits(
        self,
        report: WsrReport,
        requested_by: UUID,
        payload: WsrApprovalRequestDTO,
    ) -> WsrApprovalResponseDTO:
        """Create a new approved content version from PM final edits."""
        if payload.content_sections is None:
            raise WsrApprovalStateError("Approve with edits requires edited content.")

        now = datetime.now(UTC)
        content_version = self._repository.save_content_version(
            WsrContentVersion(
                account_id=report.account_id,
                project_id=report.project_id,
                wsr_report_id=report.id,
                source_ai_draft_id=None,
                edited_by=requested_by,
                version_number=self._repository.next_content_version_number(report.id),
                status=WsrLifecycleStatus.APPROVED.value,
                content_sections=payload.content_sections.model_dump(mode="json", by_alias=True),
                approved_at=now,
                created_at=now,
            )
        )
        report.lifecycle_status = WsrLifecycleStatus.APPROVED.value
        approval_event = self._repository.save_approval_event(
            ApprovalEvent(
                account_id=report.account_id,
                project_id=report.project_id,
                wsr_report_id=report.id,
                content_version_id=content_version.id,
                actor_id=requested_by,
                decision=payload.decision.value,
                reason=payload.approval_note,
                created_at=now,
            )
        )
        self._session.commit()
        return WsrApprovalResponseDTO(
            wsr_id=report.id,
            content_version_id=content_version.id,
            approval_event_id=approval_event.id,
            lifecycle_status=WsrLifecycleStatus(report.lifecycle_status),
            content_version_status=WsrLifecycleStatus(content_version.status),
        )

    def _reject_report(
        self,
        report: WsrReport,
        requested_by: UUID,
        payload: WsrApprovalRequestDTO,
    ) -> WsrApprovalResponseDTO:
        """Reject a reviewed WSR and require PM feedback."""
        if not payload.rejection_reason or not payload.rejection_reason.strip():
            raise WsrApprovalStateError("Rejection requires feedback.")
        if payload.content_version_id is None:
            raise WsrApprovalNotFoundError("WSR content version was not found.")

        content_version = self._repository.get_content_version(
            report.id,
            payload.content_version_id,
        )
        if content_version is None:
            raise WsrApprovalNotFoundError("WSR content version was not found.")
        if content_version.status != WsrLifecycleStatus.REVIEWED.value:
            raise WsrApprovalStateError("Content version must be reviewed before rejection.")

        now = datetime.now(UTC)
        report.lifecycle_status = WsrLifecycleStatus.REJECTED.value
        approval_event = self._repository.save_approval_event(
            ApprovalEvent(
                account_id=report.account_id,
                project_id=report.project_id,
                wsr_report_id=report.id,
                content_version_id=content_version.id,
                actor_id=requested_by,
                decision=payload.decision.value,
                reason=payload.rejection_reason,
                created_at=now,
            )
        )
        self._session.commit()
        return WsrApprovalResponseDTO(
            wsr_id=report.id,
            content_version_id=content_version.id,
            approval_event_id=approval_event.id,
            lifecycle_status=WsrLifecycleStatus(report.lifecycle_status),
            content_version_status=WsrLifecycleStatus(content_version.status),
        )
