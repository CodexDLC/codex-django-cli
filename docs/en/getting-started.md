<!-- DOC_TYPE: GUIDE -->

> This repository documents the standalone `codex-django-cli` package. It provides project scaffolding and blueprints.

# Getting Started

## Why not `django-admin startproject`?

Unlike Django's default utility which creates an entirely empty structure, `codex-django` generates a fully production-ready architecture:
- **Modern Frontend Stack:** Comes pre-wired with **HTMX 2.x** and **Alpine.js**, modular CSS, and base themes.
- **Ready-to-use Core/System:** Includes pre-configured ASGI, Redis, standard notifications, SEO mixins, and a generated `.env` file with Fernet encryption keys.
- **Interactive Menu:** You don't need to memorize long CLI flags. Run `codex-django menu` to interactively launch wizards for initializing projects, adding features, or creating Docker/CI files.

## Install The CLI

Install the CLI globally using `uv` (recommended):

```bash
uv tool install codex-django-cli
```

Or using classic `pip`:

```bash
pip install codex-django-cli
```

`codex-django-cli` requires Python 3.12+.

## Scaffold A New Project

The CLI registers the `codex-django` command. You can use the interactive menu or pass explicit flags for automation:

```bash
# 1. Interactive wizard
codex-django menu

# 2. Fast path with explicit flags for power users:
codex-django init myproject --i18n --languages en,ru --with-cabinet --with-booking
cd myproject
# Make sure you are in a dedicated virtual environment
pip install -e .
python src/myproject/manage.py migrate
python src/myproject/manage.py runserver_plus
```

> [!IMPORTANT]
> **The `codex-django` Dependency**: The `pip install -e .` step is critical! It downloads and installs the core `codex-django` runtime library. The `codex-django-cli` only generates the scaffolding (the architectural wiring). The actual engine that powers HTMX responses, Cabinet templates, notifications, and SEO lives inside `codex-django`. **Without it, your scaffolded project will not work.**

The interactive menu is also accessible simply by typing `codex-django`. It is incredibly useful when you want to choose i18n modes, set up specific language codes, or toggle optional modules without memorizing flags. But if you know what you want, the explicit flags are the fastest way.

If you already have a scaffolded project, extend it incrementally using the CLI menu:

```bash
codex-django menu
# -> Choose "🧩  Scaffolding (Apps/Modules)"
# -> Select project target
# -> Choose "Basic app", "Client Cabinet", or "Booking"
```

The scaffolding engine generates files and prints the exact follow-up steps you need to wire them into the core `settings.py`, `urls.py`, and `admin.py`.

## Typical Development Loop for the CLI

If you are developing the CLI itself, use standard `uv` commands:

```bash
uv sync --extra dev
uv run python tools/dev/check.py
```
