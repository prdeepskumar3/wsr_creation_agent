from datetime import UTC, date, datetime
from uuid import UUID

from api.v1.router import api_v1_router
from app.create_app import create_app
from db.base import Base
from db.models import (
    Account,
    ExportAttempt,
    Project,
    ProjectAssignment,
    User,
    WsrContentVersion,
    WsrReport,
    WsrRisk,
)
from fastapi.routing import APIRoute
from services.wsr_dashboard_service import WsrDashboardService
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from wsr_shared.enums import (
    DeliveryModel,
    RiskSeverity,
    RiskStatus,
    WsrExportStatus,
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


def seed_project(session: Session) -> tuple[UUID, UUID, UUID]:
    user = User(email="exec@example.com", display_name="Delivery Executive", status="ACTIVE")
    account = Account(name="TechCorp Inc.", status="ACTIVE")
    project = Project(account=account, name="TechCorp Portal Revamp", status="ACTIVE")
    assignment = ProjectAssignment(user=user, project=project, role="EXECUTIVE")
    session.add_all([user, account, project, assignment])
    session.commit()
    return account.id, project.id, user.id


def add_report(
    session: Session,
    account_id: UUID,
    project_id: UUID,
    prepared_by: UUID,
) -> WsrReport:
    report = WsrReport(
        account_id=account_id,
        project_id=project_id,
        prepared_by=prepared_by,
        lifecycle_status=WsrLifecycleStatus.APPROVED.value,
        generation_status=WsrGenerationStatus.HUMAN_REVIEWED.value,
        reporting_week=date(2025, 6, 23),
        delivery_model=DeliveryModel.SPRINT.value,
        schema_version="wsr-draft.v1",
        version_number=1,
        entered_data_snapshot={},
        model_setup_snapshot={},
        weekly_progress_snapshot={"ragStatus": "AMBER"},
        calculated_metrics_snapshot={"completionPercent": 67},
    )
    session.add(report)
    session.flush()
    return report


def add_high_risk(session: Session, report: WsrReport) -> None:
    risk = WsrRisk(
        account_id=report.account_id,
        project_id=report.project_id,
        wsr_report_id=report.id,
        description="Vendor API documentation dependency.",
        severity=RiskSeverity.HIGH.value,
        status=RiskStatus.IN_PROGRESS.value,
        owner_contact="Priya Rao",
        mitigation="Parallel validation path is active.",
        planned_closure_date=date(2025, 6, 20),
        closure_remark=None,
    )
    session.add(risk)


def add_export_attempt(session: Session, report: WsrReport, requested_by: UUID) -> None:
    content_version = WsrContentVersion(
        account_id=report.account_id,
        project_id=report.project_id,
        wsr_report_id=report.id,
        source_ai_draft_id=None,
        edited_by=requested_by,
        version_number=1,
        status=WsrLifecycleStatus.APPROVED.value,
        content_sections={"executiveSummary": "Approved summary."},
        approved_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
    )
    session.add(content_version)
    session.flush()
    export_attempt = ExportAttempt(
        account_id=report.account_id,
        project_id=report.project_id,
        wsr_report_id=report.id,
        content_version_id=content_version.id,
        requested_by=requested_by,
        status=WsrExportStatus.QUEUED.value,
        object_key="exports/report.pptx",
        error_code=None,
        created_at=datetime.now(UTC),
    )
    session.add(export_attempt)


def test_dashboard_returns_latest_approved_wsr_health_for_authorized_project() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, requested_by = seed_project(session)
        report = add_report(session, account_id, project_id, requested_by)
        add_high_risk(session, report)
        add_export_attempt(session, report, requested_by)
        session.commit()

        dashboard = WsrDashboardService(session).get_dashboard(
            requested_by,
            today=date(2025, 6, 30),
        )

    assert dashboard.total_projects == 1
    assert dashboard.projects_with_high_risks == 1
    assert dashboard.items[0].latest_wsr_id == report.id
    assert dashboard.items[0].rag_status == "AMBER"
    assert dashboard.items[0].open_high_risk_count == 1
    assert dashboard.items[0].overdue_risk_count == 1
    assert dashboard.items[0].latest_export_status == WsrExportStatus.QUEUED


def test_dashboard_route_is_registered() -> None:
    registered_paths = collect_api_paths(create_app().routes)
    registered_paths |= collect_api_paths(api_v1_router.routes, "/api/v1")

    assert "/api/v1/wsr-dashboard" in registered_paths
