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

The current blueprint space is split into seven main families:

- `repo`
- `project`
- `cabinet`
- `cabinet_booking`
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

`cabinet/` is a dedicated top-level blueprint family.
It contains the project-local cabinet shell: views, services, templates, static assets, routing glue, and a `fixtures/` subdirectory with demo data.

Key sub-paths:

- `services/analytics.py.j2` — `AnalyticsService` with dashboard providers and `get_report_page()` returning typed `ReportPageData`.
- `fixtures/demo_analytics.json.j2` — demo numbers and labels for the analytics dashboard. Rendered once at scaffold time; the service reads from this file at runtime. Replace service method bodies with real DB queries and delete the fixture when ready.

This family does **not** include any booking-specific cabinet views — those live in `cabinet_booking/`.

### `cabinet_booking`

`cabinet_booking/` is scaffolded only when `with_booking=True`.
It contains the booking-cabinet integration layer: booking bridge, booking views, services, and templates that extend the base cabinet with appointment management.

Keeping it separate from `cabinet/` means a standard init without booking produces a clean cabinet with zero booking artefacts.

### `features`

`features/` contains advanced or compound feature scaffolds:

- `booking_core` — booking domain models, providers, runtime services, and settings model.
- `booking_public` — public-facing booking pages and multi-step flow templates.
- `conversations` — conversations models, migrations, services, selectors, and cabinet integration.
- `notifications` — ARQ worker scaffolding, `EmailContent` model, and notification selectors.
- `client_cabinet` — specialized cabinet-facing extension for client-space views.

These blueprints are more architectural than `apps/default` because they often modify several target areas at once.
`features/` is the layer where the CLI expresses cross-cutting feature bundles rather than isolated apps.

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

## Jinja Context Variables

Every blueprint is rendered with the following context dictionary.
Templates use these variables in `{%- if ... %}` blocks to conditionally include or exclude sections.

| Variable | Type | Description |
| :--- | :--- | :--- |
| `project_name` | `str` | Snake-case project name used for app `name =` and imports. |
| `enable_i18n` | `bool` | Render `gettext_lazy` imports and `SET_LANGUAGE` URLs. |
| `languages` | `list[str]` | Language codes, e.g. `["en", "ru"]`. First code is the default. |
| `with_cabinet` | `bool` | Scaffold the `cabinet/` blueprint. |
| `with_booking` | `bool` | Scaffold `cabinet_booking/` + `features/booking_core`. |
| `with_notifications` | `bool` | Scaffold `features/notifications` + `settings/modules/notifications.py`. |
| `with_conversations` | `bool` | Scaffold `features/conversations`. |
| `with_public_booking` | `bool` | Scaffold `features/booking_public`. |
| `with_sw` | `bool` | Scaffold service worker + manifest. |
| `with_cloud_db` | `bool` | Add `dj-database-url` dependency in `pyproject.toml`. |

## Architectural Principles

Generated code follows the **Thin Views / Service Layer** pattern:

- **Views** only call service or selector methods and return HTTP responses.
- **`services/<domain>.py`** — write operations and business logic. Each method is independently testable without HTTP context.
- **`selectors/<domain>.py`** — read-only queries. Each method is independently testable without HTTP context.

This means a developer can unit-test `AnalyticsService.get_kpi_metrics()` or `BookingCabinetWorkflowService.get_modal_state()` without starting a Django server.

## Role In The CLI

Blueprints are the most durable part of the CLI architecture.
Menus, commands, and prompts may evolve, but the blueprint families define the long-term contract of what the tool generates.

That is why blueprint documentation is important even if the CLI later becomes its own package:
the blueprints encode the actual shape of the generated ecosystem.
