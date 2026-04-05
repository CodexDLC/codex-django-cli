<!-- DOC_TYPE: CONCEPT -->

# CLI Blueprints

## Purpose

The `blueprints/` directory is the generation knowledge base of the CLI.
If `CLIEngine` is the renderer, blueprints are the architectural source material it renders.

They define not only file contents, but also the intended output topology of a generated project.
Because of that, blueprints are closer to a declarative construction system than to a simple templates folder.

## Why Blueprints Matter

The most important thing about the CLI is not the menu itself.
It is the fact that project structure, project extension, repository shell generation, and deployment files are all driven from reusable blueprint trees.

This means the CLI architecture is fundamentally template-centric:

- commands choose a blueprint family or subtree
- the engine renders it with context
- the generated tree becomes part of the target repository or project

So understanding the CLI means understanding how blueprints are partitioned.

## Top-Level Blueprint Families

The current blueprint space is split into six main families:

- `repo`
- `project`
- `cabinet`
- `features`
- `apps`
- `deploy`

These are not arbitrary folders.
They correspond to different layers of output responsibility.

### `repo`

`repo/` contains repository-level scaffolding.
This is the outer shell around a generated project and includes files such as:

- `pyproject.toml`
- `.env.example`
- repo-level docs and tools
- shared repository helper templates

This layer answers:
"What files belong to the repository as a whole, regardless of the internal Django app tree?"

### `project`

`project/` contains the base Django project scaffold that lands in `src/<project_name>/`.
This includes the initial structure for:

- `core`
- `system`
- `features`
- `templates`
- `static`
- `manage.py`

This family defines the starting runtime architecture of a fresh codex-django project before optional install layers are applied.

### `cabinet`

`cabinet/` is now a dedicated top-level blueprint family.
It contains the project-local cabinet shell, views, services, templates, static assets, and routing glue that used to be partially embedded under `project/`.

This matters because cabinet is no longer just an implementation detail of the base project scaffold.
It is an explicit extension layer that can be installed, reinstalled, or compared independently.

### `features`

`features/` contains advanced or compound feature scaffolds such as:

- `booking`
- `booking_core`
- `booking_public`
- `conversations`
- `client_cabinet`

These blueprints are more architectural than `apps/default` because they often modify several target areas at once.

For example:

- `booking_core` defines the booking domain and service layer
- `booking_public` adds public booking pages and multi-step templates
- `conversations` injects feature code plus cabinet-facing integration
- `client_cabinet` remains part of the blueprint tree as a specialized cabinet-facing extension surface

So `features/` is the layer where the CLI expresses cross-cutting feature bundles rather than isolated apps.

### `apps`

`apps/` contains reusable blueprints for adding a standard feature app to an existing project.
In the current CLI shape it is no longer the main interactive growth path, but it remains part of the blueprint library as a lower-level reusable scaffold family.

This layer answers:
"How do we add one regular app in the canonical codex-django shape when we need that lower-level pattern?"

### `deploy`

`deploy/` contains deployment-specific scaffolding such as Docker files and workflow templates.
This layer is intentionally separated from `project/` because deployment output has a different lifecycle than runtime application code.

It answers:
"What operational infrastructure should be generated around the project?"

## Architectural Pattern

The blueprint hierarchy reveals an implicit generation model:

1. generate repository shell when needed
2. generate base project
3. optionally install cabinet and feature layers
4. optionally generate deployment or CI/CD support
5. optionally use lower-level app blueprints for specialized scaffolding

This is not just a file-copy pipeline.
It is a staged project-construction model.

## Jinja And Structural Semantics

Blueprints are not only raw files:

- `.j2` files are rendered with context
- non-template files are copied as-is
- folder placement encodes where generated code should live

This means the blueprint tree carries two kinds of meaning at once:

- content semantics: what each file should contain
- placement semantics: where in the output architecture it belongs

## Runtime Flow

```mermaid
flowchart TD
    A["CLI command"] --> B["select blueprint family or subtree"]
    B --> C["CLIEngine.scaffold(...)"]
    C --> D["walk blueprint tree"]
    D --> E["render .j2 files with context"]
    D --> F["copy static files"]
    E --> G["target project structure"]
    F --> G
```

## Role In The CLI

Blueprints are the most durable part of the CLI architecture.
Menus, commands, and prompts may evolve, but the blueprint families define the long-term contract of what the tool generates.

That is why blueprint documentation is important even if the CLI later becomes its own package:
the blueprints encode the actual shape of the generated ecosystem.
