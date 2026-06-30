from datetime import UTC, date, datetime
from uuid import UUID

from db.base import Base
from db.models import (
    Account,
    Project,
    ProjectAssignment,
    User,
    WsrContentVersion,
    WsrReport,
    WsrRisk,
)
from services.wsr_draft_service import WsrDraftService
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from wsr_shared.enums import (
    DeliveryModel,
    RiskSeverity,
    RiskStatus,
    WsrGenerationStatus,
    WsrLifecycleStatus,
)


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


def create_report(
    session: Session,
    account_id: UUID,
    project_id: UUID,
    prepared_by: UUID,
    reporting_week: date,
    lifecycle_status: WsrLifecycleStatus = WsrLifecycleStatus.APPROVED,
    delivery_model: DeliveryModel = DeliveryModel.PI,
    model_setup: dict[str, object] | None = None,
    calculated_metrics: dict[str, object] | None = None,
) -> WsrReport:
    report = WsrReport(
        account_id=account_id,
        project_id=project_id,
        prepared_by=prepared_by,
        lifecycle_status=lifecycle_status.value,
        generation_status=WsrGenerationStatus.COMPLETED.value,
        reporting_week=reporting_week,
        delivery_model=delivery_model.value,
        schema_version="wsr-draft.v1",
        version_number=1,
        entered_data_snapshot={},
        model_setup_snapshot=model_setup or {},
        weekly_progress_snapshot={},
        calculated_metrics_snapshot=calculated_metrics or {},
    )
    session.add(report)
    session.flush()
    return report


def add_approved_content(
    session: Session,
    report: WsrReport,
    edited_by: UUID,
    content_sections: dict[str, object],
) -> WsrContentVersion:
    now = datetime.now(UTC)
    content_version = WsrContentVersion(
        account_id=report.account_id,
        project_id=report.project_id,
        wsr_report_id=report.id,
        source_ai_draft_id=None,
        edited_by=edited_by,
        version_number=1,
        status=WsrLifecycleStatus.APPROVED.value,
        content_sections=content_sections,
        approved_at=now,
        created_at=now,
    )
    session.add(content_version)
    session.flush()
    return content_version


def add_risk(
    session: Session,
    report: WsrReport,
    description: str,
    status: RiskStatus = RiskStatus.OPEN,
) -> WsrRisk:
    risk = WsrRisk(
        account_id=report.account_id,
        project_id=report.project_id,
        wsr_report_id=report.id,
        description=description,
        severity=RiskSeverity.HIGH.value,
        status=status.value,
        owner_contact="Priya Rao",
        mitigation="Parallel validation interface is active.",
        planned_closure_date=date(2025, 7, 4),
        closure_remark="Resolved in the approved WSR." if status == RiskStatus.CLOSED else None,
    )
    session.add(risk)
    session.flush()
    return risk


def test_prefill_uses_latest_approved_report_for_same_project() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        older_report = create_report(
            session,
            account_id,
            project_id,
            prepared_by,
            reporting_week=date(2025, 6, 16),
            model_setup={"piName": "PI 2"},
            calculated_metrics={"completedToDateStoryPoints": 24},
        )
        latest_report = create_report(
            session,
            account_id,
            project_id,
            prepared_by,
            reporting_week=date(2025, 6, 23),
            model_setup={"piName": "PI 3", "plannedStoryPoints": 120},
            calculated_metrics={"completedToDateStoryPoints": 50},
        )
        add_approved_content(
            session,
            older_report,
            prepared_by,
            {"executiveSummary": "Older approved customer summary."},
        )
        add_approved_content(
            session,
            latest_report,
            prepared_by,
            {
                "executiveSummary": "Latest approved customer summary.",
                "deliveryProgress": "Delivery progressed with controlled dependency risk.",
            },
        )
        add_risk(session, older_report, "Older risk should not be copied.")
        active_risk = add_risk(session, latest_report, "Latest risk should be copied.")
        add_risk(session, latest_report, "Closed risk should not be copied.", RiskStatus.CLOSED)
        session.commit()

        prefill = WsrDraftService(session).get_prefill(account_id, project_id)

    assert prefill.has_approved_history is True
    assert prefill.source_wsr_id == latest_report.id
    assert prefill.delivery_model == DeliveryModel.PI
    assert prefill.model_setup == {"piName": "PI 3", "plannedStoryPoints": 120}
    assert prefill.previous_customer_context == {
        "executiveSummary": "Latest approved customer summary.",
        "deliveryProgress": "Delivery progressed with controlled dependency risk.",
    }
    assert prefill.prior_pi_completed_story_points == 50
    assert [risk.source_risk_id for risk in prefill.carry_forward_risks] == [active_risk.id]
    assert [risk.description for risk in prefill.carry_forward_risks] == [
        "Latest risk should be copied."
    ]


def test_prefill_is_scoped_to_account_and_project() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        original_report = create_report(
            session,
            account_id,
            project_id,
            prepared_by,
            reporting_week=date(2025, 6, 16),
            model_setup={"piName": "Original PI"},
        )
        other_project = Project(account_id=account_id, name="Other Project", status="ACTIVE")
        session.add(other_project)
        session.flush()
        other_report = create_report(
            session,
            account_id,
            other_project.id,
            prepared_by,
            reporting_week=date(2025, 6, 30),
            model_setup={"piName": "Wrong Project PI"},
        )
        add_approved_content(
            session,
            original_report,
            prepared_by,
            {"executiveSummary": "Original project customer summary."},
        )
        add_approved_content(
            session,
            other_report,
            prepared_by,
            {"executiveSummary": "Other project customer summary."},
        )
        session.commit()

        prefill = WsrDraftService(session).get_prefill(account_id, project_id)

    assert prefill.source_wsr_id == original_report.id
    assert prefill.model_setup == {"piName": "Original PI"}
    assert prefill.previous_customer_context["executiveSummary"] == (
        "Original project customer summary."
    )


def test_prefill_excludes_pm_only_and_internal_content() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        report = create_report(
            session,
            account_id,
            project_id,
            prepared_by,
            reporting_week=date(2025, 6, 23),
        )
        add_approved_content(
            session,
            report,
            prepared_by,
            {
                "executiveSummary": "Customer-ready summary.",
                "pmQualityInsights": "PM-only suggestion must stay private.",
                "statusDiscrepancyEvidence": "Internal discrepancy evidence.",
                "retrievalEvidence": "Internal retrieval evidence.",
                "aiInsights": ["Not customer-facing."],
            },
        )
        session.commit()

        prefill = WsrDraftService(session).get_prefill(account_id, project_id)

    assert prefill.previous_customer_context == {
        "executiveSummary": "Customer-ready summary."
    }


def test_prefill_returns_empty_when_no_approved_history_exists() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        create_report(
            session,
            account_id,
            project_id,
            prepared_by,
            reporting_week=date(2025, 6, 23),
            lifecycle_status=WsrLifecycleStatus.DRAFT,
        )
        session.commit()

        prefill = WsrDraftService(session).get_prefill(account_id, project_id)

    assert prefill.has_approved_history is False
    assert prefill.source_wsr_id is None
    assert prefill.delivery_model is None
    assert prefill.model_setup == {}
    assert prefill.previous_customer_context == {}
    assert prefill.prior_pi_completed_story_points is None
    assert prefill.carry_forward_risks == []
