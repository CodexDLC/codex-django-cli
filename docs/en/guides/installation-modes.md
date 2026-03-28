<!-- DOC_TYPE: GUIDE -->

# Installation Modes

> In the split-package layout, install `codex-django-cli` for scaffold workflows; it pulls in `codex-django` runtime support.

## Choose The Smallest Install That Matches The Job

Use `codex-django` in one of three practical modes:

1. Runtime library mode for projects that only need reusable Django modules.
2. Scaffold mode for developers generating or extending a Codex-shaped project.
3. Full contributor mode for people changing the library itself.

## Runtime Library Mode

Install only the package and the extras your Django project actually uses:

```bash
pip install codex-django
pip install "codex-django[notifications]"
pip install "codex-django[django-redis]"
pip install "codex-django[all]"
```

This mode is for teams consuming the runtime modules such as `core`, `system`, `booking`, `notifications`, and `cabinet`.

## Scaffold Mode

Use the bundled CLI when you want to generate a new project or add feature scaffolds to an existing one:

```bash
codex-django init myproject
codex-django add-client-cabinet --project myproject
codex-django add-booking --project myproject
codex-django add-notifications --app system --project myproject
```

The CLI is packaged together with the runtime library today, but operationally it should be treated as project-construction tooling rather than business runtime code.

## Contributor Mode

When you are changing `codex-django` itself, sync the full development environment:

```bash
uv sync --extra dev
uv run pytest
uv run mypy src/
uv run pre-commit run --all-files
uv build --no-sources
```

## Production Guidance

- Put generated project code into your application repository.
- Treat scaffolding as a build-time or developer-time activity.
- Keep production images focused on the dependencies your runtime application actually needs.
- Avoid making the deployed app container depend on interactive CLI flows unless that is an explicit operational choice.

## Where To Go Next

- Read [Runtime vs CLI](./runtime-vs-cli.md) for the boundary between reusable modules and project-construction tooling.
- Read [Project Structure](./project-structure.md) for the layout of a scaffolded project.
- Read [Blueprint Workflow](./blueprints-and-scaffolding.md) for how CLI commands map to generated output.
