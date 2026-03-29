# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.2] - 2026-03-30

### Added
- **Install-chain E2E smoke coverage**: Added a parametrized end-to-end smoke test for both local editable install chain and optional online install chain, including generated-project runtime sanity checks.
- **Subprocess diagnostics fixture**: Added a shared helper fixture for subprocess-based tests with command tracing, elapsed time logging, and rich failure output.

### Changed
- **Developer check flow**: Updated `tools/dev/check.py` so unit tests keep coverage, e2e can run with live subprocess output, and integration/e2e runs are prompted explicitly.
- **Pytest default flags**: Removed global coverage `addopts` from `pyproject.toml` so integration/e2e runs are not forced through coverage instrumentation by default.
- **Scaffold verification tests**: Refined integration and unit expectations around notification scaffolding paths and generated app configuration values.
- **Install-chain documentation**: Expanded `README.md` with concrete local and online install-chain e2e command examples and environment variable toggles.

### Fixed
- **Secret scanner false positives**: Added allowlist pragmas to scaffolded `.env` example secret placeholders and the commented `DATABASE_URL` template line generated during project init.

## [0.2.1] - 2026-03-29

### Changed
- **Notifications as base layer**: Moved notification scaffolding into the shared `system` and `core/arq` layers and removed it from optional init module selection so generated projects start with a consistent messaging foundation.
- **Project bootstrap environment**: `init` now creates a real local `.env` with a generated Django `SECRET_KEY` and a valid Fernet `FIELD_ENCRYPTION_KEY`, while `.env.example` remains a repository-safe example file.
- **Security menu output**: Split the interactive security helper into separate Django and Fernet key generation so scaffold users do not confuse the two values.
- **Single-language i18n support**: Kept translation-aware mode enabled for `i18n + 1 language` and rendered a valid `MODELTRANSLATION_LANGUAGES` tuple for that case.

### Fixed
- **Notification template filenames**: Renamed notification blueprints to `*.py.j2` so generated projects no longer receive Python source files without the `.py` extension.
- **Generated app config consistency**: Aligned local `AppConfig.name` values for `system` and `features.main` with the scaffold's short import model, fixing startup failures such as `StaticPageSeo` not belonging to an installed app.
- **Scaffold onboarding text**: Clarified generated-project next steps and i18n messaging so user-facing output matches the actual bootstrap flow.


## [0.2.0] - 2026-03-29

### Added
- **Release automation baseline**: Added standard GitHub Actions workflows for CI, documentation deployment, and PyPI publishing so the package can follow the same release pipeline as the other `codex-*` repositories.
- **Versioned docs changelog page**: Added a root `CHANGELOG.md` and a `docs/changelog.md` include page so release notes are published with the MkDocs site.
- **Roadmap documentation**: Added a roadmap entry documenting the planned extraction of deployment, CI/CD, and pre-commit scaffolding into a separate reusable library for future use by `codex-django`, `codex-bot`, and `codex-fastapi`.
- **Coverage-complete command tests**: Expanded unit coverage for the standalone command layer, including booking and client-cabinet scaffolding flows, bringing unit coverage to the release target.

### Changed
- **Documentation metadata**: Updated the documentation URL and MkDocs configuration to align the repository with the shared Codex documentation pattern, including `mike` versioning support and published changelog navigation.
- **Packaging boundaries**: Removed the direct runtime dependency on `codex-django` from `codex-django-cli` after confirming that `codex-django` is required by generated projects, not by the CLI package itself.
- **Checker standardization**: Reworked `tools/dev/check.py` to use the shared flag-based `BaseCheckRunner` pattern from `codex-core`, restoring a consistent quality-gate interface across Codex repositories.
- **Development dependency policy**: Added `codex-core>=0.2.2,<0.3.0` as the bounded development dependency required by the shared check runner.
- **Lockfile scope**: Regenerated `uv.lock` after the dependency cleanup so the standalone CLI environment no longer pulls in the Django runtime stack unnecessarily.
- **Lazy Django command bridge**: Switched the CLI utility bridge to lazy runtime imports so standalone typing and installation no longer require Django to be installed.

### Fixed
- **detect-secrets false positives**: Marked scaffold example values in deploy templates and workflow templates with allowlist pragmas so `pre-commit` passes without treating example credentials as real leaked secrets.
- **Standalone mypy boundary**: Removed the last direct Django import from the CLI runtime code path so type-checking succeeds without a Django dependency in the package environment.
- **Unit test compatibility**: Updated CLI utility tests to mock the new lazy import path instead of importing `django.core.management` directly.

## [0.1.0] - 2026-03-28

### Added
- **Standalone package extraction**: Created `codex-django-cli` as a dedicated repository by extracting the CLI layer from `codex-django` on March 28, 2026.
- **Interactive CLI ownership**: Moved the `codex-django` command, prompt flow, scaffold handlers, and blueprint rendering engine into the standalone package.
- **Packaged blueprint assets**: Brought over project, feature, deployment, and repository templates required to scaffold Codex Django projects.
- **CLI documentation set**: Added English and Russian guides covering installation modes, runtime vs CLI responsibilities, architecture, commands, and generated project output.
- **Developer quality tooling**: Added pytest, Ruff, Mypy, Bandit, pip-audit, pre-commit, MkDocs, and `uv`-based project metadata for independent CLI development.

### Changed
- **Repository boundaries**: Separated CLI concerns from the runtime library so `codex-django` can depend on the CLI optionally, while generated projects continue to depend on `codex-django` itself.
