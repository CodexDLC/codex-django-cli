# codex-django-cli

Standalone CLI package for `codex-django`.

It owns the interactive `codex-django` command, blueprint rendering engine, scaffold commands, and CLI-focused tests/docs. The generated project code may still import `codex_django.*` runtime modules from `codex-django`; that compatibility is intentional.

## Install

```bash
pip install codex-django-cli
```

For local development alongside the sibling runtime repository:

```bash
uv sync --extra dev
uv run pytest tests/unit/cli tests/integration/cli
uv build --no-sources
```

## Scope

- `codex_django_cli.main`: entrypoint and menu flow
- `codex_django_cli.engine`: blueprint rendering and file generation
- `codex_django_cli.commands.*`: scaffold/init/deploy helpers
- `codex_django_cli.blueprints`: packaged templates, static files, and scaffold assets

The runtime library remains in `codex-django`.
