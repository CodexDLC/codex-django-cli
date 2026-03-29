"""Top-level entrypoint for the interactive codex-django CLI.

The module decides whether to show the global scaffold menu or the
project-local command menu and also keeps compatibility with legacy
argument-based invocations.
"""

from __future__ import annotations

import os
import sys

from rich.console import Console

from codex_django_cli import prompts

console = Console()


def main(args: list[str] | None = None, forced_project: str | None = None) -> int:
    """Run the interactive or legacy codex-django CLI flow.

    Args:
        args: Optional CLI arguments. Defaults to ``sys.argv[1:]``.
        forced_project: Optional project name used to bypass interactive
            project selection in scaffold flows.

    Returns:
        Process-style exit code.
    """
    if args is None:
        args = sys.argv[1:]

    # Handle 'menu' subcommand (e.g. from manage.py menu)
    if args and args[0] == "menu":
        args = args[1:]
        if not args:
            return _interactive_menu(forced_project=forced_project)

    if args:
        return _handle_legacy_args(args)

    return _interactive_menu(forced_project=forced_project)


def _is_in_project() -> bool:
    """Check if the current directory is a codex-django scaffolded project root.

    Requires both pyproject.toml and a Django manage.py inside src/<project>/.
    This distinguishes a real user project from the library's own source tree.
    """
    if not os.path.exists("pyproject.toml") or not os.path.isdir("src"):
        return False
    src_path = os.path.join(os.getcwd(), "src")
    try:
        for item in os.listdir(src_path):
            if os.path.isfile(os.path.join(src_path, item, "manage.py")):
                return True
    except OSError:
        pass
    return False


def _interactive_menu(forced_project: str | None = None) -> int:
    """Dispatch to the global or project-local interactive menu."""
    if _is_in_project():
        return _project_menu(forced_project=forced_project)
    return _global_menu()


def _global_menu() -> int:
    """Handle the top-level menu shown outside a scaffolded project."""
    action = prompts.ask_main_action(is_project=False)
    if action == "🚀  Init new project":
        return _init_wizard()
    return 0


def _init_wizard() -> int:
    """Interactive project init wizard."""
    name = prompts.ask_project_name()
    if not name:
        return 0
    name = name.strip()

    mode = prompts.ask_init_mode()
    if not mode or mode == "← Back":
        return 0

    overwrite = "Force" in mode
    is_custom = "Custom" in mode

    with_cabinet = False
    with_booking = False
    if is_custom:
        modules = prompts.ask_init_modules()
        with_cabinet = "cabinet" in modules
        with_booking = "booking" in modules
    enable_i18n = prompts.ask_enable_i18n()
    languages = prompts.ask_languages(enable_i18n) if enable_i18n else None

    from codex_django_cli.commands.init import handle_init

    if languages is None:
        handle_init(
            name,
            os.getcwd(),
            target_dir=os.getcwd(),
            overwrite=overwrite,
            enable_i18n=enable_i18n,
            with_cabinet=with_cabinet,
            with_booking=with_booking,
        )
    else:
        handle_init(
            name,
            os.getcwd(),
            target_dir=os.getcwd(),
            overwrite=overwrite,
            enable_i18n=enable_i18n,
            languages=languages,
            with_cabinet=with_cabinet,
            with_booking=with_booking,
        )
    return 0


def _project_menu(forced_project: str | None = None) -> int:
    """Handle the project-local menu shown inside a scaffolded project."""
    action = prompts.ask_project_action()

    if not action or action == "❌  Exit":
        return 0

    if action == "🚀  Standard Commands":
        return _handle_standard_commands()

    elif action == "🧩  Scaffolding (Apps/Modules)":
        return _handle_scaffolding(forced_project=forced_project)

    elif action == "🛡  Quality & Tools":
        return _handle_quality_tools()

    elif action == "🏁  Deployment Setup":
        return _handle_deployment_setup(forced_project=forced_project)

    elif action == "⚙️  Security":
        from codex_django_cli.utils import generate_field_encryption_key, generate_secret_key

        secret_key = generate_secret_key()
        field_encryption_key = generate_field_encryption_key()
        console.print(f"\n[green]Generated new Django SECRET_KEY:[/green]\n[bold]{secret_key}[/bold]\n")
        console.print(
            f"[green]Generated new FIELD_ENCRYPTION_KEY (Fernet):[/green]\n"
            f"[bold]{field_encryption_key}[/bold]\n"
        )

    return 0


def _handle_standard_commands() -> int:
    """Execute common Django management commands from the interactive menu."""
    cmd = prompts.ask_standard_command()
    if not cmd or cmd == "← Back":
        return 0

    from codex_django_cli.utils import run_django_command

    if cmd == "makemigrations":
        run_django_command(["makemigrations"])
    elif cmd == "migrate":
        run_django_command(["migrate"])
    elif cmd == "createsuperuser":
        run_django_command(["createsuperuser"])
    elif cmd == "shell":
        run_django_command(["shell"])
    elif cmd == "i18n: Generate locale domains":
        run_django_command(["codex_makemessages"])
    elif cmd == "i18n: Compile":
        run_django_command(["compilemessages"])

    return 0


def _handle_scaffolding(forced_project: str | None = None) -> int:
    """Handle interactive feature scaffolding for an existing project.

    Args:
        forced_project: Optional project name used to bypass the target picker.

    Returns:
        Process-style exit code.
    """
    src_path = os.path.join(os.getcwd(), "src")

    if forced_project:
        target = forced_project
    else:
        projects = [d for d in os.listdir(src_path) if os.path.isdir(os.path.join(src_path, d))]
        if not projects:
            console.print("[red]❌ No projects found in src/[/red]")
            return 1

        if len(projects) == 1:
            target = projects[0]
        else:
            selected_target = prompts.ask_target_project(projects)
            if not selected_target:
                return 0
            target = selected_target

    feature = prompts.ask_feature()
    if not feature or feature == "← Back":
        return 0

    if feature == "Basic app":
        app_name = prompts.ask_app_name()
        if not app_name:
            return 0
        from codex_django_cli.commands.add_app import handle_add_app

        handle_add_app(app_name.strip(), os.path.join(src_path, target))

    elif feature == "Notifications":
        app_name = prompts.ask_app_name("App name for notifications (default: system):", default="system")
        if not app_name:
            return 0
        from codex_django_cli.commands.notifications import handle_add_notifications

        handle_add_notifications(
            app_name.strip(),
            os.path.join(src_path, target),
        )

    elif feature == "Client Cabinet":
        from codex_django_cli.commands.client_cabinet import handle_add_client_cabinet

        handle_add_client_cabinet(os.path.join(src_path, target))

    elif feature == "Booking (Advanced)":
        from codex_django_cli.commands.booking import handle_add_booking

        handle_add_booking(os.path.join(src_path, target))

    return 0


def _handle_quality_tools() -> int:
    """Run quality helpers chosen from the interactive menu."""
    opt = prompts.ask_quality_tool()
    if not opt or opt == "← Back":
        return 0

    if opt == "Configure pre-commit":
        from codex_django_cli.commands.quality import handle_configure_precommit

        handle_configure_precommit(os.getcwd())
    elif opt == "Run Project Checker":
        console.print("[yellow]Running Project Checker...[/yellow]")
        import subprocess

        # Using --all as it's a developer-friendly interactive default in BaseCheckRunner
        subprocess.run([sys.executable, "tools/dev/check.py", "--all"])  # nosec B603
    return 0


def _handle_deployment_setup(forced_project: str | None = None) -> int:
    """Collect deployment options and generate deploy scaffolding."""
    opt = prompts.ask_deploy_option()
    if not opt or opt == "← Back":
        return 0

    generate_docker = "Docker" in opt
    generate_cicd = "CI/CD" in opt

    src_path = os.path.join(os.getcwd(), "src")

    if forced_project:
        target = forced_project
    else:
        projects = [d for d in os.listdir(src_path) if os.path.isdir(os.path.join(src_path, d))]
        if not projects:
            console.print("[red]No projects found in src/ directory.[/red]")
            return 0
        if len(projects) == 1:
            target = projects[0]
        else:
            selected_target = prompts.ask_target_project(projects)
            if not selected_target:
                return 0
            target = selected_target

    deploy_mode = prompts.ask_deploy_mode()
    if not deploy_mode:
        return 0

    domain_name = prompts.ask_domain_name()
    if not domain_name:
        return 0

    services = prompts.ask_deploy_services()

    from codex_django_cli.commands.deploy import handle_generate_deploy

    handle_generate_deploy(
        name=target,
        project_root=os.getcwd(),
        deploy_mode=deploy_mode,
        domain_name=domain_name,
        with_bot=services["with_bot"],
        with_worker=services["with_worker"],
        generate_docker=generate_docker,
        generate_cicd=generate_cicd,
    )
    return 0


def _handle_legacy_args(args: list[str]) -> int:
    """Handle legacy argparse-style invocation for scripting and CI.

    Args:
        args: Raw argument vector without the program name.

    Returns:
        Process-style exit code.
    """
    import argparse

    from codex_django_cli.commands.add_app import handle_add_app
    from codex_django_cli.commands.booking import handle_add_booking
    from codex_django_cli.commands.client_cabinet import handle_add_client_cabinet
    from codex_django_cli.commands.init import handle_init
    from codex_django_cli.commands.notifications import handle_add_notifications

    parser = argparse.ArgumentParser(prog="codex-django")
    subparsers = parser.add_subparsers(dest="command")

    init_parser = subparsers.add_parser("init", help="Initialize a new project.")
    subparsers.add_parser("menu", help="Launch interactive menu.")
    init_parser.add_argument("name", help="Name of the project (folder inside src/)")
    init_parser.add_argument(
        "target_dir",
        nargs="?",
        default=None,
        help="Target directory for the project (default: <name>)",
    )
    init_parser.add_argument(
        "--code",
        action="store_true",
        help="Only scaffold the core code (no repo/wrapper files)",
    )
    init_parser.add_argument(
        "--dev",
        action="store_true",
        help="Dev mode: scaffold into sandbox/ inside the library",
    )
    init_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files",
    )
    init_parser.add_argument(
        "--i18n",
        dest="enable_i18n",
        action="store_true",
        default=False,
        help="Enable i18n / modular locale support",
    )
    init_parser.add_argument(
        "--no-i18n",
        dest="enable_i18n",
        action="store_false",
        help="Disable i18n / modular locale support (default)",
    )
    init_parser.add_argument(
        "--languages",
        default=None,
        help="Comma-separated language codes for i18n mode, e.g. en, ru, de-at, ja",
    )
    init_parser.add_argument("--with-cabinet", action="store_true", default=False)
    init_parser.add_argument("--with-booking", action="store_true", default=False)
    init_parser.set_defaults(
        func=lambda args: handle_init(
            name=args.name,
            base_dir=os.getcwd(),
            target_dir=args.target_dir,
            code_only=args.code,
            dev_mode=args.dev,
            overwrite=args.overwrite,
            enable_i18n=args.enable_i18n,
            languages=prompts.parse_language_codes(args.languages) if args.languages else None,
            with_cabinet=args.with_cabinet,
            with_booking=args.with_booking,
        )
    )

    app_parser = subparsers.add_parser("add-app")
    app_parser.add_argument("name")
    app_parser.add_argument("--project", default=None)
    app_parser.set_defaults(
        func=lambda args: handle_add_app(
            args.name,
            os.path.join(os.getcwd(), "src", args.project) if args.project else os.getcwd(),
        )
    )

    notif_parser = subparsers.add_parser("add-notifications")
    notif_parser.add_argument("--app", default="system")
    notif_parser.add_argument("--arq-dir", default=None, dest="arq_dir")
    notif_parser.add_argument("--project", default=None)
    notif_parser.set_defaults(
        func=lambda args: handle_add_notifications(
            args.app,
            os.path.join(os.getcwd(), "src", args.project) if args.project else os.getcwd(),
            arq_dir=args.arq_dir,
        )
    )

    cab_parser = subparsers.add_parser("add-client-cabinet")
    cab_parser.add_argument("--project", default=None)
    cab_parser.set_defaults(
        func=lambda args: handle_add_client_cabinet(
            os.path.join(os.getcwd(), "src", args.project) if args.project else os.getcwd(),
        )
    )

    booking_parser = subparsers.add_parser("add-booking")
    booking_parser.add_argument("--project", default=None)
    booking_parser.set_defaults(
        func=lambda args: handle_add_booking(
            os.path.join(os.getcwd(), "src", args.project) if args.project else os.getcwd(),
        )
    )

    from codex_django_cli.commands.deploy import handle_generate_deploy

    deploy_parser = subparsers.add_parser("deploy", help="Generate Docker + CI/CD deployment files.")
    deploy_parser.add_argument("name", help="Project name (folder inside src/)")
    deploy_parser.add_argument("--mode", choices=["standalone", "stack"], default="standalone")
    deploy_parser.add_argument("--domain", default="example.com")
    deploy_parser.add_argument("--with-bot", action="store_true", default=False)
    deploy_parser.add_argument("--with-worker", action="store_true", default=False)
    deploy_parser.add_argument("--no-docker", action="store_true", default=False)
    deploy_parser.add_argument("--no-cicd", action="store_true", default=False)
    deploy_parser.set_defaults(
        func=lambda args: handle_generate_deploy(
            name=args.name,
            project_root=os.getcwd(),
            deploy_mode=args.mode,
            domain_name=args.domain,
            with_bot=args.with_bot,
            with_worker=args.with_worker,
            generate_docker=not args.no_docker,
            generate_cicd=not args.no_cicd,
        )
    )

    parsed = parser.parse_args(args)

    if hasattr(parsed, "func"):
        parsed.func(parsed)
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())







