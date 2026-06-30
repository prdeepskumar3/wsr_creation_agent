from datetime import UTC, date, datetime
from uuid import UUID

from api.v1.router import api_v1_router
from app.create_app import create_app
from db.base import Base
from db.models import Account, ApprovalEvent, Project, ProjectAssignment, User, WsrContentVersion
from db.models.wsr_report import WsrReport
from fastapi.routing import APIRoute
from services.wsr_approval_service import WsrApprovalService, WsrApprovalStateError
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from wsr_shared.dtos import WsrApprovalRequestDTO
from wsr_shared.enums import (
    DeliveryModel,
    WsrApprovalDecision,
    WsrGenerationStatus,
    WsrLifecycleStatus,
)


def collect_api_paths(routes: list[object], prefix: str = "") -> set[str]:
    paths: set[str] = set()
    for route in routes:
        if isinstance(route, APIRoute):
            paths.add(f"{prefix}{route.path}")
            continue
        original_router = getattr(route, "original_router", None)
        include_context = getattr(route, "include_context", None)
        child_prefix = getattr(include_context, "prefix", "") if include_context else ""
        child_routes = getattr(original_router, "routes", None)
        if child_routes is not None:
            paths |= collect_api_paths(child_routes, f"{prefix}{child_prefix}")
    return paths


def create_test_session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


def seed_authorized_project(session: Session) -> tuple[UUID, UUID, UUID]:
    user = User(email="pm@example.com", display_name="Project Manager", status="ACTIVE")
    account = Account(name="TechCorp Inc.", status="ACTIVE")
    project = Project(account=account, name="TechCorp Portal Revamp", status="ACTIVE")
    assignment = ProjectAssignment(user=user, project=project, role="PM")
    session.add_all([user, account, project, assignment])
    session.commit()
    return account.id, project.id, user.id


def create_reviewed_report(
    session: Session,
    account_id: UUID,
    project_id: UUID,
    prepared_by: UUID,
) -> tuple[WsrReport, WsrContentVersion]:
    report = WsrReport(
        account_id=account_id,
        project_id=project_id,
        prepared_by=prepared_by,
        lifecycle_status=WsrLifecycleStatus.REVIEWED.value,
        generation_status=WsrGenerationStatus.HUMAN_REVIEWED.value,
        reporting_week=date(2025, 6, 23),
        delivery_model=DeliveryModel.SPRINT.value,
        schema_version="wsr-draft.v1",
        version_number=1,
        entered_data_snapshot={},
        model_setup_snapshot={},
        weekly_progress_snapshot={},
        calculated_metrics_snapshot={},
    )
    session.add(report)
    session.flush()
    content_version = WsrContentVersion(
        account_id=account_id,
        project_id=project_id,
        wsr_report_id=report.id,
        source_ai_draft_id=None,
        edited_by=prepared_by,
        version_number=1,
        status=WsrLifecycleStatus.REVIEWED.value,
        content_sections={"executiveSummary": "Customer-ready reviewed summary."},
        approved_at=None,
        created_at=datetime.now(UTC),
    )
    session.add(content_version)
    session.commit()
    return report, content_version


def approval_request(content_version_id: UUID) -> WsrApprovalRequestDTO:
    return WsrApprovalRequestDTO(
        content_version_id=content_version_id,
        decision=WsrApprovalDecision.APPROVE,
        approval_note="Approved for customer sharing.",
    )


def test_approve_reviewed_content_version_creates_approval_event() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        report, content_version = create_reviewed_report(
            session,
            account_id,
            project_id,
            prepared_by,
        )

        response = WsrApprovalService(session).approve_content_version(
            report.id,
            prepared_by,
            approval_request(content_version.id),
        )
        approval_events = session.scalars(select(ApprovalEvent)).all()

    assert response.lifecycle_status == WsrLifecycleStatus.APPROVED
    assert response.content_version_status == WsrLifecycleStatus.APPROVED
    assert response.approval_event_id == approval_events[0].id
    assert content_version.status == WsrLifecycleStatus.APPROVED.value
    assert content_version.approved_at is not None
    assert report.lifecycle_status == WsrLifecycleStatus.APPROVED.value


def test_approve_rejects_unreviewed_report_state() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        report, content_version = create_reviewed_report(
            session,
            account_id,
            project_id,
            prepared_by,
        )
        report.lifecycle_status = WsrLifecycleStatus.DRAFT.value
        session.commit()

        try:
            WsrApprovalService(session).approve_content_version(
                report.id,
                prepared_by,
                approval_request(content_version.id),
            )
        except WsrApprovalStateError as exc:
            assert str(exc) == "WSR must be reviewed before approval."
        else:
            raise AssertionError("Expected WsrApprovalStateError.")


def test_approve_rejects_already_approved_content_version() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        report, content_version = create_reviewed_report(
            session,
            account_id,
            project_id,
            prepared_by,
        )
        content_version.status = WsrLifecycleStatus.APPROVED.value
        session.commit()

        try:
            WsrApprovalService(session).approve_content_version(
                report.id,
                prepared_by,
                approval_request(content_version.id),
            )
        except WsrApprovalStateError as exc:
            assert str(exc) == "Content version must be reviewed before approval."
        else:
            raise AssertionError("Expected WsrApprovalStateError.")


def test_wsr_approval_route_is_registered() -> None:
    registered_paths = collect_api_paths(create_app().routes)
    registered_paths |= collect_api_paths(api_v1_router.routes, "/api/v1")

    assert "/api/v1/wsr-approvals/{wsr_id}/approve" in registered_paths
