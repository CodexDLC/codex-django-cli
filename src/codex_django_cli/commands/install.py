"""Installation orchestrator for menu-first project scaffolding."""

from __future__ import annotations

import os
from dataclasses import dataclass

from rich.console import Console

console = Console()

MODULE_MARKERS: dict[str, list[str]] = {
    "cabinet": ["cabinet/apps.py", "cabinet/urls.py"],
    "conversations": ["features/conversations/apps.py", "features/conversations/urls.py"],
    "booking_engine": ["features/booking/booking_settings.py", "features/booking/providers/runtime.py"],
    "booking_cabinet": ["cabinet/views/booking.py", "cabinet/templates/cabinet/booking/list.html"],
    "public_booking": ["features/booking_public/urls.py", "features/booking_public/views.py"],
    "sw": ["templates/sw.js", "static/manifest.json"],
}


@dataclass(frozen=True)
class InstallSelection:
    cabinet: bool = True
    booking: bool = False
    booking_cabinet: bool = False
    conversations: bool = True
    public_booking: bool = False
    sw: bool = False
    code_only: bool = False
    overwrite: bool = False
    dev_mode: bool = False
    i18n: bool = False
    cloud_db: bool = False


@dataclass(frozen=True)
class ResolvedInstallPlan:
    cabinet: bool
    booking: bool
    conversations: bool
    public_booking: bool
    sw: bool

    def module_labels(self) -> list[str]:
        labels = ["base"]
        if self.cabinet:
            labels.append("cabinet")
        if self.conversations:
            labels.append("conversations")
        if self.booking:
            labels.append("booking")
        if self.public_booking:
            labels.append("public-booking")
        if self.sw:
            labels.append("sw")
        return labels


def detect_project_modules(project_dir: str) -> dict[str, bool]:
    detected: dict[str, bool] = {}
    for module_name, markers in MODULE_MARKERS.items():
        detected[module_name] = any(os.path.exists(os.path.join(project_dir, marker)) for marker in markers)
    return detected


def resolve_install_selection(selection: InstallSelection, *, base_mode: bool) -> ResolvedInstallPlan:
    with_conversations = True if base_mode else selection.conversations
    with_booking = selection.booking or selection.booking_cabinet or selection.public_booking
    with_cabinet = selection.cabinet or selection.booking_cabinet or with_booking
    with_public_booking = selection.public_booking and with_booking
    return ResolvedInstallPlan(
        cabinet=with_cabinet,
        booking=with_booking,
        conversations=with_conversations,
        public_booking=with_public_booking,
        sw=selection.sw,
    )


def describe_plan(plan: ResolvedInstallPlan) -> str:
    return ", ".join(plan.module_labels())


def _normalize_languages(languages: list[str] | None) -> list[str]:
    if not languages:
        return ["en"]
    normalized: list[str] = []
    for item in languages:
        code = item.strip().lower().replace("_", "-")
        if code and code not in normalized:
            normalized.append(code)
    return normalized or ["en"]


def _resolve_scaffold_paths(name: str, base_dir: str, target_dir: str | None, dev_mode: bool) -> tuple[str, str]:
    if dev_mode:
        lib_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        pyproject_path = os.path.join(lib_root, "pyproject.toml")
        is_lib_source = False
        if os.path.exists(pyproject_path):
            with open(pyproject_path, encoding="utf-8") as handle:
                pyproject_content = handle.read()
            if 'name = "codex-django"' in pyproject_content or 'name = "codex-django-cli"' in pyproject_content:
                is_lib_source = True
        if not is_lib_source:
            raise ValueError("--dev mode is only available when running from the library source tree.")
        project_root = os.path.join(lib_root, "sandbox")
        backend_dir = os.path.join(project_root, "src", name)
        return project_root, backend_dir
    if target_dir:
        project_root = os.path.abspath(target_dir)
        backend_dir = os.path.join(project_root, "src", name)
        return project_root, backend_dir
    project_root = os.path.join(base_dir, name)
    backend_dir = os.path.join(project_root, "src", name)
    return project_root, backend_dir


def scaffold_new_project(
    *, name: str, base_dir: str, target_dir: str | None, selection: InstallSelection, languages: list[str] | None
) -> ResolvedInstallPlan | None:
    from codex_django_cli import engine as engine_module
    from codex_django_cli.commands.repo import handle_generate_repo_config

    try:
        project_root, backend_dir = _resolve_scaffold_paths(name, base_dir, target_dir, selection.dev_mode)
    except ValueError as exc:
        console.print(f"[red]❌ {exc}[/red]")
        return None
    if os.path.exists(backend_dir) and not selection.overwrite:
        console.print(f"[yellow]⚠ Django project already exists in:[/yellow] [bold]{backend_dir}[/bold]")
        console.print("[yellow]  Use overwrite mode to re-scaffold.[/yellow]")
        return None

    normalized_languages = _normalize_languages(languages)
    enable_i18n = selection.i18n or languages is not None
    plan = resolve_install_selection(selection, base_mode=True)
    engine = engine_module.CLIEngine()
    context = {
        "project_name": name,
        "enable_i18n": enable_i18n,
        "languages": normalized_languages,
        "with_cabinet": plan.cabinet,
        "with_booking": plan.booking,
        "with_conversations": plan.conversations,
        "with_public_booking": plan.public_booking,
        "with_sw": plan.sw,
        "with_cloud_db": selection.cloud_db,
    }
    if not selection.code_only:
        handle_generate_repo_config(
            name=name,
            project_root=project_root,
            include_pyproject=True,
            include_env_example=True,
            overwrite=selection.overwrite,
        )
    engine.scaffold("project", target_dir=backend_dir, context=context, overwrite=selection.overwrite)
    if plan.cabinet:
        engine.scaffold(
            "cabinet", target_dir=os.path.join(backend_dir, "cabinet"), context=context, overwrite=selection.overwrite
        )
    if plan.conversations:
        engine.scaffold(
            "features/conversations", target_dir=backend_dir, context=context, overwrite=selection.overwrite
        )
    if plan.booking:
        engine.scaffold("features/booking_core", target_dir=backend_dir, context=context, overwrite=selection.overwrite)
    if plan.public_booking:
        engine.scaffold(
            "features/booking_public", target_dir=backend_dir, context=context, overwrite=selection.overwrite
        )
    console.print(f"[green]✓[/green] Project [bold]{name}[/bold] initialized in [bold]{project_root}[/bold]")
    console.print(f"  Modules: [cyan]{describe_plan(plan)}[/cyan]")
    return plan


def _scaffold_modules_to_target(
    *, target_dir: str, selection: InstallSelection, compare_copy: bool = False
) -> ResolvedInstallPlan:
    from codex_django_cli import engine as engine_module

    plan = resolve_install_selection(selection, base_mode=False)
    context = {
        "with_cabinet": plan.cabinet,
        "with_booking": plan.booking,
        "with_conversations": plan.conversations,
        "with_public_booking": plan.public_booking,
        "with_sw": plan.sw,
        "enable_i18n": selection.i18n,
    }
    engine = engine_module.CLIEngine()

    if plan.cabinet:
        engine.scaffold(
            "cabinet",
            target_dir=os.path.join(target_dir, "cabinet"),
            context=context,
            overwrite=selection.overwrite or compare_copy,
        )
    if plan.conversations:
        engine.scaffold(
            "features/conversations",
            target_dir=target_dir,
            context=context,
            overwrite=selection.overwrite or compare_copy,
        )
    if plan.booking:
        engine.scaffold(
            "features/booking_core",
            target_dir=target_dir,
            context=context,
            overwrite=selection.overwrite or compare_copy,
        )
    if plan.public_booking:
        engine.scaffold(
            "features/booking_public",
            target_dir=target_dir,
            context=context,
            overwrite=selection.overwrite or compare_copy,
        )
    return plan


def scaffold_existing_project(*, project_dir: str, selection: InstallSelection) -> ResolvedInstallPlan:
    plan = _scaffold_modules_to_target(target_dir=project_dir, selection=selection)
    console.print(f"[green]✓[/green] Modules installed in [bold]{project_dir}[/bold]")
    console.print(f"  Modules: [cyan]{describe_plan(plan)}[/cyan]")
    return plan


def scaffold_compare_copy(*, project_dir: str, selection: InstallSelection) -> tuple[ResolvedInstallPlan, str]:
    compare_dir = os.path.join(project_dir, "_scaffold_compare")
    plan = _scaffold_modules_to_target(target_dir=compare_dir, selection=selection, compare_copy=True)
    console.print(f"[green]✓[/green] Compare copy generated in [bold]{compare_dir}[/bold]")
    console.print(f"  Modules: [cyan]{describe_plan(plan)}[/cyan]")
    return plan, compare_dir
