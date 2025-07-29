import asyncio
import tomllib
from pathlib import Path
from typing import Any

import httpx
import tomli_w
from packaging.requirements import Requirement
from packaging.version import Version, parse


def parse_dependency(requirement: str) -> dict[str, Any]:
    parsed = Requirement(requirement)
    spec = next(iter(parsed.specifier), None)

    return {
        "name": parsed.name,
        "version": str(spec) if spec else None,
    }


def classify_update(specified: str | None, latest: str) -> str:
    if not specified or latest == "-":
        return "unknown"

    try:
        specified_version = parse(specified.lstrip("<>=!~^"))
        latest_version = parse(latest)
    except Exception:
        return "unknown"

    if specified_version == latest_version:
        return "up-to-date"
    if specified_version.major < latest_version.major:
        return "major"
    if specified_version.minor < latest_version.minor:
        return "minor"
    if specified_version.micro < latest_version.micro:
        return "patch"

    return "unknown"


def compare_versions(specified: str | None, latest: str | None) -> str:
    if not specified or not latest:
        return "-"
    try:
        specified_version = Version(specified.strip("=<>!~"))
        latest_version = Version(latest)
        if specified_version.major < latest_version.major:
            return "major"
        elif specified_version.minor < latest_version.minor:
            return "minor"
        elif specified_version.micro < latest_version.micro:
            return "patch"
        else:
            return "up-to-date"
    except Exception:
        return "?"


async def fetch_latest_from_pypi(name: str) -> tuple[str, str, str]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"https://pypi.org/pypi/{name}/json")
        if resp.status_code != 200:
            return name, "-", "-"

        data = resp.json()
        latest = data["info"].get("version", "-")
        filetype = "-"

        for f in data["releases"].get(latest, []):
            if f["packagetype"] == "bdist_wheel":
                filetype = "wheel"
                break

        if filetype == "-":
            for f in data["releases"].get(latest, []):
                if f["packagetype"] == "sdist":
                    filetype = "sdist"
                    break

        return name, latest, filetype


async def gather_metadata(dependencies: dict[str, str]) -> list[dict[str, Any]]:
    parsed = [parse_dependency(v) for v in dependencies.values()]
    results = await asyncio.gather(
        *[fetch_latest_from_pypi(dep["name"]) for dep in parsed], return_exceptions=True
    )

    for i, res in enumerate(results):
        if isinstance(res, Exception | BaseException):
            parsed[i]["latest_version"] = "-"
            parsed[i]["latest_filetype"] = "-"
            parsed[i]["update_type"] = "error"
        else:
            _, latest, filetype = res
            parsed[i]["latest_version"] = latest
            parsed[i]["latest_filetype"] = filetype
            parsed[i]["update_type"] = classify_update(parsed[i]["version"], latest)

    return parsed


# ------------------ TOML Logic ------------------ #
def load_pyproject(path: Path) -> dict[str, Any]:
    with path.open("rb") as f:
        return tomllib.load(f)


def save_pyproject(data: dict[str, Any], path: Path):
    text = tomli_w.dumps(data)
    path.write_text(text)


def get_dependency_group(data: dict[str, Any], group: str) -> dict[str, str]:
    if group == "project":
        return {
            Requirement(req).name: req for req in data.get("project", {}).get("dependencies", [])
        }
    elif group == "dev":
        dev_deps = data.get("tool", {}).get("uv", {}).get("dev-dependencies", {})
        if isinstance(dev_deps, list):
            return {Requirement(req).name: req for req in dev_deps}
        elif isinstance(dev_deps, dict):
            return {
                Requirement(f"{name}{specifier}").name: f"{name}{specifier}"
                for name, specifier in dev_deps.items()
            }
    raise ValueError(f"Unknown dependency group: {group}")


def update_pyproject_versions(data: dict[str, Any], upgrades: dict[str, str], group: str):
    if group == "project":
        deps = data["project"]["dependencies"]
        new_deps = []
        for req in deps:
            name, _ = parse_dependency(req)
            if name in upgrades:
                new_deps.append(f"{name}=={upgrades[name]}")
            else:
                new_deps.append(req)
        data["project"]["dependencies"] = new_deps
    elif group == "dev":
        for name, version in upgrades.items():
            data["tool"]["uv"]["dev-dependencies"][name] = f"=={version}"
