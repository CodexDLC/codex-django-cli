# CLI skill delivery

The editable source is `src/codex_django_cli/agent_skills/resources`. Consumer copies in `.agents/skills/codex-django-cli` are managed by `python -m codex_django_cli.agent_skills`; do not hand-edit their manifest to accept changes. The installer uses hashes and a marked `AGENTS.md` block so update and delete can preserve unrelated user content.

When adding a reference, link it from `resources/SKILL.md` only for tasks that need it. Keep examples tied to current public CLI and engine behavior. Verify package data in both build artifacts, then install a wheel into a clean environment and test its lifecycle against a temporary consumer project.
