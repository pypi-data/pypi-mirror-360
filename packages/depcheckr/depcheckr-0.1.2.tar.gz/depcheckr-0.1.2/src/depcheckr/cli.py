import asyncio
from pathlib import Path
from typing import Annotated, Any

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from .helpers import (
    gather_metadata,
    get_dependency_group,
    load_pyproject,
    save_pyproject,
    update_pyproject_versions,
)

app = typer.Typer()
inspect_app = typer.Typer()
upgrade_app = typer.Typer()

app.add_typer(inspect_app, name="inspect", help="Inspect current dependencies and versions")
app.add_typer(upgrade_app, name="upgrade", help="Upgrade specified or all outdated dependencies")

console = Console()
DEFAULT_PATH = Path("pyproject.toml")
DEFAULT_OPTION: list[Any] = []


@inspect_app.command()
def show(
    path: Annotated[Path, typer.Argument()] = DEFAULT_PATH,
    group: str = typer.Option("project", help="Dependency group: project or dev"),
):
    data = load_pyproject(path)
    deps = get_dependency_group(data, group)
    if not deps:
        console.print(f"[red]No dependencies found in [{group}] group[/red]")
        raise typer.Exit(1)

    results = asyncio.run(gather_metadata(deps))
    table = Table(title=f"[{group}] dependencies", show_lines=True)
    table.add_column("Name")
    table.add_column("Specified")
    table.add_column("Latest")
    table.add_column("Filetype")
    table.add_column("Update")

    for r in results:
        table.add_row(
            r["name"],
            r["version"] or "-",
            r["latest_version"] or "-",
            r["latest_filetype"] or "-",
            r["update_type"],
        )

    console.print(table)


@upgrade_app.command()
def apply(
    path: Annotated[Path, typer.Argument()] = DEFAULT_PATH,
    group: Annotated[str, typer.Option(help="Dependency group: project or dev")] = "project",
    upgrade: Annotated[
        list[str], typer.Option(help="List of packages to upgrade")
    ] = DEFAULT_OPTION,
    upgrade_all: Annotated[bool, typer.Option(help="Upgrade all outdated dependencies")] = False,
    dry_run: Annotated[bool, typer.Option(help="Don't modify pyproject.toml")] = False,
):
    data = load_pyproject(path)
    deps = get_dependency_group(data, group)
    if not deps:
        console.print(f"[red]No dependencies found in [{group}] group[/red]")
        raise typer.Exit(1)

    results = asyncio.run(gather_metadata(deps))
    table = Table(title=f"Upgrade [{group}]", show_lines=True)
    table.add_column("Name")
    table.add_column("Current")
    table.add_column("Latest")
    table.add_column("Type")

    upgrades = {}
    for r in results:
        if (upgrade_all and r["update_type"] != "up-to-date" and r["latest_version"]) or (
            r["name"] in upgrade and r["latest_version"]
        ):
            upgrades[r["name"]] = r["latest_version"]
            table.add_row(
                r["name"],
                r["version"] or "-",
                r["latest_version"] or "-",
                r["update_type"],
            )

    if not upgrades:
        rprint("[green]All dependencies are up to date[/green]")
        return

    console.print(table)

    if dry_run:
        rprint("[bold blue]Dry run: no changes made[/bold blue]")
    else:
        update_pyproject_versions(data, upgrades, group)
        save_pyproject(data, path)
        rprint(f"[green]Updated [bold]{path}[/bold] with new versions[/green]")
