from pathlib import Path

import pytest

from depcheckr.helpers import (
    classify_update,
    get_dependency_group,
    load_pyproject,
    parse_dependency,
)


@pytest.fixture(scope="module")
def pyproject_data():
    path = Path("pyproject.toml")
    return load_pyproject(path)


def test_parse_dependency():
    result = parse_dependency("httpx>=0.28.0")
    assert result["name"] == "httpx"
    assert result["version"] == ">=0.28.0" or result["version"] == "0.28.0"


def test_classify_update():
    assert classify_update("1.0.0", "1.0.0") == "up-to-date"
    assert classify_update("1.0.0", "2.0.0") == "major"
    assert classify_update("1.0.0", "1.1.0") == "minor"
    assert classify_update("1.0.0", "1.0.1") == "patch"
    assert classify_update(None, "1.0.0") == "unknown"
    assert classify_update("1.0.0", "-") == "unknown"


def test_get_dependency_group_project_from_file(pyproject_data):
    deps = get_dependency_group(pyproject_data, "project")
    assert "httpx" in deps
    assert deps["httpx"].startswith("httpx")


def test_get_dependency_group_dev_from_file(pyproject_data):
    deps = get_dependency_group(pyproject_data, "dev")
    assert "pytest" in deps or "mypy" in deps


def test_get_dependency_group_invalid():
    with pytest.raises(ValueError):
        get_dependency_group({}, "invalid")


def test_load_pyproject(tmp_path):
    content = """
    [project]
    dependencies = ["httpx>=0.28.0", "pytest"]

    [tool.uv]
    dev-dependencies = { rich = ">=13.0.0" }
    """
    file = tmp_path / "pyproject.toml"
    file.write_text(content)
    data = load_pyproject(file)

    assert "project" in data
    assert "dependencies" in data["project"]
    assert data["project"]["dependencies"] == ["httpx>=0.28.0", "pytest"]


def test_get_dependency_group_project():
    data = {"project": {"dependencies": ["httpx>=0.28.0", "pytest"]}}
    deps = get_dependency_group(data, "project")
    assert deps["httpx"] == "httpx>=0.28.0"
    assert deps["pytest"] == "pytest"


def test_get_dependency_group_dev():
    data = {"tool": {"uv": {"dev-dependencies": {"rich": ">=13.0.0"}}}}
    deps = get_dependency_group(data, "dev")
    assert deps["rich"] == "rich>=13.0.0"
