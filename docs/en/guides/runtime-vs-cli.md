<!-- DOC_TYPE: GUIDE -->

# Runtime vs CLI

> After the package split, the CLI layer lives in `codex-django-cli` while the runtime layer stays in `codex-django`.

## The Two Layers Of codex-django

`codex-django` contains two related but different layers:

- Runtime modules that are imported by Django projects after installation.
- CLI/scaffolding tooling that creates or extends those projects.

Understanding that split keeps the documentation easier to navigate and helps teams decide what belongs in production.

## Runtime Layer

The runtime layer is what your Django app imports and executes:

- `codex_django.core`
- `codex_django.system`
- `codex_django.notifications`
- `codex_django.booking`
- `codex_django.cabinet`

These modules define reusable models, mixins, selectors, adapters, Redis helpers, templates, and integration points.

## CLI Layer

The CLI layer is what developers use to create and evolve project structure:

- `codex_django.cli.main`
- command handlers under `codex_django.cli.commands`
- blueprint trees under `codex_django.cli.blueprints`
- rendering logic in `codex_django.cli.engine`

This layer is about generation, orchestration, and project assembly.

## How To Think About The Boundary

- Runtime code stays in the long-lived application path of the generated project.
- CLI code runs before or around that runtime path to create files, wiring, and defaults.
- Generated output becomes your project's codebase and can then evolve independently.

## Practical Rule

If the question is "what does my Django app import at runtime?", stay in the runtime modules.
If the question is "what command creates or extends this structure?", move into the CLI guides and architecture pages.

## Related Pages

- [Getting Started](../getting-started.md)
- [Installation Modes](./installation-modes.md)
- [Project Structure](./project-structure.md)
- [CLI Architecture](../architecture/cli/README.md)
