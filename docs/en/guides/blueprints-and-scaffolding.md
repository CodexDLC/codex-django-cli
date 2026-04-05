<!-- DOC_TYPE: GUIDE -->

# Blueprint Workflow

## How Scaffold Commands Work

Every major CLI flow translates a developer intention into one or more blueprint renders.

Typical flow:

1. Choose a flow such as `init`, project extension from the menu, or repository config generation.
2. The command or orchestration layer resolves the relevant blueprint family.
3. `CLIEngine` renders templates and copies static assets into the target project or repository.
4. The command prints follow-up integration steps you still need to apply manually.

## Blueprint Families

The CLI blueprint tree is organized by the kind of output it creates:

- `repo` for repository shell files
- `project` for the base Django project layout
- `cabinet` for the dedicated project-local cabinet layer
- `features` for cross-cutting functional bundles
- `apps` for lower-level app building blocks
- `deploy` for operational and deployment-oriented output

## Safe Working Pattern

Use this order whenever you scaffold new functionality:

1. Generate the files.
2. Read the printed follow-up instructions.
3. Wire settings, admin, URLs, and migrations.
4. Run local checks before continuing.

## Why This Matters

`codex-django` is not only a package of reusable modules.
It is also a project-construction framework, so the blueprint workflow is part of the product surface.

## Related Pages

- [Getting Started](../getting-started.md)
- [CLI Architecture](../architecture/cli/README.md)
- [CLI Blueprints](../architecture/cli/blueprints.md)
