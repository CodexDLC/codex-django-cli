---
name: cli-development
description: Maintain codex-django-cli command flows, blueprints, package delivery, or generated project contracts in this source repository.
---

# Maintain codex-django-cli

This repository owns the `codex-django-cli` generator and its packaged consumer skill under `src/codex_django_cli/agent_skills/resources`. The sibling `codex-django` repository owns runtime APIs and its own skill. Read that sibling as evidence when necessary, but make CLI-owned changes here.

For command routing and module selection, inspect `src/codex_django_cli/main.py`, `src/codex_django_cli/commands/init.py`, and `src/codex_django_cli/commands/install.py`. For generated output, inspect the specific `src/codex_django_cli/blueprints/` subtree and the command context that renders it. `CLIEngine.scaffold` skips existing files unless overwrite is requested; compare-copy output is for review. Keep generator behavior aligned with the generated project's installed runtime contract.

For installer work, read [skill delivery](references/skill-delivery.md). Run focused tests for affected command or blueprint code. When delivery changes, inspect wheel and sdist contents and exercise install, status, update, and delete in an isolated consumer. Preserve the pre-existing worktree diff; this checkout often contains unrelated scaffold changes.
