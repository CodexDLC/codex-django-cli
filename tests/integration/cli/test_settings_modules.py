"""Integration tests: settings modules are generated correctly per selected features."""

from __future__ import annotations

from pathlib import Path

import pytest

from codex_django_cli.commands.init import handle_init


def _settings_modules_dir(project_root: Path, name: str) -> Path:
    return project_root / name / "src" / name / "core" / "settings" / "modules"


def _base_settings(project_root: Path, name: str) -> Path:
    return project_root / name / "src" / name / "core" / "settings" / "base.py"


@pytest.mark.integration
class TestSettingsModules:
    """Verify settings modules are scaffolded and wired correctly."""

    # ── booking ──────────────────────────────────────────────────────────────

    def test_booking_settings_file_generated_with_booking(self, tmp_path: Path) -> None:
        handle_init("testproj", str(tmp_path), with_booking=True)
        booking_file = _settings_modules_dir(tmp_path, "testproj") / "booking.py"

        assert booking_file.exists(), "core/settings/modules/booking.py not generated"
        content = booking_file.read_text(encoding="utf-8")
        assert "BOOKING_DEFAULT_SLOT_MINUTES" in content
        assert "BOOKING_MAX_ADVANCE_DAYS" in content
        assert "BOOKING_CHAIN_MODE" in content
        assert "CODEX_BOOKING_SETTINGS_MODEL" in content

    def test_booking_settings_empty_without_booking(self, tmp_path: Path) -> None:
        handle_init("testproj", str(tmp_path), with_booking=False)
        booking_file = _settings_modules_dir(tmp_path, "testproj") / "booking.py"

        # File should either not exist or be empty / contain no setting keys
        if booking_file.exists():
            content = booking_file.read_text(encoding="utf-8").strip()
            assert "BOOKING_DEFAULT_SLOT_MINUTES" not in content, (
                "booking.py should not contain booking settings when booking=False"
            )

    def test_base_settings_imports_booking_when_enabled(self, tmp_path: Path) -> None:
        handle_init("testproj", str(tmp_path), with_booking=True)
        base = _base_settings(tmp_path, "testproj")

        assert base.exists()
        content = base.read_text(encoding="utf-8")
        assert "from .modules.booking import" in content

    def test_base_settings_no_booking_import_when_disabled(self, tmp_path: Path) -> None:
        handle_init("testproj", str(tmp_path), with_booking=False)
        base = _base_settings(tmp_path, "testproj")

        assert base.exists()
        content = base.read_text(encoding="utf-8")
        assert "from .modules.booking import" not in content

    # ── LOGIN_URL parametrization ─────────────────────────────────────────────

    def test_codex_settings_no_hardcoded_login_url(self, tmp_path: Path) -> None:
        handle_init("testproj", str(tmp_path))
        codex_file = _settings_modules_dir(tmp_path, "testproj") / "codex.py"

        assert codex_file.exists(), "core/settings/modules/codex.py not generated"
        content = codex_file.read_text(encoding="utf-8")
        # Hardcoded string should be gone — now comes from env via CABINET_LOGIN_URL
        assert 'LOGIN_URL = "/cabinet/login/"' not in content, (
            "LOGIN_URL must not be hardcoded; use CABINET_LOGIN_URL env var"
        )
        assert "CABINET_LOGIN_URL" in content, "CABINET_LOGIN_URL env-backed variable must be present in codex.py"
