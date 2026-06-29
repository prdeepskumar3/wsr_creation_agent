import tomllib
from pathlib import Path


def test_root_uv_workspace_declares_python_members() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text())

    assert pyproject["tool"]["uv"]["workspace"]["members"] == ["backend", "agent", "shared"]


def test_shared_package_imports() -> None:
    import wsr_shared

    assert wsr_shared.__version__ == "0.1.0"
