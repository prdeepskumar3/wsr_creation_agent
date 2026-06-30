from datetime import date
from uuid import uuid4

from domain.wsr_drafts.validation import WsrDraftValidator
from wsr_shared.dtos import WsrDraftSaveRequestDTO


def sprint_validation_payload() -> WsrDraftSaveRequestDTO:
    return WsrDraftSaveRequestDTO(
        account_id=uuid4(),
        project_id=uuid4(),
        prepared_by=uuid4(),
        reporting_week=date(2025, 6, 23),
        delivery_model="SPRINT",
        model_setup={
            "sprintName": "Sprint 14",
            "startDate": "2025-06-23",
            "endDate": "2025-07-04",
            "plannedStories": 20,
            "plannedStoryPoints": 80,
            "plannedEffortHours": 160,
            "dorPercent": 85,
        },
        weekly_progress={
            "progressUpdate": "Sprint progress is tracking with manageable delivery risk.",
            "storiesCompleted": 10,
            "storyPointsCompleted": 40,
            "effortBurnedHours": 80,
            "unplannedStories": 0,
            "unplannedStoryPoints": 0,
            "ragStatus": "AMBER",
            "nextWeekPlan": "Complete remaining API validation and planned stories.",
            "remarks": "",
        },
        overview="Portal revamp sprint delivery remains on track with manageable risk.",
        key_achievements=(
            "- Completed authentication service baseline\n"
            "- Validated API integration test interface\n"
            "- Resolved sprint planning dependency"
        ),
        next_week_focus=(
            "- Complete vendor API validation; Owner: Priya; Target: Tue\n"
            "- Finish dashboard contract review; Owner: Arjun; Target: Wed\n"
            "- Prepare sprint closure notes; Owner: Neha; Target: Fri"
        ),
    )


def pi_validation_payload() -> WsrDraftSaveRequestDTO:
    return WsrDraftSaveRequestDTO(
        account_id=uuid4(),
        project_id=uuid4(),
        prepared_by=uuid4(),
        reporting_week=date(2025, 6, 23),
        delivery_model="PI",
        model_setup={
            "piName": "PI 3",
            "piStartDate": "2025-06-01",
            "piEndDate": "2025-08-31",
            "totalSprints": 5,
            "currentSprint": 2,
            "plannedStoryPoints": 100,
            "completedToDateStoryPoints": 30,
        },
        weekly_progress={
            "progressUpdate": "PI progress is moving through planned scope with dependency focus.",
            "storyPointsCompletedThisWeek": 20,
            "featuresCompletedThisWeek": 2,
            "delayedScopeItems": 0,
            "blockersDependenciesCount": 1,
            "ragStatus": "AMBER",
            "nextWeekPlan": "Close dependency and continue planned PI scope.",
            "remarks": "",
        },
        overview="PI delivery is progressing with controlled dependency management.",
        key_achievements=(
            "- Completed authentication feature baseline\n"
            "- Advanced dashboard API objective\n"
            "- Reduced integration dependency risk"
        ),
        next_week_focus=(
            "- Close vendor clarification; Owner: Priya; Target: Tue\n"
            "- Complete PI objective review; Owner: Arjun; Target: Thu\n"
            "- Confirm dependency burn-down; Owner: Neha; Target: Fri"
        ),
    )


def test_sprint_validation_returns_calculated_story_point_and_effort_metrics() -> None:
    result = WsrDraftValidator().validate(sprint_validation_payload())

    assert result.is_valid is True
    assert result.calculated_metrics == {
        "completionPercent": 50.0,
        "pointCompletionPercent": 50.0,
        "effortUsagePercent": 50.0,
    }


def test_sprint_validation_returns_field_error_when_completed_exceeds_planned() -> None:
    payload = sprint_validation_payload()
    payload.weekly_progress = {**payload.weekly_progress, "storiesCompleted": 21}

    result = WsrDraftValidator().validate(payload)

    assert result.is_valid is False
    assert result.errors[0].field == "storiesCompleted"
    assert result.errors[0].code == "EXCEEDS_PLANNED_STORIES"


def test_pi_validation_returns_calculated_velocity_metrics() -> None:
    result = WsrDraftValidator().validate(pi_validation_payload())

    assert result.is_valid is True
    assert result.calculated_metrics == {
        "completedToDateStoryPoints": 50,
        "completionPercent": 50.0,
        "remainingStoryPoints": 50,
        "requiredVelocity": 16.67,
        "averageVelocity": 25.0,
        "confidence": "HIGH",
    }


def test_pi_validation_rejects_current_sprint_greater_than_total_sprints() -> None:
    payload = pi_validation_payload()
    payload.weekly_progress = {**payload.weekly_progress, "currentSprint": 6}

    result = WsrDraftValidator().validate(payload)

    assert result.is_valid is False
    assert any(
        error.field == "currentSprint" and error.code == "CURRENT_SPRINT_EXCEEDS_TOTAL"
        for error in result.errors
    )


def test_validation_requires_remarks_when_rag_conflicts_with_metrics() -> None:
    payload = sprint_validation_payload()
    payload.weekly_progress = {
        **payload.weekly_progress,
        "storiesCompleted": 19,
        "storyPointsCompleted": 76,
        "ragStatus": "RED",
        "remarks": "",
    }

    result = WsrDraftValidator().validate(payload)

    assert result.is_valid is False
    assert any(
        error.field == "remarks" and error.code == "RAG_REMARKS_REQUIRED"
        for error in result.errors
    )


def test_validation_maps_missing_required_fields_to_field_level_errors() -> None:
    payload = sprint_validation_payload()
    payload.weekly_progress = {**payload.weekly_progress, "progressUpdate": ""}

    result = WsrDraftValidator().validate(payload)

    assert result.is_valid is False
    assert any(
        error.field == "progressUpdate" and error.code == "REQUIRED"
        for error in result.errors
    )


def test_validation_requires_project_overview_before_generation() -> None:
    payload = sprint_validation_payload()
    payload.overview = " "

    result = WsrDraftValidator().validate(payload)

    assert result.is_valid is False
    assert any(
        error.field == "overview" and error.code == "REQUIRED"
        for error in result.errors
    )


def test_validation_requires_at_least_three_achievements() -> None:
    payload = sprint_validation_payload()
    payload.key_achievements = "Completed authentication module\nValidated API interface"

    result = WsrDraftValidator().validate(payload)

    assert result.is_valid is False
    assert any(
        error.field == "keyAchievements" and error.code == "MIN_ACHIEVEMENTS_REQUIRED"
        for error in result.errors
    )


def test_validation_requires_at_least_three_next_week_plan_items() -> None:
    payload = sprint_validation_payload()
    payload.next_week_focus = "Complete integration validation; Prepare sprint demo"

    result = WsrDraftValidator().validate(payload)

    assert result.is_valid is False
    assert any(
        error.field == "nextWeekFocus"
        and error.code == "MIN_NEXT_WEEK_PLAN_ITEMS_REQUIRED"
        for error in result.errors
    )


def test_validation_accepts_plan_items_with_owner_and_target_timing() -> None:
    payload = sprint_validation_payload()
    payload.next_week_focus = (
        "1. Complete integration validation - Owner: Priya - Target: Tuesday\n"
        "2. Review dashboard API contract - Owner: Arjun - Target: Wednesday\n"
        "3. Prepare customer status narrative - Owner: Neha - Target: Friday"
    )

    result = WsrDraftValidator().validate(payload)

    assert result.is_valid is True
