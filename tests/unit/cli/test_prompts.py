"""Unit tests for CLI prompt wrappers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestPromptWrappers:
    def _make_select(self, return_value):
        mock_q = MagicMock()
        mock_q.ask.return_value = return_value
        return mock_q

    def _make_text(self, return_value):
        mock_q = MagicMock()
        mock_q.ask.return_value = return_value
        return mock_q

    def _make_checkbox(self, return_value):
        mock_q = MagicMock()
        mock_q.ask.return_value = return_value
        return mock_q

    def test_ask_main_action_returns_selection(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("🚀  Init new project")
            result = prompts.ask_main_action()
            assert result == "🚀  Init new project"
            mock_q.select.assert_called_once()

    def test_ask_project_action_returns_selection(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("❌  Exit")
            result = prompts.ask_project_action()
            assert result == "❌  Exit"

    def test_ask_project_action_does_not_offer_old_scaffolding_menu(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("❌  Exit")
            prompts.ask_project_action()
            _, kwargs = mock_q.select.call_args
            assert kwargs["choices"] == [
                "🆕  Init new project",
                "🧩  Extend Existing Project",
                "🚀  Standard Commands",
                "🛡  Quality & Tools",
                "🏁  Deployment Setup",
                "⚙️  Security",
                "❌  Exit",
            ]

    def test_ask_standard_command_returns_selection(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("migrate")
            result = prompts.ask_standard_command()
            assert result == "migrate"

    def test_ask_quality_tool_returns_selection(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("Configure pre-commit")
            result = prompts.ask_quality_tool()
            assert result == "Configure pre-commit"

    def test_ask_deploy_option_returns_selection(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("Generate Docker + CI/CD")
            result = prompts.ask_deploy_option()
            assert result == "Generate Docker + CI/CD"

    def test_ask_deploy_mode_returns_selection(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("standalone")
            result = prompts.ask_deploy_mode()
            assert result == "standalone"

    def test_ask_domain_name_returns_text(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.text.return_value = self._make_text("demo.example.com")
            result = prompts.ask_domain_name()
            assert result == "demo.example.com"
            _, kwargs = mock_q.text.call_args
            assert kwargs.get("default") == "example.com"

    def test_ask_deploy_services_maps_selected_values(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.checkbox.return_value = self._make_checkbox(["worker", "bot"])
            result = prompts.ask_deploy_services()
            assert result == {"with_worker": True, "with_bot": True}

    def test_ask_deploy_services_handles_empty_selection(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.checkbox.return_value = self._make_checkbox(None)
            result = prompts.ask_deploy_services()
            assert result == {"with_worker": False, "with_bot": False}

    def test_ask_project_name_returns_text(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.text.return_value = self._make_text("myproject")
            result = prompts.ask_project_name()
            assert result == "myproject"

    def test_ask_target_project_returns_selection(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("myproject")
            result = prompts.ask_target_project(["myproject", "other"])
            assert result == "myproject"

    def test_ask_app_name_returns_text(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.text.return_value = self._make_text("blog")
            result = prompts.ask_app_name()
            assert result == "blog"

    def test_ask_app_name_with_default(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.text.return_value = self._make_text("system")
            result = prompts.ask_app_name(default="system")
            assert result == "system"
            _, kwargs = mock_q.text.call_args
            assert kwargs.get("default") == "system"

    def test_ask_enable_i18n(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.confirm.return_value = self._make_select(True)
            result = prompts.ask_enable_i18n()
            assert result is True
            mock_q.confirm.assert_called_once()
            assert "one language" in mock_q.confirm.call_args.args[0]

    def test_parse_language_codes_normalizes_and_deduplicates(self):
        from codex_django_cli import prompts

        result = prompts.parse_language_codes(" EN, ru , de_AT, ru ,, ja ")
        assert result == ["en", "ru", "de-at", "ja"]

    def test_ask_languages_disabled_returns_default_language(self):
        from codex_django_cli import prompts

        result = prompts.ask_languages(enable_i18n=False)
        assert result == ["en"]

    def test_ask_languages_preset_mode(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("preset")
            mock_q.checkbox.return_value = self._make_select(["en", "ru"])
            result = prompts.ask_languages(enable_i18n=True)
            assert result == ["en", "ru"]

    def test_ask_languages_manual_mode(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("manual")
            mock_q.text.return_value = self._make_text("ja, en, de_AT")
            result = prompts.ask_languages(enable_i18n=True)
            assert result == ["ja", "en", "de-at"]

    def test_ask_languages_manual_mode_empty_falls_back_to_en(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("manual")
            mock_q.text.return_value = self._make_text("  ")
            result = prompts.ask_languages(enable_i18n=True)
            assert result == ["en"]

    def test_ask_install_modules_init_mode(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.checkbox.return_value = self._make_checkbox(["cabinet", "booking"])
            result = prompts.ask_install_modules(mode="init")
            assert result == ["cabinet", "booking"]

    def test_ask_install_modules_extend_mode_empty(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.checkbox.return_value = self._make_checkbox(None)
            result = prompts.ask_install_modules(mode="extend")
            assert result == []

    def test_ask_confirm_plan_false(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.confirm.return_value = self._make_select(False)
            result = prompts.ask_confirm_plan("base, cabinet")
            assert result is False

    def test_ask_init_mode_returns_selection(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.select.return_value = self._make_select("🧩  Custom (choose modules)")
            result = prompts.ask_init_mode()
            assert result == "🧩  Custom (choose modules)"

    def test_ask_init_modules_alias(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.ask_install_modules", return_value=["cabinet"]) as mock_install:
            result = prompts.ask_init_modules()
            mock_install.assert_called_once_with(mode="init")
            assert result == ["cabinet"]

    def test_ask_extension_modules_alias(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.ask_install_modules", return_value=["booking"]) as mock_install:
            result = prompts.ask_extension_modules()
            mock_install.assert_called_once_with(mode="extend")
            assert result == ["booking"]

    def test_ask_with_cloud_db(self):
        from codex_django_cli import prompts

        with patch("codex_django_cli.prompts.questionary") as mock_q:
            mock_q.confirm.return_value = self._make_select(True)
            result = prompts.ask_with_cloud_db()
            assert result is True
