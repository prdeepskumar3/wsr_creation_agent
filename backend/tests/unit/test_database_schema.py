from pathlib import Path

from alembic import command
from alembic.config import Config
from db.models import Base, WsrContentVersion
from sqlalchemy import create_engine, inspect
from sqlalchemy.sql.sqltypes import Uuid

EXPECTED_TABLES = {
    "accounts",
    "admin_settings",
    "ai_drafts",
    "ai_insights",
    "approval_events",
    "audit_logs",
    "delivery_model_configs",
    "export_attempts",
    "project_assignments",
    "projects",
    "users",
    "workflow_checkpoints",
    "workflow_runs",
    "wsr_content_versions",
    "wsr_reports",
    "wsr_risks",
}


def test_sqlalchemy_models_create_core_tables() -> None:
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    assert set(inspect(engine).get_table_names()) == EXPECTED_TABLES


def test_alembic_migration_creates_core_tables(tmp_path: Path) -> None:
    database_path = tmp_path / "migration-smoke.db"
    config = Config("backend/alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite:///{database_path}")

    command.upgrade(config, "head")

    engine = create_engine(f"sqlite:///{database_path}")
    assert set(inspect(engine).get_table_names()) == EXPECTED_TABLES | {"alembic_version"}


def test_content_version_links_to_approval_and_export_events() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    inspector = inspect(engine)

    approval_fks = {
        fk["constrained_columns"][0]: fk["referred_table"]
        for fk in inspector.get_foreign_keys("approval_events")
    }
    export_fks = {
        fk["constrained_columns"][0]: fk["referred_table"]
        for fk in inspector.get_foreign_keys("export_attempts")
    }

    assert approval_fks["content_version_id"] == "wsr_content_versions"
    assert export_fks["content_version_id"] == "wsr_content_versions"


def test_content_version_has_uuid_id_and_unique_report_version() -> None:
    constraints = {
        constraint.name
        for constraint in WsrContentVersion.__table__.constraints
        if constraint.name is not None
    }

    assert isinstance(WsrContentVersion.__table__.c.id.type, Uuid)
    assert "uq_wsr_content_versions_report_version" in constraints


def test_restrictive_foreign_keys_for_approved_history() -> None:
    for table_name in ["approval_events", "export_attempts"]:
        for foreign_key in Base.metadata.tables[table_name].foreign_keys:
            assert foreign_key.ondelete == "RESTRICT"
