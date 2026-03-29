"""E2E tests for the CLI — run via subprocess in an isolated venv."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


@pytest.mark.e2e
def test_init_creates_project_structure(sterile_env: dict):
    cli = sterile_env["cli"]
    work_dir = sterile_env["work_dir"]

    result = subprocess.run(
        [str(cli), "init", "testproject"],
        cwd=str(work_dir),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    # CLI creates: work_dir / testproject / src / testproject /
    project_dir = work_dir / "testproject" / "src" / "testproject"
    assert project_dir.is_dir()
    assert (project_dir / "manage.py").exists()
    assert (project_dir / "core").is_dir()
    assert (project_dir / "system").is_dir()
    assert (project_dir / "cabinet").is_dir()
    system_apps = project_dir / "system" / "apps.py"
    main_apps = project_dir / "features" / "main" / "apps.py"
    assert system_apps.exists()
    assert main_apps.exists()
    assert 'name = "system"' in system_apps.read_text(encoding="utf-8")
    assert 'name = "features.main"' in main_apps.read_text(encoding="utf-8")


@pytest.mark.e2e
def test_init_skips_existing_project(sterile_env: dict):
    cli = sterile_env["cli"]
    work_dir = sterile_env["work_dir"]

    # Create the target directory before running
    target = work_dir / "src" / "myapp"
    target.mkdir(parents=True)

    result = subprocess.run(
        [str(cli), "init", "myapp"],
        cwd=str(work_dir),
        capture_output=True,
        text=True,
    )

    # Should not fail but should warn
    assert result.returncode == 0
    assert (target / "manage.py").not_exists() if hasattr(Path, "not_exists") else not (target / "manage.py").exists()


@pytest.mark.e2e
def test_add_app_creates_app_structure(sterile_env: dict):
    cli = sterile_env["cli"]
    work_dir = sterile_env["work_dir"]

    # First init a project
    subprocess.run([str(cli), "init", "myproject"], cwd=str(work_dir), check=True)

    # Then add an app
    project_src = work_dir / "myproject" / "src" / "myproject"
    result = subprocess.run(
        [str(cli), "add-app", "blog"],
        cwd=str(project_src),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    app_dir = project_src / "features" / "blog"
    assert app_dir.is_dir()
    assert (app_dir / "apps.py").exists()
    assert (app_dir / "models" / "__init__.py").exists()
    assert (app_dir / "views" / "__init__.py").exists()


@pytest.mark.e2e
def test_init_i18n_creates_i18n_settings(sterile_env: dict):
    cli = sterile_env["cli"]
    work_dir = sterile_env["work_dir"]

    result = subprocess.run(
        [str(cli), "init", "mlproject", "--i18n"],
        cwd=str(work_dir),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    i18n_file = (
        work_dir / "mlproject" / "src" / "mlproject" / "core" / "settings" / "modules" / "internationalization.py"
    )
    assert i18n_file.exists(), "internationalization.py was not generated"

    content = i18n_file.read_text(encoding="utf-8")
    assert "LANGUAGES = [" in content
    assert "discover_locale_paths(BASE_DIR)" in content
    assert "USE_I18N = True" in content
    assert 'MODELTRANSLATION_DEFAULT_LANGUAGE = LANGUAGE_CODE.split("-")[0]' in content
    assert 'MODELTRANSLATION_LANGUAGES = ("en", )' in content


@pytest.mark.e2e
def test_init_languages_argument_supports_arbitrary_language_codes(sterile_env: dict):
    cli = sterile_env["cli"]
    work_dir = sterile_env["work_dir"]

    result = subprocess.run(
        [str(cli), "init", "langproject", "--languages", "ja,en,de-at"],
        cwd=str(work_dir),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    i18n_file = (
        work_dir / "langproject" / "src" / "langproject" / "core" / "settings" / "modules" / "internationalization.py"
    )
    assert i18n_file.exists(), "internationalization.py was not generated"

    content = i18n_file.read_text(encoding="utf-8")
    assert 'LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "ja")' in content
    assert '("ja", "ja")' in content
    assert '("de-at", "de-at")' in content
    assert 'MODELTRANSLATION_LANGUAGES = ("ja", "en", "de-at", )' in content


@pytest.mark.e2e
def test_cli_help_exits_cleanly(sterile_env: dict):
    cli = sterile_env["cli"]
    work_dir = sterile_env["work_dir"]

    result = subprocess.run(
        [str(cli), "--help"],
        cwd=str(work_dir),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
