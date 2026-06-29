"""Create core WSR schema.

Revision ID: 0001_create_core_schema
Revises:
Create Date: 2026-06-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001_create_core_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

UUID_TYPE = sa.Uuid()


def id_column() -> sa.Column:
    return sa.Column("id", UUID_TYPE, primary_key=True)


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    ]


def fk_column(name: str, target: str, nullable: bool = False) -> sa.Column:
    return sa.Column(name, UUID_TYPE, sa.ForeignKey(target, ondelete="RESTRICT"), nullable=nullable)


def upgrade() -> None:
    op.create_table(
        "users",
        id_column(),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        *timestamps(),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_table(
        "accounts",
        id_column(),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        *timestamps(),
    )
    op.create_table(
        "projects",
        id_column(),
        fk_column("account_id", "accounts.id"),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        *timestamps(),
    )
    op.create_index("ix_projects_account_id_id", "projects", ["account_id", "id"])
    op.create_table(
        "project_assignments",
        id_column(),
        fk_column("user_id", "users.id"),
        fk_column("project_id", "projects.id"),
        sa.Column("role", sa.Text(), nullable=False),
        *timestamps(),
        sa.UniqueConstraint("user_id", "project_id", name="uq_project_assignments_user_project"),
    )
    op.create_table(
        "delivery_model_configs",
        id_column(),
        fk_column("project_id", "projects.id"),
        fk_column("updated_by", "users.id"),
        sa.Column("delivery_model", sa.Text(), nullable=False),
        sa.Column("config", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "wsr_reports",
        id_column(),
        fk_column("account_id", "accounts.id"),
        fk_column("project_id", "projects.id"),
        fk_column("prepared_by", "users.id"),
        sa.Column("lifecycle_status", sa.Text(), nullable=False),
        sa.Column("generation_status", sa.Text(), nullable=False),
        sa.Column("reporting_week", sa.Date(), nullable=False),
        sa.Column("delivery_model", sa.Text(), nullable=False),
        sa.Column("schema_version", sa.Text(), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("entered_data_snapshot", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("model_setup_snapshot", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("weekly_progress_snapshot", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("calculated_metrics_snapshot", sa.JSON(), nullable=False, server_default="{}"),
        *timestamps(),
        sa.UniqueConstraint(
            "account_id",
            "project_id",
            "reporting_week",
            "version_number",
            name="uq_wsr_reports_account_project_week_version",
        ),
    )
    op.create_table(
        "wsr_risks",
        id_column(),
        fk_column("account_id", "accounts.id"),
        fk_column("project_id", "projects.id"),
        fk_column("wsr_report_id", "wsr_reports.id"),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("owner_contact", sa.Text(), nullable=False),
        sa.Column("mitigation", sa.Text(), nullable=False),
        sa.Column("planned_closure_date", sa.Date(), nullable=False),
        sa.Column("closure_remark", sa.Text(), nullable=True),
        sa.Column("source_risk_id", UUID_TYPE, nullable=True),
        *timestamps(),
    )
    op.create_index(
        "ix_wsr_risks_report_status_severity_closure",
        "wsr_risks",
        ["wsr_report_id", "status", "severity", "planned_closure_date"],
    )
    op.create_table(
        "workflow_runs",
        id_column(),
        fk_column("account_id", "accounts.id"),
        fk_column("project_id", "projects.id"),
        fk_column("wsr_report_id", "wsr_reports.id"),
        fk_column("requested_by", "users.id"),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("checkpoint_id", sa.Text(), nullable=True),
        sa.Column("retrieval_metadata", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("workflow_error_summary", sa.JSON(), nullable=False, server_default="[]"),
        *timestamps(),
    )
    op.create_table(
        "workflow_checkpoints",
        id_column(),
        fk_column("workflow_run_id", "workflow_runs.id"),
        sa.Column("checkpoint_name", sa.Text(), nullable=False),
        sa.Column("state_payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "ai_drafts",
        id_column(),
        fk_column("account_id", "accounts.id"),
        fk_column("project_id", "projects.id"),
        fk_column("wsr_report_id", "wsr_reports.id"),
        fk_column("workflow_run_id", "workflow_runs.id"),
        sa.Column("draft_sections", sa.JSON(), nullable=False),
        sa.Column("qa_warnings", sa.JSON(), nullable=False, server_default="[]"),
        *timestamps(),
    )
    op.create_table(
        "wsr_content_versions",
        id_column(),
        fk_column("account_id", "accounts.id"),
        fk_column("project_id", "projects.id"),
        fk_column("wsr_report_id", "wsr_reports.id"),
        fk_column("source_ai_draft_id", "ai_drafts.id", nullable=True),
        fk_column("edited_by", "users.id"),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("content_sections", sa.JSON(), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "wsr_report_id",
            "version_number",
            name="uq_wsr_content_versions_report_version",
        ),
    )
    op.create_index(
        "uq_wsr_content_versions_one_approved",
        "wsr_content_versions",
        ["wsr_report_id"],
        unique=True,
        sqlite_where=sa.text("status = 'APPROVED'"),
        postgresql_where=sa.text("status = 'APPROVED'"),
    )
    op.create_table(
        "ai_insights",
        id_column(),
        fk_column("account_id", "accounts.id"),
        fk_column("project_id", "projects.id"),
        fk_column("wsr_report_id", "wsr_reports.id"),
        fk_column("workflow_run_id", "workflow_runs.id"),
        sa.Column("type", sa.Text(), nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("severity", sa.Text(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("recommendation", sa.Text(), nullable=False),
        sa.Column("suggested_edit", sa.Text(), nullable=True),
        sa.Column("target_field", sa.Text(), nullable=True),
        *timestamps(),
    )
    op.create_table(
        "approval_events",
        id_column(),
        fk_column("account_id", "accounts.id"),
        fk_column("project_id", "projects.id"),
        fk_column("wsr_report_id", "wsr_reports.id"),
        fk_column("content_version_id", "wsr_content_versions.id"),
        fk_column("actor_id", "users.id"),
        sa.Column("decision", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "export_attempts",
        id_column(),
        fk_column("account_id", "accounts.id"),
        fk_column("project_id", "projects.id"),
        fk_column("wsr_report_id", "wsr_reports.id"),
        fk_column("content_version_id", "wsr_content_versions.id"),
        fk_column("requested_by", "users.id"),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("object_key", sa.Text(), nullable=True),
        sa.Column("error_code", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "audit_logs",
        id_column(),
        fk_column("actor_id", "users.id", nullable=True),
        fk_column("account_id", "accounts.id", nullable=True),
        fk_column("project_id", "projects.id", nullable=True),
        fk_column("wsr_report_id", "wsr_reports.id", nullable=True),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("field_path", sa.Text(), nullable=True),
        sa.Column("before_value", sa.JSON(), nullable=True),
        sa.Column("after_value", sa.JSON(), nullable=True),
        sa.Column("correlation_id", UUID_TYPE, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "admin_settings",
        id_column(),
        sa.Column("setting_key", sa.Text(), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        fk_column("updated_by", "users.id"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("setting_key", name="uq_admin_settings_setting_key"),
    )


def downgrade() -> None:
    for table_name in reversed(
        [
            "users",
            "accounts",
            "projects",
            "project_assignments",
            "delivery_model_configs",
            "wsr_reports",
            "wsr_risks",
            "workflow_runs",
            "workflow_checkpoints",
            "ai_drafts",
            "wsr_content_versions",
            "ai_insights",
            "approval_events",
            "export_attempts",
            "audit_logs",
            "admin_settings",
        ]
    ):
        op.drop_table(table_name)
