"""CLI handler for project initialization."""

from __future__ import annotations

from rich.console import Console

from codex_django_cli.commands.install import InstallSelection, scaffold_new_project

console = Console()


def handle_init(
    name: str,
    base_dir: str,
    target_dir: str | None = None,
    code_only: bool = False,
    dev_mode: bool = False,
    overwrite: bool = False,
    enable_i18n: bool = False,
    languages: list[str] | None = None,
    with_cabinet: bool = True,
    with_booking: bool = False,
    with_conversations: bool = True,
    with_public_booking: bool = False,
    with_sw: bool = False,
    with_cloud_db: bool = False,
) -> None:
    """Scaffold a new codex-django project using module-selection orchestration."""
    selection = InstallSelection(
        cabinet=with_cabinet,
        booking=with_booking,
        conversations=with_conversations,
        public_booking=with_public_booking,
        sw=with_sw,
        code_only=code_only,
        overwrite=overwrite,
        dev_mode=dev_mode,
        i18n=enable_i18n,
        cloud_db=with_cloud_db,
    )

    if enable_i18n and languages and len(languages) == 1:
        console.print("[cyan]Using translation-aware settings with a single selected language.[/cyan]")

    scaffold_new_project(
        name=name,
        base_dir=base_dir,
        target_dir=target_dir,
        selection=selection,
        languages=languages,
    )
