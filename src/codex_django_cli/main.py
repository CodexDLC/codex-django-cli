"""Top-level entrypoint for the interactive codex-django CLI."""

from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Literal

from rich.console import Console

from codex_django_cli import prompts

if TYPE_CHECKING:
    from codex_django_cli.commands.install import InstallSelection

console = Console()
MenuResult = Literal["done", "back", "exit"]


def main(args: list[str] | None = None, forced_project: str | None = None) -> int:
    if args is None:
        args = sys.argv[1:]
    if args and args[0] == "menu":
        args = args[1:]
        if not args:
            return _interactive_menu(forced_project=forced_project)
    if args:
        return _handle_cli_args(args)
    return _interactive_menu(forced_project=forced_project)


def _interactive_menu(forced_project: str | None = None) -> int:
    return _global_menu(forced_project=forced_project)


def _global_menu(forced_project: str | None = None) -> int:
    while True:
        action = prompts.ask_main_action()
        if not action or action == "❌  Exit":
            return 0
        if action == "🚀  Init Django project":
            result = _init_wizard()
        elif action == "🧩  Extend existing Django project":
            result = _extend_wizard(forced_project=forced_project)
        elif action == "🏗  Generate deployment files":
            result = _deploy_wizard(generate_docker=True, generate_cicd=False, forced_project=forced_project)
        elif action == "🔁  Generate CI/CD workflows":
            result = _deploy_wizard(generate_docker=False, generate_cicd=True, forced_project=forced_project)
        elif action == "🪝  Configure pre-commit":
            result = _precommit_wizard()
        elif action == "📦  Generate repo config files":
            result = _repo_config_wizard(forced_project=forced_project)
        else:
            result = "back"
        if result == "exit":
            return 0


def _list_projects(src_path: str) -> list[str]:
    if not os.path.isdir(src_path):
        return []
    projects: list[str] = []
    for item in sorted(os.listdir(src_path)):
        if item.startswith("."):
            continue
        project_dir = os.path.join(src_path, item)
        manage_py = os.path.join(project_dir, "manage.py")
        if os.path.isdir(project_dir) and os.path.isfile(manage_py):
            projects.append(item)
    return projects


def _resolve_project_dir(forced_project: str | None = None) -> str | None:
    src_path = os.path.join(os.getcwd(), "src")
    if forced_project:
        return os.path.join(src_path, forced_project)
    projects = _list_projects(src_path)
    if not os.path.isdir(src_path):
        console.print("[red]❌ No src/ directory found.[/red]")
        return None
    if not projects:
        console.print("[red]❌ No Django projects found in src/[/red]")
        return None
    if len(projects) == 1:
        return os.path.join(src_path, projects[0])
    selected_target = prompts.ask_target_project(projects)
    if not selected_target or selected_target == "← Back":
        return None
    return os.path.join(src_path, selected_target)


def _resolve_project_name(forced_project: str | None = None) -> str | None:
    if forced_project:
        return forced_project
    project_dir = _resolve_project_dir(forced_project=forced_project)
    if project_dir:
        return os.path.basename(project_dir)
    return prompts.ask_project_name()


def _build_selection_from_modules(
    modules: list[str], *, overwrite: bool, enable_i18n: bool, with_cloud_db: bool
) -> InstallSelection:
    from codex_django_cli.commands.install import InstallSelection

    return InstallSelection(
        cabinet="cabinet" in modules,
        booking="booking" in modules or "booking_engine" in modules or "booking_cabinet" in modules,
        booking_cabinet="booking_cabinet" in modules,
        conversations="conversations" in modules,
        public_booking="public_booking" in modules,
        sw="sw" in modules,
        overwrite=overwrite,
        i18n=enable_i18n,
        cloud_db=with_cloud_db,
    )


def _init_wizard() -> MenuResult:
    name = prompts.ask_project_name()
    if not name:
        return "back"
    name = name.strip()
    mode = prompts.ask_init_mode()
    if not mode or mode == "← Back":
        return "back"
    overwrite = "Force" in mode
    is_custom = "Custom" in mode
    modules = ["cabinet", "conversations"]
    if is_custom:
        selected_modules = prompts.ask_init_modules()
        if selected_modules is None:
            return "back"
        modules = selected_modules
    with_cloud_db = prompts.ask_with_cloud_db()
    enable_i18n = prompts.ask_enable_i18n()
    languages = prompts.ask_languages(enable_i18n) if enable_i18n else None
    from codex_django_cli.commands.install import describe_plan, resolve_install_selection

    selection = _build_selection_from_modules(
        modules, overwrite=overwrite, enable_i18n=enable_i18n, with_cloud_db=with_cloud_db
    )
    resolved = resolve_install_selection(selection, base_mode=True)
    if not prompts.ask_confirm_plan(describe_plan(resolved)):
        return "back"
    from codex_django_cli.commands.init import handle_init

    handle_init(
        name=name,
        base_dir=os.getcwd(),
        target_dir=os.getcwd(),
        overwrite=overwrite,
        enable_i18n=enable_i18n,
        languages=languages,
        with_cabinet=selection.cabinet,
        with_booking=selection.booking,
        with_conversations=selection.conversations,
        with_public_booking=selection.public_booking,
        with_sw=selection.sw,
        with_cloud_db=with_cloud_db,
    )
    return "done"


def _extend_wizard(forced_project: str | None = None) -> MenuResult:
    project_dir = _resolve_project_dir(forced_project=forced_project)
    if not project_dir:
        return "back"
    from codex_django_cli.commands.install import (
        InstallSelection,
        describe_plan,
        detect_project_modules,
        resolve_install_selection,
        scaffold_compare_copy,
        scaffold_existing_project,
    )

    detected_modules = detect_project_modules(project_dir)
    modules = prompts.ask_extension_modules(installed_modules=detected_modules)
    if modules is None:
        return "back"
    if not modules:
        return "back"

    install_modules: list[str] = []
    compare_modules: list[str] = []
    for module_name in modules:
        if not detected_modules.get(module_name):
            install_modules.append(module_name)
            continue
        action = prompts.ask_existing_module_action(module_name.replace("_", " "))
        if not action or action == "← Back":
            return "back"
        if action == "compare":
            compare_modules.append(module_name)
        else:
            install_modules.append(module_name)

    if install_modules:
        install_selection = InstallSelection(
            cabinet="cabinet" in install_modules,
            booking="booking" in install_modules
            or "booking_engine" in install_modules
            or "booking_cabinet" in install_modules,
            booking_cabinet="booking_cabinet" in install_modules,
            conversations="conversations" in install_modules,
            public_booking="public_booking" in install_modules,
            sw="sw" in install_modules,
        )
        resolved_install = resolve_install_selection(install_selection, base_mode=False)
        if not prompts.ask_confirm_plan(f"install: {describe_plan(resolved_install)}"):
            return "back"
        scaffold_existing_project(project_dir=project_dir, selection=install_selection)

    if compare_modules:
        compare_selection = InstallSelection(
            cabinet="cabinet" in compare_modules,
            booking="booking" in compare_modules
            or "booking_engine" in compare_modules
            or "booking_cabinet" in compare_modules,
            booking_cabinet="booking_cabinet" in compare_modules,
            conversations="conversations" in compare_modules,
            public_booking="public_booking" in compare_modules,
            sw="sw" in compare_modules,
        )
        resolved_compare = resolve_install_selection(compare_selection, base_mode=False)
        if not prompts.ask_confirm_plan(f"compare copy: {describe_plan(resolved_compare)}"):
            return "back"
        scaffold_compare_copy(project_dir=project_dir, selection=compare_selection)
    return "done"


def _deploy_wizard(*, generate_docker: bool, generate_cicd: bool, forced_project: str | None = None) -> MenuResult:
    project_dir = _resolve_project_dir(forced_project=forced_project)
    if not project_dir:
        return "back"
    deploy_mode = prompts.ask_deploy_mode()
    if not deploy_mode or deploy_mode == "← Back":
        return "back"
    domain_name = prompts.ask_domain_name()
    if not domain_name:
        return "back"
    services = prompts.ask_deploy_services()
    if services is None:
        return "back"
    action_label = (
        "deployment files under deploy/"
        if generate_docker and not generate_cicd
        else "CI/CD workflows under .github/workflows/"
    )
    if not prompts.ask_confirm_action(f"Generate {action_label} for project '{os.path.basename(project_dir)}'?"):
        return "back"
    from codex_django_cli.commands.deploy import handle_generate_deploy

    handle_generate_deploy(
        name=os.path.basename(project_dir),
        project_root=os.getcwd(),
        deploy_mode=deploy_mode,
        domain_name=domain_name,
        with_bot=services["with_bot"],
        with_worker=services["with_worker"],
        generate_docker=generate_docker,
        generate_cicd=generate_cicd,
    )
    return "done"


def _precommit_wizard() -> MenuResult:
    if not prompts.ask_confirm_action("Create .pre-commit-config.yaml and .secrets.baseline in the current repo root?"):
        return "back"
    from codex_django_cli.commands.quality import handle_configure_precommit

    handle_configure_precommit(os.getcwd())
    return "done"


def _repo_config_wizard(forced_project: str | None = None) -> MenuResult:
    action = prompts.ask_repo_config_action()
    if not action or action == "← Back":
        return "back"
    project_name = _resolve_project_name(forced_project=forced_project)
    if not project_name:
        return "back"
    include_pyproject = action in {"Generate pyproject.toml + .env.example", "Generate pyproject.toml only"}
    include_env_example = action in {"Generate pyproject.toml + .env.example", "Generate .env.example only"}
    if not prompts.ask_confirm_action(
        f"Generate repo config files for project '{project_name}' in the current repo root?"
    ):
        return "back"
    from codex_django_cli.commands.repo import handle_generate_repo_config

    handle_generate_repo_config(
        name=project_name,
        project_root=os.getcwd(),
        include_pyproject=include_pyproject,
        include_env_example=include_env_example,
    )
    return "done"


def _handle_cli_args(args: list[str]) -> int:
    import argparse

    from codex_django_cli.commands.deploy import handle_generate_deploy
    from codex_django_cli.commands.init import handle_init

    parser = argparse.ArgumentParser(prog="codex-django")
    subparsers = parser.add_subparsers(dest="command")
    init_parser = subparsers.add_parser("init", help="Initialize a new project.")
    menu_parser = subparsers.add_parser("menu", help="Launch interactive scaffold menu.")
    init_parser.add_argument("name", help="Name of the project (folder inside src/)")
    init_parser.add_argument("target_dir", nargs="?", default=None)
    init_parser.add_argument("--code", action="store_true", help="Only scaffold core code (no repo wrappers)")
    init_parser.add_argument("--dev", action="store_true", help="Dev mode scaffold into local sandbox")
    init_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    init_parser.add_argument("--i18n", dest="enable_i18n", action="store_true", default=False)
    init_parser.add_argument("--no-i18n", dest="enable_i18n", action="store_false")
    init_parser.add_argument("--languages", default=None)
    init_parser.add_argument("--with-booking", action="store_true", default=False)
    init_parser.add_argument("--with-public-booking", action="store_true", default=False)
    init_parser.add_argument("--without-cabinet", dest="with_cabinet", action="store_false")
    init_parser.add_argument("--without-conversations", dest="with_conversations", action="store_false")
    init_parser.add_argument("--with-sw", action="store_true", default=False)
    init_parser.add_argument("--with-cloud-db", action="store_true", default=False)
    init_parser.set_defaults(with_cabinet=True, with_conversations=True)
    init_parser.set_defaults(
        func=lambda parsed: handle_init(
            name=parsed.name,
            base_dir=os.getcwd(),
            target_dir=parsed.target_dir,
            code_only=parsed.code,
            dev_mode=parsed.dev,
            overwrite=parsed.overwrite,
            enable_i18n=parsed.enable_i18n,
            languages=prompts.parse_language_codes(parsed.languages) if parsed.languages else None,
            with_cabinet=parsed.with_cabinet,
            with_booking=parsed.with_booking,
            with_conversations=parsed.with_conversations,
            with_public_booking=parsed.with_public_booking,
            with_sw=parsed.with_sw,
            with_cloud_db=parsed.with_cloud_db,
        )
    )
    menu_parser.set_defaults(func=lambda parsed: _interactive_menu())
    deploy_parser = subparsers.add_parser("deploy", help="Generate Docker + CI/CD deployment files.")
    deploy_parser.add_argument("name", help="Project name (folder inside src/)")
    deploy_parser.add_argument("--mode", choices=["standalone", "stack"], default="standalone")
    deploy_parser.add_argument("--domain", default="example.com")
    deploy_parser.add_argument("--with-bot", action="store_true", default=False)
    deploy_parser.add_argument("--with-worker", action="store_true", default=False)
    deploy_parser.add_argument("--no-docker", action="store_true", default=False)
    deploy_parser.add_argument("--no-cicd", action="store_true", default=False)
    deploy_parser.set_defaults(
        func=lambda parsed: handle_generate_deploy(
            name=parsed.name,
            project_root=os.getcwd(),
            deploy_mode=parsed.mode,
            domain_name=parsed.domain,
            with_bot=parsed.with_bot,
            with_worker=parsed.with_worker,
            generate_docker=not parsed.no_docker,
            generate_cicd=not parsed.no_cicd,
        )
    )
    parsed = parser.parse_args(args)
    if hasattr(parsed, "func"):
        parsed.func(parsed)
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
