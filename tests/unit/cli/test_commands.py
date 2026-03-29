"""Unit tests for CLI command handlers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import ANY, MagicMock, call, patch

import pytest

_ENGINE_PATH = "codex_django_cli.engine.CLIEngine"


@pytest.mark.unit
class TestHandleInit:
    def test_scaffolds_project(self, tmp_path: Path):
        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            from codex_django_cli.commands.init import handle_init

            handle_init("myproject", str(tmp_path))

            assert mock_engine.scaffold.call_count == 7
            calls = mock_engine.scaffold.call_args_list
            base_context = {
                "project_name": "myproject",
                "secret_key": ANY,
                "enable_i18n": False,
                "languages": ["en"],
                "with_cabinet": False,
                "with_booking": False,
            }
            assert calls[0] == call(
                "repo",
                target_dir=str(tmp_path / "myproject"),
                context=base_context,
                overwrite=False,
            )
            assert calls[1] == call(
                "deploy/shared",
                target_dir=str(tmp_path / "myproject" / "deploy"),
                context=base_context,
                overwrite=False,
            )
            assert calls[2] == call(
                "project",
                target_dir=str(tmp_path / "myproject" / "src" / "myproject"),
                context=base_context,
                overwrite=False,
            )
            assert calls[3] == call(
                "features/notifications/feature/models",
                target_dir=str(tmp_path / "myproject" / "src" / "myproject" / "system" / "models"),
                context={**base_context, "app_name": "system"},
            )
            assert calls[4] == call(
                "features/notifications/feature/selectors",
                target_dir=str(tmp_path / "myproject" / "src" / "myproject" / "system" / "selectors"),
                context={**base_context, "app_name": "system"},
            )
            assert calls[5] == call(
                "features/notifications/feature/services",
                target_dir=str(tmp_path / "myproject" / "src" / "myproject" / "system" / "services"),
                context={**base_context, "app_name": "system"},
            )
            assert calls[6] == call(
                "features/notifications/arq",
                target_dir=str(tmp_path / "myproject" / "src" / "myproject" / "core" / "arq"),
                context={**base_context, "app_name": "system"},
            )

            env_path = tmp_path / "myproject" / ".env"
            assert env_path.exists()
            env_content = env_path.read_text(encoding="utf-8")
            assert "SECRET_KEY=" in env_content
            assert "FIELD_ENCRYPTION_KEY=" in env_content
            assert "replace-with-your" not in env_content

    def test_skips_if_target_exists(self, tmp_path: Path):
        manage_py = tmp_path / "myproject" / "src" / "myproject" / "manage.py"
        manage_py.parent.mkdir(parents=True)
        manage_py.write_text("")

        with patch(_ENGINE_PATH) as mock_engine_cls:
            from codex_django_cli.commands.init import handle_init

            handle_init("myproject", str(tmp_path))

            mock_engine_cls.return_value.scaffold.assert_not_called()

    def test_uses_correct_project_name_in_context(self, tmp_path: Path):
        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            from codex_django_cli.commands.init import handle_init

            handle_init("my_app", str(tmp_path))

            _, kwargs = mock_engine.scaffold.call_args
            assert kwargs["context"]["project_name"] == "my_app"

    def test_target_dir(self, tmp_path: Path):
        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine
            from codex_django_cli.commands.init import handle_init

            handle_init("myproject", "base_dir", target_dir=str(tmp_path))
            calls = mock_engine.scaffold.call_args_list
            assert calls[0][1]["target_dir"] == str(tmp_path)

    def test_dev_mode_valid(self, tmp_path: Path):
        from unittest.mock import mock_open

        with (
            patch(_ENGINE_PATH) as mock_engine_cls,
            patch("os.path.exists", side_effect=lambda path: str(path).endswith("pyproject.toml")),
            patch("builtins.open", mock_open(read_data='name = "codex-django"')),
        ):
            from codex_django_cli.commands.init import handle_init

            handle_init("myproject", "base_dir", dev_mode=True)
            mock_engine_cls.return_value.scaffold.assert_called()

    def test_dev_mode_invalid(self, tmp_path: Path):
        with patch("os.path.exists", return_value=False):
            from codex_django_cli.commands.init import handle_init

            handle_init("myproject", "base_dir", dev_mode=True)

    def test_code_only(self, tmp_path: Path):
        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine
            from codex_django_cli.commands.init import handle_init

            handle_init("myproject", str(tmp_path), code_only=True)
            assert mock_engine.scaffold.call_count == 5
            assert not (tmp_path / "myproject" / ".env").exists()

    def test_i18n_languages_context(self, tmp_path: Path):
        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine
            from codex_django_cli.commands.init import handle_init

            handle_init("myproject", str(tmp_path), enable_i18n=True, languages=["en", "ru", "de"])

            _, kwargs = mock_engine.scaffold.call_args
            context = kwargs["context"]
            assert context["enable_i18n"] is True
            assert context["languages"] == ["en", "ru", "de"]

    def test_i18n_context_allows_single_language(self, tmp_path: Path):
        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine
            from codex_django_cli.commands.init import handle_init

            handle_init("myproject", str(tmp_path), enable_i18n=True, languages=["ja"])

            _, kwargs = mock_engine.scaffold.call_args
            context = kwargs["context"]
            assert context["enable_i18n"] is True
            assert context["languages"] == ["ja"]

    def test_i18n_single_language_init_output_mentions_translation_aware_config(self, tmp_path: Path):
        with (
            patch(_ENGINE_PATH) as mock_engine_cls,
            patch("codex_django_cli.commands.init.console.print") as mock_print,
        ):
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine
            from codex_django_cli.commands.init import handle_init

            handle_init("myproject", str(tmp_path), enable_i18n=True, languages=["en"])

            rendered = "\n".join(str(call.args[0]) for call in mock_print.call_args_list if call.args)
            assert "translation-aware settings" in rendered
            assert "single selected language" in rendered

    def test_explicit_languages_enable_i18n_even_without_flag(self, tmp_path: Path):
        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine
            from codex_django_cli.commands.init import handle_init

            handle_init("myproject", str(tmp_path), enable_i18n=False, languages=["ja", "en"])

            _, kwargs = mock_engine.scaffold.call_args
            context = kwargs["context"]
            assert context["enable_i18n"] is True
            assert context["languages"] == ["ja", "en"]


@pytest.mark.unit
class TestHandleAddApp:
    def test_scaffolds_app(self, tmp_path: Path):
        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            from codex_django_cli.commands.add_app import handle_add_app

            handle_add_app("blog", str(tmp_path))

            mock_engine.scaffold.assert_called_once_with(
                "apps/default",
                target_dir=str(tmp_path / "features" / "blog"),
                context={"app_name": "blog"},
            )

    def test_skips_if_app_exists(self, tmp_path: Path):
        target = tmp_path / "features" / "blog"
        target.mkdir(parents=True)

        with patch(_ENGINE_PATH) as mock_engine_cls:
            from codex_django_cli.commands.add_app import handle_add_app

            handle_add_app("blog", str(tmp_path))

            mock_engine_cls.return_value.scaffold.assert_not_called()


@pytest.mark.unit
class TestHandleAddNotifications:
    def test_scaffolds_feature_and_arq(self, tmp_path: Path):
        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            from codex_django_cli.commands.notifications import handle_add_notifications

            handle_add_notifications("system", str(tmp_path))

            calls = mock_engine.scaffold.call_args_list
            assert len(calls) == 4

            assert calls[0][0][0] == "features/notifications/feature/models"
            assert calls[0][1]["target_dir"] == str(tmp_path / "system" / "models")
            assert calls[0][1]["context"] == {"app_name": "system"}

            assert calls[1][0][0] == "features/notifications/feature/selectors"
            assert calls[1][1]["target_dir"] == str(tmp_path / "system" / "selectors")

            assert calls[2][0][0] == "features/notifications/feature/services"
            assert calls[2][1]["target_dir"] == str(tmp_path / "system" / "services")

            arq_call = calls[3]
            assert arq_call[0][0] == "features/notifications/arq"
            assert arq_call[1]["target_dir"] == str(tmp_path / "core" / "arq")

    def test_custom_arq_dir(self, tmp_path: Path):
        import os

        with patch(_ENGINE_PATH) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            from codex_django_cli.commands.notifications import handle_add_notifications

            handle_add_notifications("system", str(tmp_path), arq_dir="myapp/arq")

            arq_call = mock_engine.scaffold.call_args_list[3]
            expected = os.path.join(str(tmp_path), "myapp/arq")
            assert arq_call[1]["target_dir"] == expected

