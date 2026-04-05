"""Unit tests for CLI command handlers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_ENGINE_PATH = "codex_django_cli.engine.CLIEngine"


@pytest.mark.unit
class TestHandleInit:
    def test_scaffolds_project(self, tmp_path: Path):
        with (
            patch(_ENGINE_PATH) as mock_engine_cls,
            patch("codex_django_cli.commands.repo.handle_generate_repo_config") as mock_repo_config,
        ):
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            from codex_django_cli.commands.init import handle_init

            handle_init("myproject", str(tmp_path))

            calls = mock_engine.scaffold.call_args_list
            assert len(calls) == 3
            base_context = {
                "project_name": "myproject",
                "enable_i18n": False,
                "languages": ["en"],
                "with_cabinet": True,
                "with_booking": False,
                "with_conversations": True,
                "with_public_booking": False,
                "with_sw": False,
                "with_cloud_db": False,
            }
            assert calls[0].args[0] == "project"
            assert calls[0].kwargs == {
                "target_dir": str(tmp_path / "myproject" / "src" / "myproject"),
                "context": base_context,
                "overwrite": False,
            }
            assert calls[1].args[0] == "cabinet"
            assert calls[1].kwargs == {
                "target_dir": str(tmp_path / "myproject" / "src" / "myproject" / "cabinet"),
                "context": base_context,
                "overwrite": False,
            }
            assert calls[2].args[0] == "features/conversations"
            assert calls[2].kwargs == {
                "target_dir": str(tmp_path / "myproject" / "src" / "myproject"),
                "context": base_context,
                "overwrite": False,
            }
            mock_repo_config.assert_called_once_with(
                name="myproject",
                project_root=str(tmp_path / "myproject"),
                include_pyproject=True,
                include_env_example=True,
                overwrite=False,
            )

    def test_skips_if_target_exists(self, tmp_path: Path):
        manage_py = tmp_path / "myproject" / "src" / "myproject" / "manage.py"
        manage_py.parent.mkdir(parents=True)
        manage_py.write_text("")

        with (
            patch(_ENGINE_PATH) as mock_engine_cls,
            patch("codex_django_cli.commands.repo.handle_generate_repo_config") as mock_repo_config,
        ):
            from codex_django_cli.commands.init import handle_init

            handle_init("myproject", str(tmp_path))

            mock_engine_cls.return_value.scaffold.assert_not_called()
            mock_repo_config.assert_not_called()

    def test_uses_correct_project_name_in_context(self, tmp_path: Path):
        with (
            patch(_ENGINE_PATH) as mock_engine_cls,
            patch("codex_django_cli.commands.repo.handle_generate_repo_config"),
        ):
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            from codex_django_cli.commands.init import handle_init

            handle_init("my_app", str(tmp_path))

            _, kwargs = mock_engine.scaffold.call_args
            assert kwargs["context"]["project_name"] == "my_app"

    def test_target_dir(self, tmp_path: Path):
        with (
            patch(_ENGINE_PATH) as mock_engine_cls,
            patch("codex_django_cli.commands.repo.handle_generate_repo_config") as mock_repo_config,
        ):
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine
            from codex_django_cli.commands.init import handle_init

            handle_init("myproject", "base_dir", target_dir=str(tmp_path))
            calls = mock_engine.scaffold.call_args_list
            assert calls[0].kwargs["target_dir"] == str(tmp_path / "src" / "myproject")
            mock_repo_config.assert_called_once_with(
                name="myproject",
                project_root=str(tmp_path),
                include_pyproject=True,
                include_env_example=True,
                overwrite=False,
            )

    def test_dev_mode_valid(self, tmp_path: Path):
        from unittest.mock import mock_open

        with (
            patch(_ENGINE_PATH) as mock_engine_cls,
            patch("codex_django_cli.commands.repo.handle_generate_repo_config"),
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
        with (
            patch(_ENGINE_PATH) as mock_engine_cls,
            patch("codex_django_cli.commands.repo.handle_generate_repo_config") as mock_repo_config,
        ):
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine
            from codex_django_cli.commands.init import handle_init

            handle_init("myproject", str(tmp_path), code_only=True)
            assert mock_engine.scaffold.call_count == 3
            mock_repo_config.assert_not_called()

    def test_i18n_languages_context(self, tmp_path: Path):
        with (
            patch(_ENGINE_PATH) as mock_engine_cls,
            patch("codex_django_cli.commands.repo.handle_generate_repo_config"),
        ):
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine
            from codex_django_cli.commands.init import handle_init

            handle_init("myproject", str(tmp_path), enable_i18n=True, languages=["en", "ru", "de"])

            _, kwargs = mock_engine.scaffold.call_args
            context = kwargs["context"]
            assert context["enable_i18n"] is True
            assert context["languages"] == ["en", "ru", "de"]

    def test_i18n_context_allows_single_language(self, tmp_path: Path):
        with (
            patch(_ENGINE_PATH) as mock_engine_cls,
            patch("codex_django_cli.commands.repo.handle_generate_repo_config"),
        ):
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
            patch("codex_django_cli.commands.repo.handle_generate_repo_config"),
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
        with (
            patch(_ENGINE_PATH) as mock_engine_cls,
            patch("codex_django_cli.commands.repo.handle_generate_repo_config"),
        ):
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine
            from codex_django_cli.commands.init import handle_init

            handle_init("myproject", str(tmp_path), enable_i18n=False, languages=["ja", "en"])

            _, kwargs = mock_engine.scaffold.call_args
            context = kwargs["context"]
            assert context["enable_i18n"] is True
            assert context["languages"] == ["ja", "en"]
