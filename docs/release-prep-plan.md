# Release Prep Plan

## Goal

Use this file as the working release-prep tracker for the current `codex-django-cli` refactor.  
The release pass must move layer by layer and avoid mixing documentation, runtime architecture, blueprint moves, test synchronization, and release notes.

## Tracking Rules

- Work strictly by layers.
- For each layer, first capture factual changes from `git status` and the current file tree.
- Only after that decide what documentation text must change.
- Treat moves, deletions, and truly new additions separately.
- Do not finalize `CHANGELOG.md` or decide the version until every other layer is reviewed.
- After each layer, update this file with:
  - confirmed facts;
  - open questions or disputed points;
  - whether the layer affects release versioning.

## Layer Order

| Layer | Status | Notes |
| --- | --- | --- |
| docs | done | Landing, getting-started, architecture, API, and blueprint workflow docs were aligned with the current CLI model. |
| commands / prompts / main / engine | done | Current CLI operating model was confirmed from code and reflected in the tracker. |
| blueprints/cabinet | done | Extraction mapped: a small subset is true rename, but most of the layer is a new cabinet app contract. |
| blueprints/features/* | done | Feature map confirmed: booking split across runtime/core/public layers and conversations introduced as a first-class feature package. |
| blueprints/project/* | done | Project output map confirmed: cabinet was extracted out, while system/core/templates gained richer runtime and operational defaults. |
| tooling + pyproject + helper scripts | done | Tooling map confirmed: quality policy moved into pyproject, checks became config-driven, and project tree helpers were added as internal dev tooling. |
| tests | done | Test map confirmed: legacy command coverage was removed, new install/menu/runtime guarantees were added, and CLI unit suite currently passes. |
| CHANGELOG + version | done | Version recommendation is `0.3.0`, and CHANGELOG.md was restored to a readable multiline draft. |

## Docs Layer

### Factual Summary

- Reviewed and updated the following documentation groups:
  - landing + getting-started pages;
  - CLI architecture pages for module, commands, entrypoints, blueprints, and project output;
  - internal CLI API page;
  - blueprint workflow guides in English and Russian.
- The docs now consistently describe:
  - `init/install/repo` instead of the old bootstrap model;
  - `startserver` instead of `runserver_plus`;
  - the extracted top-level `cabinet` blueprint family;
  - the split between `booking_core` and `booking_public`;
  - conversations as a dedicated feature layer;
  - current menu wording centered on project init, project extension, repo config, deploy, CI/CD, and pre-commit flows.

### Confirmed Points

- Old menu wording such as `Scaffolding (Apps/Modules)` was removed from live docs.
- Removed command families such as `add_app`, `add-booking`, `add-client-cabinet`, and notification-specific CLI paths were removed from live docs.
- The internal API reference now points at the current internal modules.
- Blueprint docs now describe the real top-level partition: `repo`, `project`, `cabinet`, `features`, `apps`, `deploy`.

### Remaining Notes

- References to `client_cabinet` remain only where it still exists as a blueprint subtree and therefore still has architectural value.
- `Notifications` in the Codex ecosystem table remains valid because it refers to `codex-platform`, not to a removed CLI command family.

### Release Impact

- This layer materially strengthens release framing and reduces architectural drift in docs.
- Version choice is still deferred.

## Commands / Prompts / Main / Engine Layer

### Factual Summary

- `main.py` now exposes one top-level CLI with two real operating modes:
  - interactive menu mode;
  - scripted subcommand mode.
- The interactive menu is repository-scoped, not project-local in the old sense:
  - it scans `src/` for generated projects;
  - it resolves a target project when an extension, deploy, or repo-config action needs one.
- The public scripted subcommands currently exposed by `_handle_cli_args()` are:
  - `init`
  - `menu`
  - `deploy`
- `prompts.py` now defines the active menu tree around:
  - project initialization;
  - project extension;
  - deployment file generation;
  - CI/CD workflow generation;
  - repo config generation;
  - pre-commit setup.
- `install.py` is the orchestration core of the current scaffold model.
  It owns:
  - module detection for existing projects;
  - install-plan resolution;
  - new-project scaffolding;
  - extension of existing projects;
  - compare-copy generation.
- `init.py` is now a thin public entrypoint that normalizes flags into `InstallSelection` and delegates real project assembly to `install.py`.
- `repo.py` is now the repository-shell generator for `pyproject.toml` and `.env.example`, including compare-file behavior when those files already exist.
- `deploy.py` and `quality.py` remain separate operational layers outside the runtime project tree.
- `engine.py` remains the low-level scaffold contract:
  - render `.j2` templates with context;
  - copy static files as-is;
  - prefer templated variants when both `foo` and `foo.j2` exist;
  - write scaffold trees into target paths with optional overwrite.

### Confirmed Points

- The old command family model (`add_app`, `booking`, `client_cabinet`, `notifications`) is no longer the current public CLI model.
- The real command/orchestration model is now `init -> install`, plus `repo`, `deploy`, and `quality`.
- The menu labels in docs must be treated as API-like UX contracts because tests cover them directly through `prompts.py`.
- The current CLI is hybrid, but only some flows are scriptable; richer install/extend flows are still menu-first.

### Remaining Notes

- `deploy.py` still carries some broader optional context fields such as `with_notifications`, `enable_i18n`, and `cluster_name`; these belong to the operational layer review, not the core command-model review.
- The engine contract itself looks stable; the remaining architectural questions now shift to blueprint layout rather than entrypoint behavior.

### Release Impact

- This layer is version-relevant because it changes how users understand and operate the CLI.
- Version choice is still deferred until blueprint and tooling layers are also mapped.

## Blueprints / Cabinet Layer

### Factual Summary

- The cabinet scaffold is no longer primarily a subtree inside `blueprints/project/cabinet`.
  It is now a dedicated top-level blueprint family under `blueprints/cabinet`.
- Git recognizes only a small subset as true renames:
  - `apps.py.j2`
  - `static/cabinet/css/base.css`
  - `static/cabinet/css/compiler_config.json`
  - `static/cabinet/css/theme/tokens.css`
- Most of the layer is therefore not just a file move. It is a structural rewrite with new responsibilities.
- The old cabinet tree was small and mostly centered on:
  - a default cabinet registration in `cabinet.py.j2`;
  - user selector/view templates;
  - mock-backed dashboard and user data;
  - a narrow user + client-booking routing model.
- The new top-level cabinet tree now includes distinct app-level surfaces for:
  - registration entrypoint and app bootstrapping;
  - adapters and context processors;
  - auth routes;
  - booking bridge integration;
  - service-layer modules for users, booking, analytics, client, and conversations;
  - dedicated views for analytics, auth, booking, client, conversations, site settings, and users;
  - expanded cabinet CSS and JS assets;
  - dedicated templates for analytics, booking, client, conversations, site settings, and users.

### Confirmed Moves

- A small core of cabinet assets was genuinely moved forward into the new top-level family:
  - app registration file;
  - base cabinet CSS;
  - CSS compiler config;
  - theme tokens.
- The cabinet concept itself clearly survived the refactor, but it was promoted from a project subtree to a first-class blueprint layer.

### Confirmed Deletions / Replacements

- The following old project-local cabinet pieces are gone as standalone concepts:
  - `mock.py.j2`
  - selector-only user data access under `selector/users.py.j2`
  - old function-based user views;
  - user detail template pair `index.html` / `detail.html`;
  - old `my/bookings` client portal route model;
  - placeholder package stubs like `admin`, `forms`, `models`, `modules`, `tests`, and `services` under the old cabinet subtree.
- These were not simply renamed one-to-one. In practice they were replaced by a broader app-layer contract built around service objects, class-based views, richer templates, and explicit integration points.

### Confirmed New Responsibilities

- `cabinet.py.j2` changed role.
  The old file declared default sections and dashboard extensions directly.
  The new file is a cabinet app registration entrypoint and intentionally leaves feature registrations to feature-specific `cabinet.py` modules.
- User pages moved from selector-driven function views to a service-backed class view model:
  - old: `selector/users.py.j2` + function views + `index/detail` templates;
  - new: `services/users.py.j2` + `UserListView` + card-grid based users page.
- Cabinet routing expanded from a narrow users/client-booking scope to a broader application shell that can host:
  - analytics;
  - client corner and appointments;
  - booking schedule/settings/new flows;
  - conversations inbox/thread/compose flows;
  - site settings tabs.
- Client-facing cabinet behavior is now explicit inside the cabinet layer itself through `views/client.py.j2`, `services/client.py.j2`, and dedicated templates.
- Conversations are integrated at the cabinet shell level instead of being absent from the old cabinet subtree.
- Booking inside cabinet now looks like an operator-facing workflow layer, not just a minimal client-portal add-on.

### Remaining Notes

- Some files shown as adds may still contain reused fragments, but at the release-mapping level this layer should be described as an extraction plus architectural expansion, not as a pure rename.
- Final docs wording for cabinet should emphasize promotion to a first-class blueprint family and the split of feature registrations out of the cabinet root itself.

### Release Impact

- This layer is strongly version-relevant because it changes the generated project architecture and the cabinet extension model.
- Version choice is still deferred until features, project output, tooling, and tests are also mapped.

## Blueprints / Features Layer

### Factual Summary

- The old single `features/booking` story is now split across three distinct concerns:
  - `features/booking`
  - `features/booking_core`
  - `features/booking_public`
- `features/conversations` is entirely new as a first-class feature package.
- `features/client_cabinet` remains in place, but the current diff there is mostly template alignment with the expanded cabinet shell rather than a brand-new feature family.
- `features/notifications` still exists in the tree, but it is not part of the current staged expansion in the way booking and conversations are.

### Booking Layer Mapping

- `features/booking` still survives, but it is no longer the whole booking story.
- The legacy-style booking package under `features/booking/booking/*` still contains the thin public booking app surface:
  - models;
  - selectors wrapping `codex_django.booking` adapters;
  - API-style views and URLs;
  - public booking wiki/docs.
- A new nested package under `features/booking/features/booking/*` was added in the same feature family.
  At release-mapping level this means the booking blueprint now also emits a project-local `features.booking` package structure rather than only the older root-level `booking` app shape.
- The booking cabinet subtree under `features/booking/cabinet/*` remains active, but it was updated to fit the new cabinet shell and current appointment UX.
- The old public booking page and step partials did not disappear conceptually, but they were extracted into a dedicated public-template layer.

### Booking Core Layer Mapping

- `features/booking_core` is genuinely new as a separate feature layer.
- It introduces the missing domain/service contracts that were not previously isolated as their own blueprint package:
  - `apps.py.j2`
  - `booking_settings.py.j2`
  - `cabinet.py.j2`
  - provider modules;
  - selector engine;
  - service helpers and cabinet workflow service;
  - URLs and view package skeletons.
- In practical terms this layer owns the reusable booking engine integration:
  - project provider access;
  - cabinet workflow state;
  - booking bridge adapter;
  - core settings/runtime contracts.
- This means booking is no longer described accurately as only a public wizard plus a couple of models. It now has an explicit core/runtime layer.

### Booking Public Layer Mapping

- `features/booking_public` is also new as its own layer.
- Its staged diff is template-only and clearly corresponds to the old public booking wizard UI:
  - `booking_page.html`
  - `partials/step_service.html`
  - `partials/step_date.html`
  - `partials/step_time.html`
  - `partials/step_confirm.html`
- Comparing the old and new booking page shows near-direct extraction rather than a conceptual rewrite.
- This means the public booking wizard presentation was separated out from the broader booking feature package and can now be described independently from booking runtime/core logic.

### Conversations Layer Mapping

- `features/conversations` is a genuinely new feature family, not a rename.
- It introduces a complete project-local package with:
  - app registration;
  - cabinet registration;
  - forms;
  - migrations;
  - message and reply models;
  - selectors;
  - service modules for alerts, email import, notifications, and workflow;
  - URLs and views;
  - translations and tests.
- The conversations cabinet registration confirms that the feature integrates directly into the cabinet shell through:
  - topbar entries;
  - sidebar entries;
  - dashboard metrics;
  - bell/notification integration.
- This layer therefore changes not just generated files but the feature topology of generated projects.

### Confirmed Moves / Extractions

- Public booking templates were effectively extracted out of the older `features/booking/templates/booking/*` location into `features/booking_public/templates/features/booking/*`.
- Booking cabinet pages remain attached to the booking feature family, but the cabinet shell they plug into is now broader and more modular than before.

### Confirmed Additions / Replacements

- Booking gained explicit core/runtime scaffolding instead of keeping all responsibilities bundled in one feature package.
- Conversations was added as a new feature package rather than being represented indirectly through notifications or cabinet-only pages.
- `client_cabinet` template updates indicate downstream alignment with the new cabinet structure, but `client_cabinet` itself is not the main source of this layer's architectural change.

### Remaining Notes

- The coexistence of `features/booking/booking/*` and `features/booking/features/booking/*` should be described carefully in docs as two output shapes inside the same booking family, not as a simple typo or duplicate.
- The exact install-selection matrix for when `booking`, `booking_core`, and `booking_public` are combined should be verified later from install orchestration, but the structural split itself is already clear from the blueprint tree.

### Release Impact

- This layer is strongly version-relevant because it changes the feature composition of generated projects.
- Version choice is still deferred until the `project/*`, tooling, tests, and final release layers are also mapped.

## Blueprints / Project Layer

### Factual Summary

- This layer contains two different kinds of change and they must be described separately:
  - removal of the old `project/cabinet` subtree because cabinet became its own top-level blueprint family;
  - expansion of the remaining base project output under `core`, `system`, `features.main`, and `templates`.
- The `project/cabinet/*` removals are real, but they are not a loss of cabinet functionality.
  They belong to the cabinet extraction already mapped in the previous layer.
- Outside cabinet extraction, the generated project shell itself became richer and more operationally opinionated.

### Core / Settings Mapping

- `project/core/settings/modules/*` was updated in multiple places:
  - installed apps;
  - codex integration settings;
  - i18n settings;
  - middleware;
  - logger configuration.
- The updated apps settings confirm the new generated project topology:
  - local apps include `system`, `features.main`, optional `cabinet`, optional `features.conversations`, and optional `features.booking`;
  - codex library apps still provide `codex_django.cabinet` and `codex_django.showcase`.
- `project/core/urls.py.j2` now explicitly wires more generated runtime endpoints:
  - `robots.txt`;
  - `llms_de.txt` and `llms_en.txt`;
  - optional `sw.js` and `manifest.json`;
  - optional public booking and conversations routes;
  - cabinet and showcase wiring.
- This means the base project routing contract now assumes a broader generated surface than before.

### System Layer Mapping

- `project/system/*` gained several new project-level runtime pieces:
  - `cabinet.py.j2`;
  - `management/commands/compile_assets.py.j2`;
  - `management/commands/startserver.py.j2`;
  - `models/user_profile.py.j2`;
  - `selectors/client_profile.py.j2` and `selectors/users.py.j2`;
  - `services/client_profile.py.j2` and `services/site_settings.py.j2`.
- `runserver_plus.py.j2` was removed and replaced by `startserver.py.j2`.
  The new command keeps the same high-level purpose of compiling assets before local serving, but it is cleaner and delegates compilation to a dedicated `compile_assets` command.
- `compile_assets.py.j2` is a new standalone operational command that scans static directories and app static folders for `compiler_config.json` files and compiles them through `codex_core.dev.static_compiler.StaticCompiler`.
- `system/cabinet.py.j2` is new and important.
  It registers default analytics, users, and client cabinet modules directly at the system layer, including dashboard widgets and sidebar/topbar entries.
- `system/models/user_profile.py.j2` is a new shared profile model built on `AbstractUserProfile`.
- The new selectors/services indicate that user and client-profile behavior is now scaffolded as first-class project infrastructure rather than being left to ad-hoc example code.

### Templates / Public Runtime Mapping

- `project/templates/main/home.html` was replaced by `home.html.j2`, so the homepage is now scaffolded as a true template rather than shipped as a fixed static HTML file.
- The new generated homepage is a structured starter landing page centered on:
  - showcase usage;
  - public site foundation;
  - cabinet/backoffice flows;
  - notifications/integrations.
- New generated text templates were added:
  - `llms_de.txt.j2`
  - `llms_en.txt.j2`
- New generated web-app/runtime templates were added:
  - `manifest.json.j2`
  - `robots.txt.j2`
  - `sw.js.j2`
- This indicates that the generated project now ships with a stronger default public/runtime shell, including PWA-facing assets and machine-readable site files.

### Confirmed Moves / Removals

- `project/cabinet/*` was removed from the project layer because cabinet responsibility moved to the new top-level `blueprints/cabinet` family.
- `runserver_plus.py.j2` was removed in favor of `startserver.py.j2` plus `compile_assets.py.j2`.
- `templates/main/home.html` was removed in favor of `templates/main/home.html.j2`.

### Confirmed Additions / Replacements

- The system layer now provides more real project infrastructure by default:
  - user profile model;
  - selectors/services for user and client profile data;
  - default cabinet registrations at the system level;
  - dedicated asset compilation command.
- The public template layer now includes default runtime assets for SEO/PWA/discovery rather than only core HTML pages.
- The generated project is therefore closer to a ready operational starter and less like a minimal skeleton.

### Remaining Notes

- Some of the changed `system/admin` and `system/models` files are incremental expansions rather than wholly new concepts, but together they reinforce the same shift: the scaffold is supplying more truthful application infrastructure up front.
- The final release summary should avoid merging the cabinet extraction story into this layer again; it should treat cabinet extraction and project-runtime enrichment as adjacent but separate changes.

### Release Impact

- This layer is strongly version-relevant because it changes the default generated project runtime, developer commands, and shipped public assets.
- Version choice is still deferred until tooling, tests, and final release framing are also mapped.

## Tooling / Package Layer

### Factual Summary

- This layer is small in file count but meaningful in development workflow impact.
- The staged changes touch exactly five paths:
  - `pyproject.toml`
  - `tools/dev/check.py`
  - `tools/dev/generate_project_tree.py`
  - `src/codex_django_cli/dev/__init__.py`
  - `src/codex_django_cli/dev/project_tree.py`
- The overall direction is clear:
  - quality policy moved into declarative project config;
  - the check launcher became thinner;
  - a reusable project-tree generator was added as internal dev tooling.

### Pyproject Mapping

- `pyproject.toml` now requires a newer `codex-core` range in dev dependencies:
  - from `>=0.2.2,<0.3.0`
  - to `>=0.3.0,<0.4.0`
- Pytest config now injects default coverage flags through `addopts`.
- Coverage omission rules were expanded so reports focus on meaningful runtime code rather than:
  - blueprint sources;
  - the new `dev/project_tree.py` helper;
  - draft paths.
- A new `[tool.codex-check]` section was added.
  It centralizes project-specific check policy, including:
  - audit flags;
  - security command;
  - stage definitions for unit / integration / e2e;
  - when coverage should or should not run;
  - prompt expectations for heavier test stages.
- This means the repository's quality gate is now more configuration-driven and less hardcoded inside scripts.

### Check Runner Mapping

- `tools/dev/check.py` was simplified into a thin launcher over `codex_core.dev.check_runner.BaseCheckRunner`.
- The script now explicitly says that project policy lives in `pyproject.toml`.
- This is a real tooling architecture change:
  - before, project-local scripting carried more responsibility;
  - now, `pyproject.toml` is the main source of truth for the quality/check pipeline.

### Project Tree Helper Mapping

- A new internal helper package was added under `src/codex_django_cli/dev/*`.
- Its main export is `ProjectTreeGenerator`, a reusable utility that:
  - scans a project directory;
  - filters noisy directories and binary/static artifacts;
  - writes a human-readable tree to a text file;
  - supports interactive selection of a top-level subtree versus the full project.
- `tools/dev/generate_project_tree.py` is the thin script entrypoint for that helper.
- This confirms that project-tree generation is now a first-class dev utility rather than a one-off local script.

### Confirmed Additions / Replacements

- Quality/check behavior is now driven more by shared codex-core tooling plus project config, and less by custom local script logic.
- The repo gained an internal helper module intended for repository introspection and documentation support.
- Coverage defaults became stricter and more standardized for local test runs.

### Remaining Notes

- The working tree currently contains `src/codex_django_cli/dev/__pycache__/*` from local execution, but those are runtime byproducts, not meaningful source changes for release framing.
- This layer should be described as developer-experience and maintenance infrastructure, not as generated-project runtime behavior.

### Release Impact

- This layer is moderately version-relevant: it does not change end-user generated app behavior directly, but it does change contributor workflow, check semantics, and dev-tool expectations.
- Version choice is still deferred until the tests layer and final release framing are also mapped.

## Tests Layer

### Factual Summary

- The current staged test changes span unit, integration, and e2e layers:
  - unit CLI tests;
  - integration command tests;
  - e2e init/install chain tests.
- The main pattern is consistent across all three levels:
  - legacy command coverage was removed;
  - the rewritten `init/install/menu/deploy` model is now the source of behavioral assertions;
  - generated output expectations were updated to the new scaffold topology.
- Current verification status:
  - `tests/unit/cli` passes locally;
  - latest run: `90 passed`;
  - coverage is now injected by default from `pyproject.toml`, and the latest unit CLI run reported `TOTAL 88%` for measured runtime code.

### Synchronization Changes

- Several tests were changed mainly to stop asserting old architecture details that are no longer true:
  - old `add_app` command tests were removed;
  - old `notifications` command tests were removed;
  - old `booking` command tests were removed;
  - old `client_cabinet` command tests were removed;
  - old prompt expectations for scaffolding-specific menus were removed.
- These removals should be understood as synchronization with the rewritten CLI surface, not as a reduction in overall seriousness.

### New / Updated Public Guarantees

- `tests/unit/cli/test_install.py` is new and is now the clearest unit-level contract for the install orchestrator.
  It verifies:
  - install-selection resolution;
  - language normalization;
  - scaffold path resolution;
  - `.env` writing behavior;
  - scaffold order for new projects and existing projects;
  - automatic implication rules such as booking => cabinet and public booking => booking.
- `tests/unit/cli/test_prompts.py` now treats prompt/menu wording as a real contract.
  It verifies:
  - the current top-level menu choices;
  - absence of the old scaffolding menu wording;
  - install-module prompts and aliases;
  - init-mode and plan-confirm flows;
  - cloud DB prompt behavior.
- `tests/unit/cli/test_main.py` was reshaped around `_handle_cli_args()` and the current interactive flow.
  It now checks:
  - `menu` command behavior;
  - current `init` flag mapping;
  - rejection of removed commands such as `add-app`;
  - deploy flag handling;
  - project discovery from `src/`.
- `tests/unit/cli/test_engine.py` gained a direct guarantee that `.j2` wins when raw and templated files share the same output path.
- Integration and e2e tests now assert the new scaffold topology:
  - cabinet directory exists in generated projects;
  - conversations scaffold appears in base init flow;
  - optional booking/public-booking layers can be generated;
  - generated management command is `startserver`, not `runserver_plus`.

### Staged vs Working Tree Notes

- Some unit test files still have staged/working-tree divergence:
  - `tests/unit/cli/test_commands.py`
  - `tests/unit/cli/test_install.py`
  - `tests/unit/cli/test_prompts.py`
- This does not invalidate the architectural map, but it does mean final staging cleanup is still required before a release commit is cut.

### Remaining Notes

- The test layer should be described as a synchronization-and-guardrail layer:
  it now follows the rewritten runtime and also locks in several new public expectations.
- The strongest new source of truth for CLI behavior is now the combination of:
  - install orchestration tests;
  - prompt/menu contract tests;
  - init/integration/e2e scaffold topology tests.

### Release Impact

- This layer is release-relevant because it shows that the rewritten CLI and scaffold flow are not just code changes but tested behavior.
- With this layer mapped, the only remaining layer before release naming is `CHANGELOG + version`.

## Changelog / Version Layer

### Factual Summary

- All preceding layers are now mapped in this tracker, so version naming can finally be judged from confirmed scope rather than first impressions.
- The staged `CHANGELOG.md` already contains a draft `0.3.0` entry dated `2026-04-05`.
- `CHANGELOG.md` was restored from the structured staged draft back into a readable multiline working copy.
- The version naming decision is therefore no longer blocked by changelog corruption; remaining cleanup is ordinary staging hygiene across the repo.

### Version Recommendation

- Recommended version: `0.3.0`.
- Reasoning:
  - the CLI public model changed materially from legacy command families to `init/install/repo` orchestration;
  - the scaffold topology changed materially through cabinet extraction, booking layer split, and conversations introduction;
  - the generated project runtime changed materially through `startserver`, `compile_assets`, user-profile/selectors/services, and new public/runtime assets;
  - docs and tests were updated broadly to match the new mental model rather than a narrow bugfix.
- This is larger than a patch release and more coherent than a series of unrelated small fixes.
- It still fits a minor release better than a major one because the package is already in `0.x`, the project is still evolving rapidly, and the changes represent a significant iteration of the scaffold/CLI model rather than a stable-1.0 contract break.

### Changelog Draft Assessment

- The staged draft is directionally correct.
- Its current sections broadly match the mapped release layers:
  - cabinet extraction;
  - booking/conversations additions;
  - system/project template expansion;
  - CLI/install/repo changes;
  - tooling/check updates;
  - removal of legacy command modules.
- The remaining editorial choice is only about emphasis: whether docs/test synchronization should stay secondary in the release note or be elevated further.
- The current draft already works as a release note and does not need structural rescue anymore.

### Remaining Notes

- `.gitignore` is still modified and likely belongs in the release commit as hygiene, but it should remain a secondary note rather than the headline of the release.
- Several docs/tests files still have staged/working-tree divergence; changelog finalization should happen only after that staging cleanup so the release commit reflects one coherent final state.

### Release Impact

- The factual map now supports a `0.3.0` release framing.
- This planning pass is complete; remaining work is final staging cleanup and release execution.
