<!-- DOC_TYPE: LANDING -->

# codex-django-cli

<div class="cdx-hero">
  <p class="cdx-eyebrow">Codex Django CLI</p>
  <h1>Project assembly, scaffold generation, and developer workflows for Codex-shaped Django projects.</h1>
  <p class="cdx-lead">
    <code>codex-django-cli</code> owns the interactive <code>codex-django</code> command, blueprint rendering,
    project bootstrap flows, feature scaffolding, deployment helpers, and CLI-focused quality tooling.
    Generated projects still target the <code>codex_django.*</code> runtime API from
    <code>codex-django</code>.
  </p>
  <div class="cdx-actions">
    <a class="md-button md-button--primary" href="./en/getting-started/">Getting Started</a>
    <a class="md-button" href="./en/guides/runtime-vs-cli/">Runtime vs CLI</a>
    <a class="md-button" href="./en/api/cli/">API Reference</a>
  </div>
</div>

## Why Not `django-admin startproject`?

<div class="cdx-grid cdx-grid-2">
  <div class="cdx-card">
    <h3>Production-ready Architecture</h3>
    <p>We don't just create an empty folder. <code>codex-django init</code> scaffolds a robust, modern baseline: an <strong>HTMX 2.x + Alpine.js</strong> frontend stack, a configured <strong>Redis/ASGI</strong> core, standard <code>system/</code> apps with SEO and notifications, and secure <code>.env</code> handling with Fernet encryption keys.</p>
  </div>
  <div class="cdx-card">
    <h3>The Interactive Menu</h3>
    <p>Just run <code>codex-django menu</code>. Inside your project, it provides a context-sensitive interface to scaffold new modules, generate Docker/CI files, build translation domains, or run quality checks without memorizing commands or flags.</p>
  </div>
</div>

## Install

Install globally using `uv` (recommended) to use it as a developer tool:

```bash
uv tool install codex-django-cli
```

Or via classic pip:

```bash
pip install codex-django-cli
```

## Quick Start

Launch the interactive project wizard:

```bash
# Launch the global interactive menu
codex-django menu
```

Or initialize explicitly using flags for CI/CD or fast scaffolding:

```bash
codex-django init myproject --i18n --languages en,ru --with-cabinet --with-booking
cd myproject
# Make sure you are in a dedicated virtual environment
pip install -e .
python src/myproject/manage.py migrate
python src/myproject/manage.py runserver_plus
```

Add modular features incrementally to an existing project:

```bash
codex-django menu
# Choose "🧩  Scaffolding (Apps/Modules)" -> Select "Client Cabinet", "Booking", etc.
```

## Start Here

<div class="cdx-grid cdx-grid-3">
  <div class="cdx-card">
    <h3>Bootstrap a project</h3>
    <p>Create a new Codex Django project skeleton with repo files, settings, templates, and app structure.</p>
    <p><a href="./en/getting-started/">Open getting started</a></p>
  </div>
  <div class="cdx-card">
    <h3>Extend an existing project</h3>
    <p>Add feature apps, booking, cabinet, notifications, and deployment assets on top of an existing scaffold.</p>
    <p><a href="./en/guides/blueprints-and-scaffolding/">Open blueprint guide</a></p>
  </div>
  <div class="cdx-card">
    <h3>Read the CLI API</h3>
    <p>Jump directly to the Python entrypoints, scaffold engine, prompt helpers, and command modules.</p>
    <p><a href="./en/api/cli/">Browse API reference</a></p>
  </div>
</div>

## Choose A Path

<div class="cdx-grid cdx-grid-2">
  <div class="cdx-card">
    <h3>For project builders</h3>
    <ul>
      <li><a href="./en/getting-started/">Getting Started</a></li>
      <li><a href="./en/guides/installation-modes/">Installation Modes</a></li>
      <li><a href="./en/guides/blueprints-and-scaffolding/">Blueprint Workflow</a></li>
      <li><a href="./en/guides/runtime-vs-cli/">Runtime vs CLI</a></li>
    </ul>
  </div>
  <div class="cdx-card">
    <h3>For maintainers</h3>
    <ul>
      <li><a href="./en/architecture/cli/README/">Architecture Overview</a></li>
      <li><a href="./en/architecture/cli/entrypoints/">CLI Entrypoints</a></li>
      <li><a href="./en/architecture/cli/blueprints/">Blueprint Architecture</a></li>
      <li><a href="./en/api/internal/cli/">Internal Modules</a></li>
    </ul>
  </div>
</div>

## CLI Layers (Module Map)

<div class="cdx-grid cdx-grid-3">
  <div class="cdx-card">
    <h3><code>main</code></h3>
    <p>Top-level mode selection, interactive routing, legacy subcommand parsing, and project-context dispatch.</p>
    <p><a href="./en/architecture/cli/entrypoints/">Architecture</a> · <a href="./en/api/cli/">API</a></p>
  </div>
  <div class="cdx-card">
    <h3><code>commands</code></h3>
    <p>Concrete scaffold handlers for project init, app generation, booking, notifications, deploy, and quality flows.</p>
    <p><a href="./en/architecture/cli/commands/">Architecture</a> · <a href="./en/api/internal/cli/">API</a></p>
  </div>
  <div class="cdx-card">
    <h3><code>engine</code></h3>
    <p>Blueprint rendering layer that turns Jinja templates into real repository and project file trees.</p>
    <p><a href="./en/architecture/cli/engine/">Architecture</a> · <a href="./en/api/internal/cli/">API</a></p>
  </div>
  <div class="cdx-card">
    <h3><code>blueprints</code></h3>
    <p>Template asset tree for runtime projects, optional features, deploy files, and shared repository scaffolds.</p>
    <p><a href="./en/architecture/cli/blueprints/">Architecture</a></p>
  </div>
  <div class="cdx-card">
    <h3><code>prompts</code></h3>
    <p>Interactive questionary wrappers used by the menu-driven workflow and tested independently from terminal UX.</p>
    <p><a href="./en/api/internal/cli/">Internal API</a></p>
  </div>
  <div class="cdx-card">
    <h3><code>project output</code></h3>
    <p>The generated repository and Django app structure that this package assembles for downstream application teams.</p>
    <p><a href="./en/architecture/cli/project-output/">Open project output model</a></p>
  </div>
</div>

## Language And Reference Split

<div class="cdx-grid cdx-grid-3">
  <div class="cdx-card">
    <h3>English guides</h3>
    <p>Task-oriented docs for installation, project bootstrap, feature scaffolding, and CLI/runtime boundaries.</p>
    <p><a href="./en/getting-started/">Open English guide</a></p>
  </div>
  <div class="cdx-card">
    <h3>Russian guides</h3>
    <p>Russian-language guide layer for the same bootstrap, extension, and architecture workflows.</p>
    <p><a href="./ru/getting-started/">Open Russian guide</a></p>
  </div>
  <div class="cdx-card">
    <h3>Technical reference</h3>
    <p>Source-driven Python reference for the public entrypoints and internal CLI modules.</p>
    <p><a href="./en/api/cli/">Open API reference</a></p>
  </div>
</div>

## Changelog & Migration

- <a href="./changelog/">Read the Changelog</a> for updates on CLI improvements and blueprint changes.

## Related Libraries (Codex Ecosystem)

| Package | Role |
| :--- | :--- |
| [codex-core](https://codexdlc.github.io/codex-core/latest/) | Foundation — immutable DTOs, PII masking, env settings |
| [codex-platform](https://codexdlc.github.io/codex-platform/latest/) | Infrastructure — Redis, Streams, ARQ workers, Notifications |
| [codex-ai](https://codexdlc.github.io/codex-ai/latest/) | LLM layer — unified async interface for OpenAI, Gemini, Anthropic |
| [codex-services](https://codexdlc.github.io/codex-services/latest/) | Business logic — Booking engine, CRM, Calendar |
| [codex-django](https://codexdlc.github.io/codex-django/latest/) | Django runtime layer — reusable apps, mixins, i18n, SEO, and frameworks |

Each library is **fully standalone** — install only what your project needs.
Together they form the backbone of the Codex ecosystem.
