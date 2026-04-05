"""Thin wrappers around questionary prompts."""

from __future__ import annotations

from typing import cast

import questionary

MODULE_LABELS: dict[str, str] = {
    "cabinet": "Cabinet app-layer",
    "conversations": "Conversations feature",
    "booking_engine": "Booking engine",
    "booking_cabinet": "Booking cabinet integration",
    "public_booking": "Public booking pages",
    "sw": "Service worker files (sw.js, manifest)",
}


def parse_language_codes(raw: str | None) -> list[str]:
    if not raw:
        return []
    normalized: list[str] = []
    for item in raw.split(","):
        code = item.strip().lower().replace("_", "-")
        if code and code not in normalized:
            normalized.append(code)
    return normalized


def ask_main_action() -> str | None:
    return cast(
        str | None,
        questionary.select(
            "Scaffold Menu — repo generators and Django project bootstrap. Runtime actions live in manage.py menu.",
            choices=[
                "🚀  Init Django project",
                "🧩  Extend existing Django project",
                "🏗  Generate deployment files",
                "🔁  Generate CI/CD workflows",
                "🪝  Configure pre-commit",
                "📦  Generate repo config files",
                "❌  Exit",
            ],
        ).ask(),
    )


def ask_confirm_action(message: str) -> bool:
    return bool(questionary.confirm(message, default=False).ask())


def ask_repo_config_action() -> str | None:
    return cast(
        str | None,
        questionary.select(
            "Repo config generator — create root comparison files when pyproject/.env.example already exist.",
            choices=[
                "Generate pyproject.toml + .env.example",
                "Generate pyproject.toml only",
                "Generate .env.example only",
                "← Back",
            ],
        ).ask(),
    )


def ask_deploy_mode() -> str | None:
    return cast(
        str | None,
        questionary.select(
            "Deployment scaffold — choose topology for files under deploy/ or .github/workflows/:",
            choices=[
                questionary.Choice(
                    "Standalone  (one project = full stack: nginx, redis, postgres)", value="standalone"
                ),
                questionary.Choice("Stack       (multiple projects share nginx, redis, worker)", value="stack"),
                "← Back",
            ],
        ).ask(),
    )


def ask_domain_name() -> str | None:
    value = questionary.text("Domain name used in generated deploy templates:", default="example.com").ask()
    return cast(str | None, value)


def ask_deploy_services() -> dict[str, bool] | None:
    result = questionary.checkbox(
        "Optional services for generated deployment files:",
        choices=[
            questionary.Choice("ARQ Worker (async tasks / notifications)", value="worker", checked=False),
            questionary.Choice("Telegram Bot", value="bot", checked=False),
        ],
        instruction="Space to toggle, Enter to confirm, Esc to cancel",
    ).ask()
    if result is None:
        return None
    selected = result or []
    return {"with_worker": "worker" in selected, "with_bot": "bot" in selected}


def ask_project_name() -> str | None:
    return cast(str | None, questionary.text("Project name (snake_case):").ask())


def ask_target_project(projects: list[str]) -> str | None:
    return cast(str | None, questionary.select("Select Django project from src/:", choices=[*projects, "← Back"]).ask())


def ask_install_modules(*, mode: str, installed_modules: dict[str, bool] | None = None) -> list[str] | None:
    installed_modules = installed_modules or {}
    if mode == "init":
        prompt = "Init project — choose modules for the new Django project:"
        module_names = ["cabinet", "conversations", "booking_engine", "booking_cabinet", "sw"]
        checked = {"cabinet", "conversations"}
    else:
        prompt = "Extend project — choose modules to add into the existing Django project:"
        module_names = ["cabinet", "conversations", "booking_engine", "booking_cabinet", "sw"]
        checked = set()
    choices = []
    for module_name in module_names:
        label = MODULE_LABELS[module_name]
        if installed_modules.get(module_name):
            label = f"{label} (already detected)"
        choices.append(questionary.Choice(label, value=module_name, checked=module_name in checked))
    result = questionary.checkbox(
        prompt, choices=choices, instruction="Space to toggle, Enter to confirm, Esc to cancel"
    ).ask()
    if result is None:
        return None
    return cast(list[str], result)


def ask_existing_module_action(module_label: str) -> str | None:
    return cast(
        str | None,
        questionary.select(
            f"Module '{module_label}' is already detected. Choose what to do:",
            choices=[
                questionary.Choice("Reinstall over existing files", value="install"),
                questionary.Choice("Generate compare copy in _scaffold_compare", value="compare"),
                "← Back",
            ],
        ).ask(),
    )


def ask_confirm_plan(summary: str) -> bool:
    result = questionary.confirm(f"Apply install plan: {summary}?", default=True).ask()
    return bool(result)


def ask_app_name(prompt: str = "App name (snake_case):", default: str = "") -> str | None:
    return cast(str | None, questionary.text(prompt, default=default).ask())


def ask_init_mode() -> str | None:
    return cast(
        str | None,
        questionary.select(
            "Init project — choose generation mode:",
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


def ask_init_modules() -> list[str] | None:
    return ask_install_modules(mode="init")


def ask_extension_modules(installed_modules: dict[str, bool] | None = None) -> list[str] | None:
    return ask_install_modules(mode="extend", installed_modules=installed_modules)


def ask_enable_i18n() -> bool:
    result = questionary.confirm(
        "Enable i18n / modular locale support? Useful even with one language.", default=False
    ).ask()
    return bool(result)


def ask_languages(enable_i18n: bool) -> list[str]:
    if not enable_i18n:
        return ["en"]
    mode = questionary.select(
        "I18n setup — how should the project define its language codes?",
        choices=[
            questionary.Choice("Quick pick recommended languages", value="preset"),
            questionary.Choice("Enter language codes manually", value="manual"),
            "← Back",
        ],
        default="preset",
    ).ask()
    if mode == "← Back":
        return ["en"]
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
        instruction="Space to toggle, Enter to confirm, Esc to cancel",
    ).ask()
    return cast(list[str], results) or ["en"]


def ask_with_cloud_db() -> bool:
    return bool(
        questionary.confirm(
            "Include Cloud DB support (Neon/Heroku/Render)? Adds dj-database-url dependency.",
            default=False,
        ).ask()
    )
