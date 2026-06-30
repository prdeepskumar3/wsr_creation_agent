"""Deterministic PM quality insight signal generation."""

from datetime import date
from typing import Any


def generate_quality_insights(draft: dict[str, Any], today: date) -> list[dict[str, object]]:
    """Generate actionable PM-only insights from saved WSR facts."""
    insights: list[dict[str, object]] = []
    metrics = draft.get("calculatedMetrics", {})
    progress = draft.get("weeklyProgress", {})
    risks = draft.get("risks", [])
    entered_data = draft.get("enteredData", {})

    rag_status = str(progress.get("ragStatus", "")).upper()
    completion = _number(metrics.get("completionPercent"))
    if rag_status == "GREEN" and completion is not None and completion < 70:
        insights.append(
            _insight(
                "DISCREPANCY",
                "HIGH",
                "Green status conflicts with completion below 70%.",
                {"completionPercent": completion, "ragStatus": rag_status},
                "Review RAG status or add clear recovery evidence.",
                "Use Amber unless recovery evidence supports Green.",
            )
        )

    active_high_risks = [
        risk
        for risk in risks
        if risk.get("severity") == "HIGH" and risk.get("status") in {"OPEN", "IN_PROGRESS"}
    ]
    if rag_status == "GREEN" and active_high_risks:
        insights.append(
            _insight(
                "DISCREPANCY",
                "HIGH",
                "Green status conflicts with active high-severity risks.",
                {"activeHighRiskCount": len(active_high_risks)},
                "Explain why high risks do not affect customer-facing status.",
                "Keep Green only with explicit mitigation confidence.",
            )
        )

    planned_points = _number(draft.get("modelSetup", {}).get("plannedStoryPoints"))
    spillover_points = _number(progress.get("unplannedStoryPoints"))
    if rag_status == "GREEN" and planned_points and spillover_points:
        spillover_percent = (spillover_points / planned_points) * 100
        if spillover_percent > 20:
            insights.append(
                _insight(
                    "DISCREPANCY",
                    "MEDIUM",
                    "Green status has spillover above 20%.",
                    {"spilloverPercent": round(spillover_percent, 2)},
                    "Call out scope movement and mitigation.",
                    "Add scope-control narrative for spillover.",
                )
            )

    for risk in risks:
        closure_date = _date_from_string(risk.get("plannedClosureDate"))
        mitigation = str(risk.get("mitigation", ""))
        if closure_date is not None and closure_date < today and risk.get("status") != "CLOSED":
            insights.append(
                _insight(
                    "RISK",
                    "HIGH",
                    "Open risk is past planned closure date.",
                    {"risk": risk.get("description"), "plannedClosureDate": str(closure_date)},
                    "Update closure date or close the risk with remarks.",
                    "Add current mitigation owner and closure date.",
                )
            )
        if risk.get("status") != "CLOSED" and len(mitigation.strip()) < 20:
            insights.append(
                _insight(
                    "RISK",
                    "MEDIUM",
                    "Risk mitigation is too weak for stakeholder review.",
                    {"risk": risk.get("description")},
                    "Describe concrete mitigation, owner, and timing.",
                    "Replace vague mitigation with a specific action.",
                )
            )

    achievements = str(entered_data.get("keyAchievements", ""))
    next_week_focus = str(entered_data.get("nextWeekFocus", ""))
    progress_update = str(progress.get("progressUpdate", ""))
    if achievements and not any(char.isdigit() for char in achievements):
        insights.append(
            _insight(
                "QUALITY",
                "MEDIUM",
                "Achievements do not include measurable impact.",
                {"field": "keyAchievements"},
                "Add numbers, milestones, or customer-visible outcomes.",
                "Add measurable impact to each achievement.",
            )
        )
    if len(progress_update.split()) < 8:
        insights.append(
            _insight(
                "QUALITY",
                "MEDIUM",
                "Progress update is too vague for enterprise reporting.",
                {"field": "progressUpdate"},
                "Include completed work, impact, and constraint.",
                "Expand the progress update with business context.",
            )
        )
    has_owner_and_target = all(
        token in next_week_focus.lower() for token in ["owner", "target"]
    )
    if next_week_focus and not has_owner_and_target:
        insights.append(
            _insight(
                "QUALITY",
                "MEDIUM",
                "Next-week plan lacks owner or target timing.",
                {"field": "nextWeekFocus"},
                "Add owner and target date for each action.",
                "Rewrite next-week plan as action, owner, and target date.",
            )
        )

    customer_sensitive_text = " ".join(
        [
            achievements,
            next_week_focus,
            str(entered_data.get("remarks", "")),
            progress_update,
        ]
    ).lower()
    if any(term in customer_sensitive_text for term in ["workaround", "internal", "blame"]):
        insights.append(
            _insight(
                "CUSTOMER_SAFETY",
                "MEDIUM",
                "Customer-facing language contains internal or sensitive wording.",
                {"terms": ["workaround", "internal", "blame"]},
                "Use neutral customer-safe delivery language.",
                "Replace internal wording with mitigation-focused language.",
            )
        )
    return insights


def _insight(
    insight_type: str,
    severity: str,
    description: str,
    evidence: dict[str, object],
    recommendation: str,
    suggested_edit: str,
) -> dict[str, object]:
    """Build the complete PM insight schema required by Phase 6."""
    return {
        "type": insight_type,
        "severity": severity,
        "description": description,
        "evidence": [evidence],
        "recommendation": recommendation,
        "suggestedEdit": suggested_edit,
    }


def _number(value: object) -> float | None:
    """Return numeric values from JSON-like draft snapshots."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    return None


def _date_from_string(value: object) -> date | None:
    """Parse ISO date strings used by risk rows."""
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None
