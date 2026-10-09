# Blueprint Notes - `messaging`

The messaging blueprint scaffolds a project-owned cabinet feature around the
runtime contracts exported by `codex_django.messaging.cabinet`.

Generated projects own their ORM models, selectors, write services, views, and
templates. The reusable runtime layer owns cabinet state dataclasses,
navigation helpers, presenter mapping, workflow validation, and fallback
components.

Navigation is intentionally narrow:

- Sidebar: Mailbox, Campaigns, Recipients, Delivery log.
- Settings: wired only through `settings_url`.
- Templates: not scaffolded as a top-level sidebar item.

The legacy `notifications` module remains available as a deprecated option for
projects that still need the older ARQ/email scaffold.
