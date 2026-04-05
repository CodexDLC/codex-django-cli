"""Unit tests for CLI main entry point."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

import codex_django_cli.prompts as prompts_module
from codex_django_cli.main import _handle_cli_args, _interactive_menu, _list_projects, main


@pytest.mark.unit
def test_main_no_args_calls_interactive_menu():
    with patch("codex_django_cli.main._interactive_menu", return_value=0) as mock_menu:
        result = main([])
        mock_menu.assert_called_once()
        assert result == 0


@pytest.mark.unit
def test_main_none_reads_sys_argv():
    with (
        patch("codex_django_cli.main.sys.argv", ["codex-django", "init", "testproj"]),
        patch("codex_django_cli.main._handle_cli_args", return_value=0) as mock_cli,
    ):
        result = main(None)
        mock_cli.assert_called_once_with(["init", "testproj"])
        assert result == 0


@pytest.mark.unit
def test_main_with_args_calls_cli_handler():
    with patch("codex_django_cli.main._handle_cli_args", return_value=0) as mock_cli:
        result = main(["init", "myproject"])
        mock_cli.assert_called_once_with(["init", "myproject"])
        assert result == 0


@pytest.mark.unit
def test_main_menu_subcommand_no_extra_args():
    with patch("codex_django_cli.main._interactive_menu", return_value=0) as mock_menu:
        result = main(["menu"])
        mock_menu.assert_called_once()
        assert result == 0


@pytest.mark.unit
def test_interactive_menu_exit():
    with patch.object(prompts_module, "ask_main_action", return_value="❌  Exit"):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_interactive_menu_none_action():
    with patch.object(prompts_module, "ask_main_action", return_value=None):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_interactive_menu_init(tmp_path: Path):
    with (
        patch.object(prompts_module, "ask_main_action", side_effect=["🚀  Init Django project", "❌  Exit"]),
        patch.object(prompts_module, "ask_project_name", return_value="myproject"),
        patch.object(prompts_module, "ask_init_mode", return_value="⚡  Standard"),
        patch.object(prompts_module, "ask_with_cloud_db", return_value=False),
        patch.object(prompts_module, "ask_enable_i18n", return_value=False),
        patch.object(prompts_module, "ask_confirm_plan", return_value=True),
        patch("codex_django_cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django_cli.commands.init.handle_init") as mock_handle,
    ):
        result = _interactive_menu()
        mock_handle.assert_called_once_with(
            name="myproject",
            base_dir=str(tmp_path),
            target_dir=str(tmp_path),
            overwrite=False,
            enable_i18n=False,
            languages=None,
            with_cabinet=True,
            with_booking=False,
            with_conversations=True,
            with_public_booking=False,
            with_sw=False,
            with_cloud_db=False,
        )
        assert result == 0


@pytest.mark.unit
def test_interactive_menu_extend_existing_install(tmp_path: Path):
    with (
        patch.object(prompts_module, "ask_main_action", side_effect=["🧩  Extend existing Django project", "❌  Exit"]),
        patch("codex_django_cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django_cli.main.os.path.isdir", return_value=True),
        patch("codex_django_cli.main.os.listdir", return_value=["myproject"]),
        patch("codex_django_cli.main.os.path.isfile", return_value=True),
        patch("codex_django_cli.commands.install.detect_project_modules", return_value={"cabinet": False, "conversations": False, "booking": False, "public_booking": False, "sw": False}),
        patch.object(prompts_module, "ask_extension_modules", return_value=["booking"]),
        patch.object(prompts_module, "ask_confirm_plan", return_value=True),
        patch("codex_django_cli.commands.install.scaffold_existing_project") as mock_scaffold,
    ):
        result = _interactive_menu()
        assert result == 0
        call_kwargs = mock_scaffold.call_args.kwargs
        assert call_kwargs["project_dir"] == str(tmp_path / "src" / "myproject")
        assert call_kwargs["selection"].booking is True


@pytest.mark.unit
def test_interactive_menu_extend_existing_compare_copy(tmp_path: Path):
    with (
        patch.object(prompts_module, "ask_main_action", side_effect=["🧩  Extend existing Django project", "❌  Exit"]),
        patch("codex_django_cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django_cli.main.os.path.isdir", return_value=True),
        patch("codex_django_cli.main.os.listdir", return_value=["myproject"]),
        patch("codex_django_cli.main.os.path.isfile", return_value=True),
        patch("codex_django_cli.commands.install.detect_project_modules", return_value={"cabinet": True, "conversations": False, "booking": False, "public_booking": False, "sw": False}),
        patch.object(prompts_module, "ask_extension_modules", return_value=["cabinet"]),
        patch.object(prompts_module, "ask_existing_module_action", return_value="compare"),
        patch.object(prompts_module, "ask_confirm_plan", return_value=True),
        patch("codex_django_cli.commands.install.scaffold_compare_copy") as mock_compare,
    ):
        result = _interactive_menu()
        assert result == 0
        assert mock_compare.call_args.kwargs["project_dir"] == str(tmp_path / "src" / "myproject")
        assert mock_compare.call_args.kwargs["selection"].cabinet is True


@pytest.mark.unit
def test_interactive_menu_deploy_files(tmp_path: Path):
    with (
        patch.object(prompts_module, "ask_main_action", side_effect=["🏗  Generate deployment files", "❌  Exit"]),
        patch("codex_django_cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django_cli.main.os.path.isdir", return_value=True),
        patch("codex_django_cli.main.os.listdir", return_value=["myproject"]),
        patch("codex_django_cli.main.os.path.isfile", return_value=True),
        patch.object(prompts_module, "ask_deploy_mode", return_value="standalone"),
        patch.object(prompts_module, "ask_domain_name", return_value="example.com"),
        patch.object(prompts_module, "ask_deploy_services", return_value={"with_bot": False, "with_worker": False}),
        patch.object(prompts_module, "ask_confirm_action", return_value=True),
        patch("codex_django_cli.commands.deploy.handle_generate_deploy") as mock_handle,
    ):
        assert _interactive_menu() == 0
        assert mock_handle.call_args.kwargs["generate_docker"] is True
        assert mock_handle.call_args.kwargs["generate_cicd"] is False


@pytest.mark.unit
def test_interactive_menu_cicd_files(tmp_path: Path):
    with (
        patch.object(prompts_module, "ask_main_action", side_effect=["🔁  Generate CI/CD workflows", "❌  Exit"]),
        patch("codex_django_cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django_cli.main.os.path.isdir", return_value=True),
        patch("codex_django_cli.main.os.listdir", return_value=["myproject"]),
        patch("codex_django_cli.main.os.path.isfile", return_value=True),
        patch.object(prompts_module, "ask_deploy_mode", return_value="stack"),
        patch.object(prompts_module, "ask_domain_name", return_value="example.com"),
        patch.object(prompts_module, "ask_deploy_services", return_value={"with_bot": False, "with_worker": True}),
        patch.object(prompts_module, "ask_confirm_action", return_value=True),
        patch("codex_django_cli.commands.deploy.handle_generate_deploy") as mock_handle,
    ):
        assert _interactive_menu() == 0
        assert mock_handle.call_args.kwargs["generate_docker"] is False
        assert mock_handle.call_args.kwargs["generate_cicd"] is True


@pytest.mark.unit
def test_interactive_menu_precommit(tmp_path: Path):
    with (
        patch.object(prompts_module, "ask_main_action", side_effect=["🪝  Configure pre-commit", "❌  Exit"]),
        patch("codex_django_cli.main.os.getcwd", return_value=str(tmp_path)),
        patch.object(prompts_module, "ask_confirm_action", return_value=True),
        patch("codex_django_cli.commands.quality.handle_configure_precommit") as mock_handle,
    ):
        assert _interactive_menu() == 0
        mock_handle.assert_called_once_with(str(tmp_path))


@pytest.mark.unit
def test_interactive_menu_repo_config(tmp_path: Path):
    with (
        patch.object(prompts_module, "ask_main_action", side_effect=["📦  Generate repo config files", "❌  Exit"]),
        patch.object(prompts_module, "ask_repo_config_action", return_value="Generate pyproject.toml + .env.example"),
        patch("codex_django_cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django_cli.main.os.path.isdir", return_value=False),
        patch.object(prompts_module, "ask_project_name", return_value="myproject"),
        patch.object(prompts_module, "ask_confirm_action", return_value=True),
        patch("codex_django_cli.commands.repo.handle_generate_repo_config") as mock_handle,
    ):
        assert _interactive_menu() == 0
        mock_handle.assert_called_once_with(
            name="myproject",
            project_root=str(tmp_path),
            include_pyproject=True,
            include_env_example=True,
        )


@pytest.mark.unit
def test_list_projects_filters_hidden_and_non_projects(tmp_path: Path):
    src_dir = tmp_path / "src"
    (src_dir / "myproject").mkdir(parents=True)
    (src_dir / "myproject" / "manage.py").write_text("", encoding="utf-8")
    (src_dir / ".idea").mkdir()
    (src_dir / "__pycache__").mkdir()
    assert _list_projects(str(src_dir)) == ["myproject"]


@pytest.mark.unit
def test_cli_init(tmp_path: Path):
    with (
        patch("codex_django_cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django_cli.commands.init.handle_init") as mock_handle,
    ):
        result = _handle_cli_args(["init", "myproject"])
        mock_handle.assert_called_once_with(
            name="myproject",
            base_dir=str(tmp_path),
            target_dir=None,
            code_only=False,
            dev_mode=False,
            overwrite=False,
            enable_i18n=False,
            languages=None,
            with_cabinet=True,
            with_booking=False,
            with_conversations=True,
            with_public_booking=False,
            with_sw=False,
            with_cloud_db=False,
        )
        assert result == 0


@pytest.mark.unit
def test_cli_init_i18n(tmp_path: Path):
    with (
        patch("codex_django_cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django_cli.commands.init.handle_init") as mock_handle,
    ):
        result = _handle_cli_args(["init", "myproject", "--i18n"])
        mock_handle.assert_called_once()
        assert mock_handle.call_args.kwargs["enable_i18n"] is True
        assert result == 0


@pytest.mark.unit
def test_cli_init_languages_argument(tmp_path: Path):
    with (
        patch("codex_django_cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django_cli.commands.init.handle_init") as mock_handle,
    ):
        result = _handle_cli_args(["init", "myproject", "--languages", "ja, en, de_AT"])
        assert result == 0
        assert mock_handle.call_args.kwargs["languages"] == ["ja", "en", "de-at"]


@pytest.mark.unit
def test_cli_menu_command():
    with patch("codex_django_cli.main._interactive_menu", return_value=0) as mock_menu:
        result = _handle_cli_args(["menu"])
        mock_menu.assert_called_once()
        assert result == 0


@pytest.mark.unit
def test_cli_rejects_removed_add_app_command():
    with pytest.raises(SystemExit):
        _handle_cli_args(["add-app", "blog"])


@pytest.mark.unit
def test_cli_no_command():
    result = _handle_cli_args([])
    assert result == 0


@pytest.mark.unit
def test_cli_deploy_uses_new_flags(tmp_path: Path):
    with (
        patch("codex_django_cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django_cli.commands.deploy.handle_generate_deploy") as mock_handle,
    ):
        result = _handle_cli_args(["deploy", "myproject", "--mode", "stack", "--domain", "prod.example.com", "--with-bot", "--with-worker", "--no-docker"])
        mock_handle.assert_called_once_with(
            name="myproject",
            project_root=str(tmp_path),
            deploy_mode="stack",
            domain_name="prod.example.com",
            with_bot=True,
            with_worker=True,
            generate_docker=False,
            generate_cicd=True,
        )
        assert result == 0


@pytest.mark.unit
def test_interactive_menu_loops_after_back_then_exit():
    with patch.object(prompts_module, "ask_main_action", side_effect=["📦  Generate repo config files", "❌  Exit"]), patch.object(prompts_module, "ask_repo_config_action", return_value="← Back"):
        assert _interactive_menu() == 0


@pytest.mark.unit
def test_interactive_menu_deploy_back_on_mode(tmp_path: Path):
    with (
        patch.object(prompts_module, "ask_main_action", side_effect=["🏗  Generate deployment files", "❌  Exit"]),
        patch("codex_django_cli.main.os.getcwd", return_value=str(tmp_path)),
        patch("codex_django_cli.main.os.path.isdir", return_value=True),
        patch("codex_django_cli.main.os.listdir", return_value=["myproject"]),
        patch("codex_django_cli.main.os.path.isfile", return_value=True),
        patch.object(prompts_module, "ask_deploy_mode", return_value="← Back"),
        patch("codex_django_cli.commands.deploy.handle_generate_deploy") as mock_handle,
    ):
        assert _interactive_menu() == 0
        mock_handle.assert_not_called()
