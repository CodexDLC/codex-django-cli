<!-- Type: LANDING -->
# codex-django-cli

[![PyPI](https://img.shields.io/pypi/v/codex-django-cli)](https://pypi.org/project/codex-django-cli/)
[![Python](https://img.shields.io/pypi/pyversions/codex-django-cli)](https://pypi.org/project/codex-django-cli/)
[![License](https://img.shields.io/badge/license-Apache--2.0-green)](https://github.com/CodexDLC/codex-django-cli/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-codexdlc.github.io-blue)](https://codexdlc.github.io/codex-django-cli/)

CLI scaffolding package for `codex-django` projects.
It provides the interactive `codex-django` command, project blueprints, and bootstrap workflows used to assemble Codex Django applications.

---

## Install

```bash
# CLI only
pip install codex-django-cli

# Recommended end-user install via the runtime package
pip install "codex-django[cli]"
```

Requires Python 3.12 or newer.

## Development

```bash
uv sync --extra dev
uv run pytest tests/unit/cli tests/integration/cli
uv build --no-sources
```

Install-chain e2e smoke:

```bash
# Local dev chain (editable codex-django-cli + editable ../codex-django)
uv run pytest tests/e2e/cli/test_install_chains_e2e.py -m e2e -k local_dev_chain -v

# Optional override for runtime checkout path
export CODEX_DJANGO_CHECKOUT=/absolute/path/to/codex-django

# Online-install chain (PyPI codex-django-cli + local codex-django wheel)
export CODEX_DJANGO_E2E_ONLINE=1
export CODEX_DJANGO_WHEEL=/absolute/path/to/codex_django-*.whl
uv run pytest tests/e2e/cli/test_install_chains_e2e.py -m e2e -k online_install_chain -v

# Optional: test a specific PyPI target (version, index alias, etc.)
export CODEX_DJANGO_CLI_PYPI_SPEC='codex-django-cli'
```

Requires Python 3.12 or newer.

## Quick Start

```bash
# Create a new project
codex-django init myproject

# Or install through codex-django and use the same CLI entrypoint
pip install "codex-django[cli]"
codex-django init myproject --i18n --languages en,ru
```

## CLI flags

```bash
codex-django init myproject [OPTIONS]

Options:
  --i18n / --no-i18n          Enable translation-aware scaffold (default: off)
  --languages CODES           Comma-separated language codes, e.g. en,ru,de
  --with-booking              Include booking engine + cabinet integration
  --with-notifications        Include ARQ worker + email notification scaffold
  --with-public-booking       Include public-facing booking pages
  --without-cabinet           Skip cabinet scaffold
  --without-conversations     Skip conversations feature
  --with-sw                   Include service worker + manifest
  --with-cloud-db             Add dj-database-url for cloud DB (Neon/Heroku/Render)
  --overwrite                 Overwrite existing files
```

## Modules

| Module | Extra | Description |
| :--- | :--- | :--- |
| `codex_django_cli.main` | - | Interactive entrypoint, menu flow, and CLI argument dispatch. |
| `codex_django_cli.engine` | - | Blueprint renderer and file generation engine for scaffold assets. |
| `codex_django_cli.commands` | - | Init, install orchestration, deploy helpers, and quality tools. |
| `codex_django_cli.blueprints` | - | Packaged project, cabinet, feature, deployment, and repository templates. |

## Documentation

Full docs with project structure, scaffold workflow, architecture, and API reference:

**[https://codexdlc.github.io/codex-django-cli/](https://codexdlc.github.io/codex-django-cli/)**

## Part of the Codex ecosystem

| Package | Role |
| :--- | :--- |
| [codex-core](https://github.com/codexdlc/codex-core) | Foundation — immutable DTOs, PII masking, env settings |
| [codex-platform](https://github.com/codexdlc/codex-platform) | Infrastructure — Redis, Streams, ARQ workers, Notifications |
| [codex-ai](https://github.com/codexdlc/codex-ai) | LLM layer — unified async interface for OpenAI, Gemini, Anthropic |
| [codex-services](https://github.com/codexdlc/codex-services) | Business logic — Booking engine, CRM, Calendar |

Each library is **fully standalone** — install only what your project needs.
Together they form the backbone of **[codex-bot](https://github.com/codexdlc/codex-bot)**
(Telegram AI-agent infrastructure built on aiogram) and
**codex-django** (Django integration layer and scaffolding toolkit).
