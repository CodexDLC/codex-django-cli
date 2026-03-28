"""
handle_generate_deploy
======================
Generates Docker infrastructure and CI/CD files for a project.

Supports two deployment modes:
  - standalone: one project = full stack (nginx, redis, postgres, worker, bot)
  - stack: multiple projects sharing nginx, redis, arq worker
"""

import os
from secrets import token_urlsafe

from rich.console import Console

from codex_django_cli.engine import CLIEngine

console = Console()


def handle_generate_deploy(
    name: str,
    project_root: str,
    deploy_mode: str = "standalone",
    domain_name: str = "example.com",
    with_bot: bool = False,
    with_worker: bool = False,
    with_notifications: bool = False,
    enable_i18n: bool = False,
    cluster_name: str | None = None,
    python_version: str = "3.13",
    generate_docker: bool = True,
    generate_cicd: bool = True,
) -> None:
    """Generate deploy infrastructure files and CI/CD workflows.

    Args:
        name: Project name used in templates and generated paths.
        project_root: Repository root where deploy assets should be written.
        deploy_mode: Deployment topology, for example ``standalone`` or ``stack``.
        domain_name: Public domain used in generated configs.
        with_bot: Whether Telegram bot assets should be included.
        with_worker: Whether worker assets should be included.
        with_notifications: Whether notification-related deploy config is needed.
        enable_i18n: Whether i18n-aware routing/templates should influence templates.
        cluster_name: Optional cluster identifier for shared-stack mode.
        python_version: Python version string injected into templates.
        generate_docker: Whether Docker assets should be generated.
        generate_cicd: Whether CI/CD workflow files should be generated.
    """
    engine = CLIEngine()

    context = {
        "project_name": name,
        "secret_key": token_urlsafe(50),
        "domain_name": domain_name,
        "python_version": python_version,
        "with_bot": with_bot,
        "with_worker": with_worker,
        "with_notifications": with_notifications,
        "enable_i18n": enable_i18n,
        "deploy_mode": deploy_mode,
        "cluster_name": cluster_name or name,
    }

    deploy_dir = os.path.join(project_root, "deploy")
    workflows_dir = os.path.join(project_root, ".github", "workflows")

    if generate_docker:
        engine.scaffold("deploy/shared", target_dir=deploy_dir, context=context, overwrite=True)
        engine.scaffold(f"deploy/{deploy_mode}", target_dir=deploy_dir, context=context, overwrite=True)
        console.print(f"[green]✓[/green] Docker files generated in [bold]{deploy_dir}[/bold]")

    if generate_cicd:
        engine.scaffold(
            f"deploy/{deploy_mode}_workflows",
            target_dir=workflows_dir,
            context=context,
            overwrite=True,
        )
        console.print(f"[green]✓[/green] CI/CD workflows generated in [bold]{workflows_dir}[/bold]")

    console.print()
    console.print("[bold]Next steps:[/bold]")
    if deploy_mode == "standalone":
        console.print("  1. [cyan]cp .env.example .env[/cyan]  # fill in secrets")
        console.print("  2. [cyan]cd deploy && docker compose up -d[/cyan]  # local dev")
        console.print("  3. Add GitHub Secrets: HOST, USERNAME, SSH_KEY, ENV_FILE, DOMAIN_NAME, REDIS_PASSWORD")
        console.print("  4. Push tag to trigger production deploy: [cyan]git tag v1.0.0 && git push --tags[/cyan]")
    else:
        console.print("  1. [cyan]cp .env.example .env[/cyan]  # fill in shared secrets")
        console.print(
            "  2. [cyan]cd deploy && docker compose -f docker-compose.infra.yml up -d[/cyan]  # start shared infra"
        )
        console.print("  3. [cyan]docker compose -f docker-compose.apps.yml up -d[/cyan]  # start this project")
        console.print("  4. Add GitHub Secrets and configure deploy-cluster.yml for your VPS")
