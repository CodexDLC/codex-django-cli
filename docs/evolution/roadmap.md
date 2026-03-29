# Roadmap

## Platform Scaffolding Extraction

### Status
Planned

### Goal
Extract the deployment, CI/CD, and developer-tooling scaffold layer from `codex-django-cli` into a dedicated reusable library.

### Why
The current repository contains two different concerns:

- Django-specific project and feature scaffolding
- reusable operational scaffolding such as deploy templates, CI workflow generation, and pre-commit/bootstrap quality tooling

The operational layer should become reusable across multiple Codex products instead of staying coupled to the Django CLI.

### Target consumers
- `codex-django` via optional CLI/dev tooling integration
- `codex-bot` via optional scaffolding dependency in the future
- `codex-fastapi` via optional scaffolding dependency in the future

### Planned extraction scope
- deployment templates and stack blueprints
- CI/CD workflow generation
- pre-commit and quality-gate bootstrap files
- repository automation scaffolds that are not Django-runtime specific

### What stays in codex-django-cli
- interactive `codex-django` command flow
- Django project initialization
- Django app and feature blueprints
- templates that are tightly coupled to `codex-django` runtime behavior

### Expected outcome
A smaller `codex-django-cli` focused on Django scaffolding, plus a separate reusable library that can be installed as an optional dependency by multiple Codex framework packages.
