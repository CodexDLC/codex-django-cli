"""Helpers for generating repository-level config files."""

from __future__ import annotations

import os

from rich.console import Console

from codex_django_cli.engine import CLIEngine

console = Console()


def _write_rendered_file(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def _resolve_output_path(project_root: str, primary_name: str, compare_name: str, *, overwrite: bool) -> tuple[str, bool]:
    primary_path = os.path.join(project_root, primary_name)
    if overwrite or not os.path.exists(primary_path):
        return primary_path, False
    return os.path.join(project_root, compare_name), True


def handle_generate_repo_config(
    *,
    name: str,
    project_root: str,
    include_pyproject: bool = True,
    include_env_example: bool = True,
    overwrite: bool = False,
) -> None:
    """Generate repository-level config files for a project."""
    engine = CLIEngine()
    context = {"project_name": name}

    if include_pyproject:
        pyproject_path, is_compare = _resolve_output_path(
            project_root,
            "pyproject.toml",
            f"pyproject.{name}.toml",
            overwrite=overwrite,
        )
        _write_rendered_file(pyproject_path, engine.render_template("repo/pyproject.toml.j2", context))
        label = "comparison file" if is_compare else "file"
        console.print(f"[green]✓[/green] Generated pyproject {label}: [bold]{pyproject_path}[/bold]")

    if include_env_example:
        env_example_path, is_compare = _resolve_output_path(
            project_root,
            ".env.example",
            f".env.{name}.example",
            overwrite=overwrite,
        )
        _write_rendered_file(env_example_path, engine.render_template("repo/.env.example.j2", context))
        label = "comparison file" if is_compare else "file"
        console.print(f"[green]✓[/green] Generated env example {label}: [bold]{env_example_path}[/bold]")
