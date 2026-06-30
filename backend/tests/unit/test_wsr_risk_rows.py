from datetime import date
from uuid import UUID, uuid4

from db.base import Base
from db.models import Account, Project, ProjectAssignment, User, WsrReport, WsrRisk
from domain.wsr_drafts.validation import ExistingProjectRisk, WsrDraftValidator
from services.wsr_draft_service import WsrDraftService
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from wsr_shared.dtos import RiskInputDTO, WsrDraftSaveRequestDTO
from wsr_shared.enums import DeliveryModel, RiskSeverity, RiskStatus


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


def valid_risk(description: str = "Vendor API dependency may delay validation.") -> RiskInputDTO:
    return RiskInputDTO(
        description=description,
        severity=RiskSeverity.HIGH,
        status=RiskStatus.IN_PROGRESS,
        owner_contact="Priya Rao",
        mitigation="Parallel validation interface is active.",
        planned_closure_date=date(2025, 6, 30),
    )


def draft_payload_with_risks(risks: list[RiskInputDTO]) -> WsrDraftSaveRequestDTO:
    return WsrDraftSaveRequestDTO(
        account_id=UUID("11111111-1111-1111-1111-111111111111"),
        project_id=UUID("22222222-2222-2222-2222-222222222222"),
        prepared_by=UUID("33333333-3333-3333-3333-333333333333"),
        reporting_week=date(2025, 6, 23),
        delivery_model=DeliveryModel.SPRINT,
        model_setup={
            "sprintName": "Sprint 14",
            "startDate": "2025-06-23",
            "endDate": "2025-07-04",
            "plannedStories": 18,
            "plannedStoryPoints": 70,
            "plannedEffortHours": 160,
            "dorPercent": 85,
        },
        weekly_progress={
            "progressUpdate": "Sprint progress is controlled with manageable delivery risk.",
            "storiesCompleted": 12,
            "storyPointsCompleted": 48,
            "effortBurnedHours": 96,
            "ragStatus": "AMBER",
            "nextWeekPlan": "Complete integration validation and dependency closure.",
            "remarks": "Delivery remains manageable.",
        },
        risks=risks,
    )


def test_active_risk_requires_owner_and_mitigation() -> None:
    incomplete_risk = RiskInputDTO.model_construct(
        description="Vendor API dependency may delay validation.",
        severity=RiskSeverity.HIGH,
        status=RiskStatus.OPEN,
        owner_contact="",
        mitigation="",
        planned_closure_date=date(2025, 6, 30),
        closure_remark=None,
    )

    result = WsrDraftValidator().validate(draft_payload_with_risks([incomplete_risk]))

    assert result.is_valid is False
    assert {error.field for error in result.errors} >= {
        "risks[0].ownerContact",
        "risks[0].mitigation",
    }


def test_closed_risk_requires_closure_remark() -> None:
    closed_risk = RiskInputDTO.model_construct(
        description="Vendor API dependency may delay validation.",
        severity=RiskSeverity.HIGH,
        status=RiskStatus.CLOSED,
        owner_contact="Priya Rao",
        mitigation="Vendor clarification received and validated.",
        planned_closure_date=date(2025, 6, 30),
        closure_remark="",
    )

    result = WsrDraftValidator().validate(draft_payload_with_risks([closed_risk]))

    assert result.is_valid is False
    assert any(
        error.field == "risks[0].closureRemark"
        and error.code == "CLOSURE_REMARK_REQUIRED"
        for error in result.errors
    )


def test_duplicate_active_risk_descriptions_are_blocked() -> None:
    duplicate_description = "Vendor API dependency may delay validation."

    result = WsrDraftValidator().validate(
        draft_payload_with_risks(
            [
                valid_risk(duplicate_description),
                valid_risk(duplicate_description.upper()),
            ]
        )
    )

    assert result.is_valid is False
    assert any(error.code == "DUPLICATE_ACTIVE_RISK" for error in result.errors)


def test_duplicate_active_risk_description_is_blocked_for_same_project() -> None:
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
        add_risk(session, report, "Vendor API dependency may delay validation.")
        session.commit()
        payload = draft_payload_with_risks(
            [valid_risk("Vendor API dependency may delay validation.")]
        )
        payload.account_id = account_id
        payload.project_id = project_id
        payload.prepared_by = prepared_by

        result = WsrDraftService(session).validate_draft(payload)

    assert result.is_valid is False
    assert any(error.code == "DUPLICATE_ACTIVE_PROJECT_RISK" for error in result.errors)


def test_carry_forward_source_risk_is_not_blocked_as_duplicate() -> None:
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
        source_risk = add_risk(session, report, "Vendor API dependency may delay validation.")
        session.commit()
        carried_forward_risk = valid_risk("Vendor API dependency may delay validation.")
        carried_forward_risk.source_risk_id = source_risk.id
        payload = draft_payload_with_risks([carried_forward_risk])
        payload.account_id = account_id
        payload.project_id = project_id
        payload.prepared_by = prepared_by

        result = WsrDraftService(session).validate_draft(payload)

    assert result.is_valid is True


def test_open_risk_can_move_to_in_progress() -> None:
    source_risk_id = uuid4()
    carried_forward_risk = valid_risk("Vendor API dependency may delay validation.")
    carried_forward_risk.status = RiskStatus.IN_PROGRESS
    carried_forward_risk.source_risk_id = source_risk_id

    result = WsrDraftValidator().validate(
        draft_payload_with_risks([carried_forward_risk]),
        [
            ExistingProjectRisk(
                risk_id=source_risk_id,
                description=carried_forward_risk.description,
                status=RiskStatus.OPEN,
                planned_closure_date=date(2025, 7, 4),
            )
        ],
    )

    assert result.is_valid is True


def test_open_risk_cannot_close_directly() -> None:
    source_risk_id = uuid4()
    carried_forward_risk = valid_risk("Vendor API dependency may delay validation.")
    carried_forward_risk.status = RiskStatus.CLOSED
    carried_forward_risk.closure_remark = "Closed after vendor documentation arrived."
    carried_forward_risk.source_risk_id = source_risk_id

    result = WsrDraftValidator().validate(
        draft_payload_with_risks([carried_forward_risk]),
        [
            ExistingProjectRisk(
                risk_id=source_risk_id,
                description=carried_forward_risk.description,
                status=RiskStatus.OPEN,
                planned_closure_date=date(2025, 7, 4),
            )
        ],
    )

    assert result.is_valid is False
    assert any(
        error.field == "risks[0].status"
        and error.code == "OPEN_RISK_CANNOT_CLOSE_DIRECTLY"
        for error in result.errors
    )


def test_in_progress_risk_can_close_with_closure_remark() -> None:
    source_risk_id = uuid4()
    carried_forward_risk = valid_risk("Vendor API dependency may delay validation.")
    carried_forward_risk.status = RiskStatus.CLOSED
    carried_forward_risk.closure_remark = "Closed after vendor documentation arrived."
    carried_forward_risk.source_risk_id = source_risk_id

    result = WsrDraftValidator().validate(
        draft_payload_with_risks([carried_forward_risk]),
        [
            ExistingProjectRisk(
                risk_id=source_risk_id,
                description=carried_forward_risk.description,
                status=RiskStatus.IN_PROGRESS,
                planned_closure_date=date(2025, 7, 4),
            )
        ],
    )

    assert result.is_valid is True


def test_closed_risk_cannot_reopen() -> None:
    source_risk_id = uuid4()
    reopened_risk = valid_risk("Vendor API dependency may delay validation.")
    reopened_risk.status = RiskStatus.OPEN
    reopened_risk.source_risk_id = source_risk_id

    result = WsrDraftValidator().validate(
        draft_payload_with_risks([reopened_risk]),
        [
            ExistingProjectRisk(
                risk_id=source_risk_id,
                description=reopened_risk.description,
                status=RiskStatus.CLOSED,
                planned_closure_date=date(2025, 7, 4),
            )
        ],
    )

    assert result.is_valid is False
    assert any(
        error.field == "risks[0].status" and error.code == "CLOSED_RISK_CANNOT_REOPEN"
        for error in result.errors
    )


def test_closed_project_risk_cannot_reopen_through_service_validation() -> None:
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
        closed_source_risk = add_risk(
            session,
            report,
            "Vendor API dependency may delay validation.",
            status=RiskStatus.CLOSED,
        )
        session.commit()
        reopened_risk = valid_risk("Vendor API dependency may delay validation.")
        reopened_risk.status = RiskStatus.OPEN
        reopened_risk.source_risk_id = closed_source_risk.id
        payload = draft_payload_with_risks([reopened_risk])
        payload.account_id = account_id
        payload.project_id = project_id
        payload.prepared_by = prepared_by

        result = WsrDraftService(session).validate_draft(payload)

    assert result.is_valid is False
    assert any(error.code == "CLOSED_RISK_CANNOT_REOPEN" for error in result.errors)


def test_high_active_risk_requires_planned_closure_date() -> None:
    high_risk = RiskInputDTO.model_construct(
        description="Vendor API dependency may delay validation.",
        severity=RiskSeverity.HIGH,
        status=RiskStatus.OPEN,
        owner_contact="Priya Rao",
        mitigation="Parallel validation interface is active.",
        planned_closure_date=None,
        closure_remark=None,
    )

    result = WsrDraftValidator().validate(draft_payload_with_risks([high_risk]))

    assert result.is_valid is False
    assert any(
        error.field == "risks[0].plannedClosureDate" and error.code == "REQUIRED"
        for error in result.errors
    )


def test_overdue_active_risk_returns_warning_without_blocking_generation() -> None:
    overdue_risk = valid_risk("Vendor API dependency may delay validation.")
    overdue_risk.planned_closure_date = date(2025, 6, 1)

    result = WsrDraftValidator().validate(draft_payload_with_risks([overdue_risk]))

    assert result.is_valid is True
    assert any(
        warning.field == "risks[0].plannedClosureDate"
        and warning.code == "RISK_OVERDUE"
        for warning in result.warnings
    )


def test_carry_forward_returns_active_risks_from_latest_approved_same_project() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        older_report = create_report(
            session,
            account_id,
            project_id,
            prepared_by,
            reporting_week=date(2025, 6, 16),
        )
        latest_report = create_report(
            session,
            account_id,
            project_id,
            prepared_by,
            reporting_week=date(2025, 6, 23),
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
        )
        add_risk(session, older_report, "Older dependency should not carry forward.")
        add_risk(session, latest_report, "Latest open dependency should carry forward.")
        add_risk(
            session,
            latest_report,
            "Closed dependency should not carry forward.",
            status=RiskStatus.CLOSED,
        )
        add_risk(session, other_report, "Other project dependency should not carry forward.")
        session.commit()

        risks = WsrDraftService(session).list_carry_forward_risks(account_id, project_id)

    assert [risk.description for risk in risks] == ["Latest open dependency should carry forward."]


def create_report(
    session: Session,
    account_id: UUID,
    project_id: UUID,
    prepared_by: UUID,
    reporting_week: date,
) -> WsrReport:
    report = WsrReport(
        account_id=account_id,
        project_id=project_id,
        prepared_by=prepared_by,
        lifecycle_status="APPROVED",
        generation_status="COMPLETED",
        reporting_week=reporting_week,
        delivery_model="SPRINT",
        schema_version="wsr-draft.v1",
        version_number=1,
        entered_data_snapshot={},
        model_setup_snapshot={},
        weekly_progress_snapshot={},
        calculated_metrics_snapshot={},
    )
    session.add(report)
    session.flush()
    return report


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
        mitigation="Mitigation is tracked inside the WSR.",
        planned_closure_date=date(2025, 7, 4),
        closure_remark="Closed in prior report." if status == RiskStatus.CLOSED else None,
    )
    session.add(risk)
    session.flush()
    return risk
