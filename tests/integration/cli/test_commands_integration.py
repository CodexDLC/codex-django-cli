"""
Integration tests for current CLI command handlers.

Uses the real CLIEngine and writes actual files to tmp_path.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from codex_django_cli.commands.init import handle_init


@pytest.mark.integration
class TestHandleInitIntegration:
    def test_creates_project_structure(self, tmp_path: Path):
        handle_init("myproject", str(tmp_path))

        project = tmp_path / "myproject" / "src" / "myproject"
        assert project.is_dir()
        assert (project / "manage.py").exists()
        assert (project / "core").is_dir()
        assert (project / "system").is_dir()
        assert (project / "cabinet").is_dir()
        assert (project / "features" / "conversations").is_dir()

    def test_creates_core_settings(self, tmp_path: Path):
        handle_init("myproject", str(tmp_path))

        settings_dir = tmp_path / "myproject" / "src" / "myproject" / "core" / "settings"
        assert (settings_dir / "base.py").exists()
        assert (settings_dir / "dev.py").exists()
        assert (settings_dir / "prod.py").exists()

    def test_i18n_init_adds_set_language_route_to_non_prefixed_urls(self, tmp_path: Path):
        handle_init("myproject", str(tmp_path), enable_i18n=True, languages=["en", "ru"])

        urls_file = tmp_path / "myproject" / "src" / "myproject" / "core" / "urls.py"
        content = urls_file.read_text(encoding="utf-8")

        assert 'path("i18n/", include("django.conf.urls.i18n"))' in content
        assert "urlpatterns += i18n_patterns(" in content

    def test_renders_system_app_config(self, tmp_path: Path):
        handle_init("blog_platform", str(tmp_path))

        system_apps = tmp_path / "blog_platform" / "src" / "blog_platform" / "system" / "apps.py"
        assert system_apps.exists()
        content = system_apps.read_text(encoding="utf-8")
        assert 'name = "system"' in content
        assert 'label = "system"' in content

    def test_skips_existing_project(self, tmp_path: Path):
        target = tmp_path / "myproject" / "src" / "myproject"
        target.mkdir(parents=True)
        (target / "manage.py").write_text("dummy", encoding="utf-8")

        sentinel = target / "sentinel.txt"
        sentinel.write_text("original", encoding="utf-8")

        handle_init("myproject", str(tmp_path))

        assert sentinel.read_text(encoding="utf-8") == "original"
        assert (target / "manage.py").read_text(encoding="utf-8") == "dummy"

    def test_idempotent_second_call_skipped(self, tmp_path: Path):
        handle_init("myproject", str(tmp_path))
        manage_py = tmp_path / "myproject" / "src" / "myproject" / "manage.py"
        original_content = manage_py.read_text(encoding="utf-8")

        handle_init("myproject", str(tmp_path))

        assert manage_py.read_text(encoding="utf-8") == original_content

    def test_booking_public_init_scaffolds_optional_layers(self, tmp_path: Path):
        handle_init(
            "bookingproj",
            str(tmp_path),
            with_booking=True,
            with_public_booking=True,
        )

        project = tmp_path / "bookingproj" / "src" / "bookingproj"
        assert (project / "cabinet").is_dir()
        assert (project / "features" / "booking").is_dir()
        booking_urls = project / "cabinet" / "urls.py"
        assert booking_urls.exists()
        content = booking_urls.read_text(encoding="utf-8")
        assert "booking" in content.lower()

    def test_cabinet_scaffold_matches_test_stand_package_layout(self, tmp_path: Path):
        handle_init("bookingproj", str(tmp_path), with_booking=True)

        project = tmp_path / "bookingproj" / "src" / "bookingproj"
        cabinet_dir = project / "cabinet"

        assert (cabinet_dir / "views" / "booking.py").exists()
        assert (cabinet_dir / "services" / "booking.py").exists()
        assert (cabinet_dir / "templates" / "cabinet" / "booking" / "schedule.html").exists()
        assert (cabinet_dir / "views" / "users.py").exists()
        assert (project / "views").exists() is False
        assert (project / "services").exists() is False

        cabinet_urls = (cabinet_dir / "urls.py").read_text(encoding="utf-8")
        assert "from .views.analytics import" in cabinet_urls
        assert "from .views.users import" in cabinet_urls
