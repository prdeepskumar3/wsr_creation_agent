from datetime import UTC, date, datetime
from uuid import UUID

from api.v1.router import api_v1_router
from app.create_app import create_app
from db.base import Base
from db.models import Account, ExportAttempt, Project, ProjectAssignment, User, WsrContentVersion
from db.models.wsr_report import WsrReport
from fastapi.routing import APIRoute
from services.pptx_export_renderer import render_wsr_pptx
from services.wsr_export_service import (
    WsrExportService,
    WsrExportStateError,
    build_customer_safe_export_sections,
)
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from wsr_shared.dtos import WsrExportRequestDTO
from wsr_shared.enums import DeliveryModel, WsrExportStatus, WsrGenerationStatus, WsrLifecycleStatus


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


def create_report_with_content(
    session: Session,
    account_id: UUID,
    project_id: UUID,
    prepared_by: UUID,
    lifecycle_status: WsrLifecycleStatus = WsrLifecycleStatus.APPROVED,
    content_status: WsrLifecycleStatus = WsrLifecycleStatus.APPROVED,
) -> tuple[WsrReport, WsrContentVersion]:
    report = WsrReport(
        account_id=account_id,
        project_id=project_id,
        prepared_by=prepared_by,
        lifecycle_status=lifecycle_status.value,
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
        status=content_status.value,
        content_sections={
            "executiveSummary": "Customer-ready approved summary.",
            "deliveryProgress": "Approved delivery progress.",
            "pmQualityInsights": "This PM-only insight must never be exported.",
            "statusDiscrepancyEvidence": "Internal evidence must never be exported.",
        },
        approved_at=datetime.now(UTC) if content_status == WsrLifecycleStatus.APPROVED else None,
        created_at=datetime.now(UTC),
    )
    session.add(content_version)
    session.commit()
    return report, content_version


def export_request(content_version_id: UUID) -> WsrExportRequestDTO:
    return WsrExportRequestDTO(content_version_id=content_version_id)


def test_export_approved_wsr_creates_successful_export_attempt() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        report, content_version = create_report_with_content(
            session,
            account_id,
            project_id,
            prepared_by,
        )

        response = WsrExportService(session).request_pptx_export(
            report.id,
            prepared_by,
            export_request(content_version.id),
        )
        export_attempts = session.scalars(select(ExportAttempt)).all()

    assert response.status == WsrExportStatus.SUCCEEDED
    assert response.export_attempt_id == export_attempts[0].id
    assert response.content_version_id == content_version.id
    assert response.object_key is not None
    assert export_attempts[0].status == WsrExportStatus.SUCCEEDED.value
    assert export_attempts[0].requested_by == prepared_by


def test_export_before_report_approval_is_blocked() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        report, content_version = create_report_with_content(
            session,
            account_id,
            project_id,
            prepared_by,
            lifecycle_status=WsrLifecycleStatus.REVIEWED,
            content_status=WsrLifecycleStatus.APPROVED,
        )

        try:
            WsrExportService(session).request_pptx_export(
                report.id,
                prepared_by,
                export_request(content_version.id),
            )
        except WsrExportStateError as exc:
            assert str(exc) == "WSR must be approved before export."
        else:
            raise AssertionError("Expected WsrExportStateError.")


def test_export_excludes_pm_only_content_sections() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        _report, content_version = create_report_with_content(
            session,
            account_id,
            project_id,
            prepared_by,
        )

        safe_sections = build_customer_safe_export_sections(content_version)

    assert safe_sections == {
        "executiveSummary": "Customer-ready approved summary.",
        "deliveryProgress": "Approved delivery progress.",
    }


def test_export_renderer_creates_pptx_package_from_customer_safe_sections() -> None:
    pptx_bytes = render_wsr_pptx(
        {
            "executiveSummary": "Customer-ready approved summary.",
            "pmQualityInsights": "This should not be passed into renderer.",
        }
    )

    assert pptx_bytes.startswith(b"PK")
    assert b"ppt/presentation.xml" in pptx_bytes


def test_wsr_export_route_is_registered() -> None:
    registered_paths = collect_api_paths(create_app().routes)
    registered_paths |= collect_api_paths(api_v1_router.routes, "/api/v1")

    assert "/api/v1/wsr-exports/{wsr_id}/pptx" in registered_paths
