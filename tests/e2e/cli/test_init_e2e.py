"""E2E tests for the current CLI surface via subprocess in an isolated venv."""

from __future__ import annotations

import subprocess

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

    project_dir = work_dir / "testproject" / "src" / "testproject"
    assert project_dir.is_dir()
    assert (project_dir / "manage.py").exists()
    manage_content = (project_dir / "manage.py").read_text(encoding="utf-8")
    assert "codex_django.cli.main" not in manage_content
    assert 'sys.argv[1] == "menu"' not in manage_content
    assert "forced_project" not in manage_content
    assert "execute_from_command_line(sys.argv)" in manage_content
    assert (project_dir / "core").is_dir()
    assert (project_dir / "system").is_dir()
    assert (project_dir / "cabinet").is_dir()
    assert (project_dir / "features" / "main" / "apps.py").exists()
    assert (project_dir / "features" / "conversations").is_dir()


@pytest.mark.e2e
def test_init_skips_existing_project(sterile_env: dict):
    cli = sterile_env["cli"]
    work_dir = sterile_env["work_dir"]

    target = work_dir / "myapp" / "src" / "myapp"
    target.mkdir(parents=True)

    result = subprocess.run(
        [str(cli), "init", "myapp"],
        cwd=str(work_dir),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert not (target / "manage.py").exists()


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
    assert i18n_file.exists()

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
    assert i18n_file.exists()

    content = i18n_file.read_text(encoding="utf-8")
    assert 'LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "ja")' in content
    assert '("ja", "ja")' in content
    assert '("de-at", "de-at")' in content
    assert 'MODELTRANSLATION_LANGUAGES = ("ja", "en", "de-at", )' in content


@pytest.mark.e2e
def test_init_with_booking_public_booking_creates_optional_layers(sterile_env: dict):
    cli = sterile_env["cli"]
    work_dir = sterile_env["work_dir"]

    result = subprocess.run(
        [str(cli), "init", "bookingproj", "--with-booking", "--with-public-booking"],
        cwd=str(work_dir),
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr

    project_dir = work_dir / "bookingproj" / "src" / "bookingproj"
    assert (project_dir / "cabinet").is_dir()
    assert (project_dir / "features" / "booking").is_dir()


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
