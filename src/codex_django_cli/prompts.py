"""
Thin wrappers around questionary prompts.

Isolated here so tests can mock `codex_django_cli.prompts.*`
instead of patching questionary directly.
"""

from __future__ import annotations

from typing import cast

import questionary


def parse_language_codes(raw: str | None) -> list[str]:
    """Parse a comma-separated list of language codes into a normalized list."""
    if not raw:
        return []

    normalized: list[str] = []
    for item in raw.split(","):
        code = item.strip().lower().replace("_", "-")
        if code and code not in normalized:
            normalized.append(code)
    return normalized


def ask_main_action(is_project: bool = False) -> str | None:
    """Ask for the top-level action in the global CLI menu."""
    choices = [
        "🚀  Init new project",
        "🧩  Add feature/extension",
        "❌  Exit",
    ]
    if is_project:
        # In a project, we don't usually need to 'init' a new one from the same root
        # but we'll use a better sub-menu instead
        pass

    return cast(
        str | None,
        questionary.select(
            "Codex Django CLI",
            choices=choices,
        ).ask(),
    )


def ask_project_action() -> str | None:
    """Ask for the main action inside a scaffolded project."""
    return cast(
        str | None,
        questionary.select(
            "Codex Project Menu",
            choices=[
                "🆕  Init new project",
                "🚀  Standard Commands",
                "🧩  Scaffolding (Apps/Modules)",
                "🛡  Quality & Tools",
                "🏁  Deployment Setup",
                "⚙️  Security",
                "❌  Exit",
            ],
        ).ask(),
    )


def ask_standard_command() -> str | None:
    """Ask which standard Django command should be executed."""
    return cast(
        str | None,
        questionary.select(
            "Standard Commands",
            choices=[
                "makemigrations",
                "migrate",
                "createsuperuser",
                "shell",
                "i18n: Generate locale domains",
                "i18n: Compile",
                "← Back",
            ],
        ).ask(),
    )


def ask_quality_tool() -> str | None:
    """Ask which quality helper should be executed."""
    return cast(
        str | None,
        questionary.select(
            "Quality & Tools",
            choices=[
                "Configure pre-commit",
                "Run Project Checker",
                "← Back",
            ],
        ).ask(),
    )


def ask_deploy_option() -> str | None:
    """Ask which deployment assets should be generated."""
    return cast(
        str | None,
        questionary.select(
            "Deployment Setup",
            choices=[
                "Generate Docker + CI/CD",
                "Generate Docker only",
                "Generate CI/CD only",
                "← Back",
            ],
        ).ask(),
    )


def ask_deploy_mode() -> str | None:
    """Ask which deployment topology should be scaffolded."""
    return cast(
        str | None,
        questionary.select(
            "Deploy mode:",
            choices=[
                questionary.Choice(
                    "Standalone  (one project = full stack: nginx, redis, postgres)", value="standalone"
                ),
                questionary.Choice("Stack       (multiple projects share nginx, redis, worker)", value="stack"),
            ],
        ).ask(),
    )


def ask_domain_name() -> str | None:
    """Ask for the deployment domain name."""
    return cast(str | None, questionary.text("Domain name:", default="example.com").ask())


def ask_deploy_services() -> dict[str, bool]:
    """Ask which optional deployment services should be enabled."""
    result = questionary.checkbox(
        "Optional services:",
        choices=[
            questionary.Choice("ARQ Worker (async tasks / notifications)", value="worker", checked=False),
            questionary.Choice("Telegram Bot", value="bot", checked=False),
        ],
    ).ask()
    selected = result or []
    return {"with_worker": "worker" in selected, "with_bot": "bot" in selected}


def ask_project_name() -> str | None:
    """Ask for the new project name."""
    return cast(str | None, questionary.text("Project name (snake_case):").ask())


def ask_target_project(projects: list[str]) -> str | None:
    """Ask which project under ``src/`` should receive the scaffold."""
    return cast(str | None, questionary.select("Select target project:", choices=projects).ask())


def ask_feature() -> str | None:
    """Ask which feature scaffold should be added to a project."""
    return cast(
        str | None,
        questionary.select(
            "Add feature:",
            choices=["Basic app", "Notifications", "Client Cabinet", "Booking (Advanced)", "← Back"],
        ).ask(),
    )


def ask_app_name(prompt: str = "App name (snake_case):", default: str = "") -> str | None:
    """Ask for a feature or app name."""
    return cast(str | None, questionary.text(prompt, default=default).ask())


def ask_init_mode() -> str | None:
    """Ask which project initialization mode should be used."""
    return cast(
        str | None,
        questionary.select(
            "Init type:",
            choices=[
                "⚡  Standard",
                "🧩  Custom (choose modules)",
                questionary.Separator(),
                "🔄  Force reinit — Standard",
                "🔄  Force reinit — Custom",
                questionary.Separator(),
                "← Back",
            ],
        ).ask(),
    )


def ask_init_modules() -> list[str]:
    """Ask which optional modules should be included during init."""
    result = questionary.checkbox(
        "Modules to include:",
        choices=[
            questionary.Choice("Client Cabinet (user portal)", value="cabinet", checked=True),
            questionary.Choice("Booking (Advanced)", value="booking", checked=False),
        ],
    ).ask()
    return result or []


def ask_enable_i18n() -> bool:
    """Ask whether the project should enable i18n / modular locale support."""
    result = questionary.confirm(
        "Enable i18n / modular locale support? Useful even with one language.",
        default=False,
    ).ask()
    return bool(result)


def ask_languages(enable_i18n: bool) -> list[str]:
    """Ask which language codes should be included in the scaffold.

    Args:
        enable_i18n: Whether i18n / modular locale support should be enabled.

    Returns:
        A non-empty list of language codes.
    """
    if not enable_i18n:
        return ["en"]

    mode = questionary.select(
        "How should the project define its language codes?",
        choices=[
            questionary.Choice("Quick pick recommended languages", value="preset"),
            questionary.Choice("Enter language codes manually", value="manual"),
        ],
        default="preset",
    ).ask()

    if mode == "manual":
        raw_codes = cast(
            str | None,
            questionary.text(
                "Language codes (comma-separated, e.g. en, ru, de-at, ja). First code becomes default.",
                default="en",
            ).ask(),
        )
        return parse_language_codes(raw_codes) or ["en"]

    results = questionary.checkbox(
        "Select language codes to support. You can keep only one if that is your base setup:",
        choices=[
            questionary.Choice("English (en)", value="en", checked=True),
            questionary.Choice("Russian (ru)", value="ru", checked=False),
            questionary.Choice("German (de)", value="de", checked=False),
            questionary.Choice("Ukrainian (uk)", value="uk", checked=False),
        ],
    ).ask()
    return cast(list[str], results) or ["en"]
