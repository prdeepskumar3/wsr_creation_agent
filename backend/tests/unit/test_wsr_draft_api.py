from datetime import date
from uuid import UUID, uuid4

from api.v1.router import api_v1_router
from app.create_app import create_app
from db.base import Base
from db.models import Account, Project, ProjectAssignment, User, WorkflowRun
from fastapi.routing import APIRoute
from services.wsr_draft_service import DraftAuthorizationError, WsrDraftService
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from wsr_shared.dtos import WsrDraftSaveRequestDTO


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


def sprint_payload(
    account_id: UUID,
    project_id: UUID,
    prepared_by: UUID,
) -> WsrDraftSaveRequestDTO:
    return WsrDraftSaveRequestDTO(
        account_id=account_id,
        project_id=project_id,
        prepared_by=prepared_by,
        reporting_week=date(2025, 6, 23),
        delivery_model="SPRINT",
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
            "progressUpdate": "Authentication completed and API integration progressed.",
            "storiesCompleted": 12,
            "storyPointsCompleted": 48,
            "effortBurnedHours": 96,
            "unplannedStories": 2,
            "unplannedStoryPoints": 6,
            "ragStatus": "AMBER",
            "nextWeekPlan": "Complete API validation after vendor clarification.",
            "remarks": "Delivery remains manageable.",
        },
        risks=[
            {
                "description": "API documentation dependency may delay validation.",
                "severity": "HIGH",
                "status": "IN_PROGRESS",
                "ownerContact": "Priya Rao",
                "mitigation": "Parallel test interface active.",
                "plannedClosureDate": "2025-06-30",
                "closureRemark": None,
            }
        ],
        overview="Sprint delivery overview for the customer-ready weekly status report.",
        key_achievements=(
            "- Authentication module completed\n"
            "- API integration baseline established\n"
            "- Sprint dependency mitigation confirmed"
        ),
        next_week_focus=(
            "- Complete integration validation; Owner: Priya; Target: Tuesday\n"
            "- Review dashboard API contract; Owner: Arjun; Target: Wednesday\n"
            "- Prepare sprint closure note; Owner: Neha; Target: Friday"
        ),
        remarks="Customer-safe PM remark",
    )


def test_save_wsr_draft_persists_full_state_and_calculated_metrics() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        response = WsrDraftService(session).save_draft(
            sprint_payload(account_id, project_id, prepared_by)
        )

    assert response.generation_status == "NOT_STARTED"
    assert response.lifecycle_status == "DRAFT"
    assert response.entered_data_snapshot["overview"] == (
        "Sprint delivery overview for the customer-ready weekly status report."
    )
    assert response.model_setup_snapshot["plannedStoryPoints"] == 70
    assert response.weekly_progress_snapshot["storyPointsCompleted"] == 48
    assert response.calculated_metrics_snapshot == {
        "completionPercent": 66.67,
        "pointCompletionPercent": 68.57,
        "effortUsagePercent": 60.0,
    }
    assert response.risks[0].owner_contact == "Priya Rao"


def test_restore_wsr_draft_returns_saved_form_state() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        service = WsrDraftService(session)
        save_response = service.save_draft(sprint_payload(account_id, project_id, prepared_by))
        restore_response = service.get_draft(save_response.wsr_id, prepared_by)

    assert restore_response == save_response


def test_save_wsr_draft_does_not_enqueue_generation() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        WsrDraftService(session).save_draft(sprint_payload(account_id, project_id, prepared_by))
        workflow_runs = session.scalars(select(WorkflowRun)).all()

    assert workflow_runs == []


def test_save_wsr_draft_rejects_unauthorized_project_access() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, _prepared_by = seed_authorized_project(session)
        payload = sprint_payload(account_id, project_id, uuid4())

        try:
            WsrDraftService(session).save_draft(payload)
        except DraftAuthorizationError as exc:
            assert str(exc) == "User is not authorized for this account/project."
        else:
            raise AssertionError("Expected DraftAuthorizationError.")


def test_restore_wsr_draft_rejects_unauthorized_project_access() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        save_response = WsrDraftService(session).save_draft(
            sprint_payload(account_id, project_id, prepared_by)
        )

        try:
            WsrDraftService(session).get_draft(save_response.wsr_id, uuid4())
        except DraftAuthorizationError as exc:
            assert str(exc) == "User is not authorized for this account/project."
        else:
            raise AssertionError("Expected DraftAuthorizationError.")


def test_save_wsr_draft_updates_existing_weekly_draft() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        service = WsrDraftService(session)
        first_response = service.save_draft(sprint_payload(account_id, project_id, prepared_by))
        payload = sprint_payload(account_id, project_id, prepared_by)
        payload.weekly_progress = {**payload.weekly_progress, "storiesCompleted": 15}
        second_response = service.save_draft(payload)

    assert second_response.wsr_id == first_response.wsr_id
    assert second_response.calculated_metrics_snapshot["completionPercent"] == 83.33


def test_save_wsr_draft_calculates_numeric_string_values_from_ui_inputs() -> None:
    session_factory = create_test_session_factory()
    with session_factory() as session:
        account_id, project_id, prepared_by = seed_authorized_project(session)
        payload = sprint_payload(account_id, project_id, prepared_by)
        payload.model_setup = {
            **payload.model_setup,
            "plannedStories": "18",
            "plannedStoryPoints": "70",
            "plannedEffortHours": "160",
        }
        payload.weekly_progress = {
            **payload.weekly_progress,
            "storiesCompleted": "12",
            "storyPointsCompleted": "48",
            "effortBurnedHours": "96",
        }

        response = WsrDraftService(session).save_draft(payload)

    assert response.calculated_metrics_snapshot == {
        "completionPercent": 66.67,
        "pointCompletionPercent": 68.57,
        "effortUsagePercent": 60.0,
    }


def test_wsr_draft_routes_are_registered() -> None:
    registered_paths = collect_api_paths(create_app().routes)
    registered_paths |= collect_api_paths(api_v1_router.routes, "/api/v1")

    assert "/api/v1/wsr-drafts" in registered_paths
    assert "/api/v1/wsr-drafts/validate" in registered_paths
    assert "/api/v1/wsr-drafts/carry-forward-risks" in registered_paths
    assert "/api/v1/wsr-drafts/{wsr_id}" in registered_paths
