<!-- DOC_TYPE: API -->

# CLI Public API

The CLI package provides the interactive `codex-django` entrypoint plus the blueprint-rendering machinery used by scaffold commands.

## Main entrypoints

- `codex_django_cli.main` for launching the interactive CLI.
- `codex_django_cli.engine.CLIEngine` for lower-level template rendering and scaffold generation.
- compatibility imports from `codex_django.cli.*` remain available via shim modules in `codex-django`.

## Example

```python
from codex_django_cli.main import main

raise SystemExit(main())
```

For prompt helpers, command handlers, and the lower-level scaffold engine modules, open [CLI internals](internal/cli.md).
