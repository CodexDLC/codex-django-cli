"""
Integration tests for CLI command handlers.

Uses the real CLIEngine (no mocks) — writes actual files to tmp_path.
No subprocess, no external services required.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from codex_django_cli.commands.add_app import handle_add_app
from codex_django_cli.commands.init import handle_init
from codex_django_cli.commands.notifications import handle_add_notifications


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
        content = system_apps.read_text()
        assert 'name = "system"' in content
        assert 'label = "system"' in content

    def test_skips_existing_project(self, tmp_path: Path):
        target = tmp_path / "myproject" / "src" / "myproject"
        target.mkdir(parents=True)
        (target / "manage.py").write_text("dummy")

        sentinel = target / "sentinel.txt"
        sentinel.write_text("original")

        handle_init("myproject", str(tmp_path))

        assert sentinel.read_text() == "original"
        assert (target / "manage.py").read_text() == "dummy"

    def test_idempotent_second_call_skipped(self, tmp_path: Path):
        handle_init("myproject", str(tmp_path))
        manage_py = tmp_path / "myproject" / "src" / "myproject" / "manage.py"
        original_content = manage_py.read_text()

        handle_init("myproject", str(tmp_path))

        assert manage_py.read_text() == original_content


@pytest.mark.integration
class TestHandleAddAppIntegration:
    def test_creates_app_structure(self, tmp_path: Path):
        handle_add_app("blog", str(tmp_path))

        app = tmp_path / "features" / "blog"
        assert app.is_dir()
        assert (app / "apps.py").exists()
        assert (app / "models" / "__init__.py").exists()
        assert (app / "views" / "__init__.py").exists()
        assert (app / "urls.py").exists()

    def test_creates_all_standard_subdirs(self, tmp_path: Path):
        handle_add_app("shop", str(tmp_path))

        app = tmp_path / "features" / "shop"
        for subdir in ("models", "views", "forms", "services", "admin", "tests"):
            assert (app / subdir).is_dir(), f"Missing subdir: {subdir}"

    def test_skips_existing_app(self, tmp_path: Path):
        target = tmp_path / "features" / "blog"
        target.mkdir(parents=True)
        sentinel = target / "sentinel.txt"
        sentinel.write_text("original")

        handle_add_app("blog", str(tmp_path))

        assert sentinel.read_text() == "original"
        assert not (target / "apps.py").exists()

    def test_multiple_apps_independent(self, tmp_path: Path):
        handle_add_app("blog", str(tmp_path))
        handle_add_app("shop", str(tmp_path))

        assert (tmp_path / "features" / "blog" / "apps.py").exists()
        assert (tmp_path / "features" / "shop" / "apps.py").exists()


@pytest.mark.integration
class TestHandleAddNotificationsIntegration:
    def test_creates_feature_and_arq_structure(self, tmp_path: Path):
        handle_add_notifications("system", str(tmp_path))

        feature = tmp_path / "system"
        assert feature.is_dir()
        assert (feature / "models" / "email_content.py").exists()
        assert (feature / "selectors" / "email_content.py").exists()
        assert (feature / "services" / "notification.py").exists()

        arq = tmp_path / "core" / "arq"
        assert arq.is_dir()
        assert (arq / "client.py").exists()

    def test_custom_arq_dir(self, tmp_path: Path):
        handle_add_notifications("alerts", str(tmp_path), arq_dir="workers/arq")

        # Notifications are always scaffolded into shared system layer.
        assert (tmp_path / "system").is_dir()
        assert (tmp_path / "workers" / "arq" / "client.py").exists()

    def test_renders_app_name_in_model_template(self, tmp_path: Path):
        handle_add_notifications("system", str(tmp_path))

        model_file = tmp_path / "system" / "models" / "email_content.py"
        content = model_file.read_text()
        assert "system" in content
