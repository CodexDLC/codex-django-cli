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

## Modules

| Module | Extra | Description |
| :--- | :--- | :--- |
| `codex_django_cli.main` | - | Interactive entrypoint, menu flow, and legacy command dispatch. |
| `codex_django_cli.engine` | - | Blueprint renderer and file generation engine for scaffold assets. |
| `codex_django_cli.commands` | - | Init, app scaffolding, deploy helpers, quality tools, and notifications bootstrap. |
| `codex_django_cli.blueprints` | - | Packaged project, feature, deployment, and repository templates used by the CLI. |

## Documentation

Full docs with project structure, scaffold workflow, architecture, and API reference:

**[https://codexdlc.github.io/codex-django-cli/](https://codexdlc.github.io/codex-django-cli/)**

## Part of the Codex ecosystem

| Package | Role |
| :--- | :--- |
| [codex-core](https://github.com/CodexDLC/codex-core) | Foundation — DTOs, settings, logging, and shared developer tooling. |
| [codex-platform](https://github.com/CodexDLC/codex-platform) | Infrastructure — Redis, streams, workers, notifications, and runtime platform services. |
| [codex-services](https://github.com/CodexDLC/codex-services) | Business logic — reusable booking and service-layer engines. |
| [codex-django](https://github.com/CodexDLC/codex-django) | Django runtime layer — reusable apps, mixins, i18n, SEO, and framework integrations. |
| **codex-django-cli** | Project assembly layer — CLI scaffolding, blueprints, and bootstrap workflows for Codex Django projects. |

Each library is fully standalone where appropriate.
Together, `codex-django` and `codex-django-cli` provide the runtime layer and project assembly workflow for Codex-based Django applications.
