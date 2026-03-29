"""
handle_add_notifications
========================
CLI handler for the ``codex-django add-notifications`` command.

Scaffolds notification infrastructure into the target project:

  system/
    models/email_content.py
    selectors/email_content.py
    services/notification.py
  core/arq/
    client.py

Usage (from project root)::

    codex-django add-notifications
    codex-django add-notifications --arq-dir myapp/arq
"""

from __future__ import annotations

import os

from rich.console import Console

console = Console()


def handle_add_notifications(app_name: str, base_dir: str, arq_dir: str | None = None) -> None:
    """Scaffold notification infrastructure into the shared system layer.

    Args:
        app_name: Reserved for backward compatibility. Notifications always live in ``system``.
        base_dir: Project root directory.
        arq_dir: Optional relative directory for the ARQ client scaffold.
    """
    from codex_django_cli.engine import CLIEngine

    engine = CLIEngine()
    context = {"app_name": "system"}

    engine.scaffold(
        "features/notifications/feature/models",
        target_dir=os.path.join(base_dir, "system", "models"),
        context=context,
    )
    engine.scaffold(
        "features/notifications/feature/selectors",
        target_dir=os.path.join(base_dir, "system", "selectors"),
        context=context,
    )
    engine.scaffold(
        "features/notifications/feature/services",
        target_dir=os.path.join(base_dir, "system", "services"),
        context=context,
    )
    console.print("[green]✓[/green] Notification layer scaffolded → [bold]system/[/bold]")

    arq_target = os.path.join(base_dir, arq_dir) if arq_dir else os.path.join(base_dir, "core", "arq")
    engine.scaffold("features/notifications/arq", target_dir=arq_target, context=context)
    arq_rel = arq_dir or "core/arq"
    console.print(f"[green]✓[/green] ARQ client scaffolded → [bold]{arq_rel}/[/bold]")

    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print("  1. Register [cyan]EmailContent[/cyan] in [cyan]system/admin[/cyan]")
    console.print("  2. Run [cyan]python manage.py makemigrations[/cyan]")
    console.print("  3. Set [cyan]ARQ_REDIS_URL[/cyan] in your project settings")
    console.print("  4. Reuse [cyan]NotificationService[/cyan] from features like booking, forms, or other workflows")
