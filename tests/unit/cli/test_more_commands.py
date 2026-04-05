"""Unit tests for deploy, quality, and utils CLI modules."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_ENGINE_PATH = "codex_django_cli.engine.CLIEngine"


# ---------------------------------------------------------------------------
# deploy.py
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestHandleGenerateDeploy:
    # deploy.py imports CLIEngine at module level, so we patch the local name
    _DEPLOY_ENGINE = "codex_django_cli.commands.deploy.CLIEngine"

    def test_scaffolds_deploy_files(self, tmp_path: Path):
        with patch(self._DEPLOY_ENGINE) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            from codex_django_cli.commands.deploy import handle_generate_deploy

            handle_generate_deploy("myproject", str(tmp_path))

            # Now scaffolds: deploy/shared + deploy/standalone + deploy/standalone_workflows
            assert mock_engine.scaffold.call_count == 3
            first_call = mock_engine.scaffold.call_args_list[0]
            assert first_call[0][0] == "deploy/shared"
            assert first_call[1]["context"]["project_name"] == "myproject"

    def test_deploy_target_dir_is_inside_deploy_folder(self, tmp_path: Path):
        with patch(self._DEPLOY_ENGINE) as mock_engine_cls:
            mock_engine = MagicMock()
            mock_engine_cls.return_value = mock_engine

            from codex_django_cli.commands.deploy import handle_generate_deploy

            handle_generate_deploy("testapp", str(tmp_path))

            # Docker files go to <project_root>/deploy/
            first_call = mock_engine.scaffold.call_args_list[0]
            target_dir = first_call[1]["target_dir"]
            assert "deploy" in target_dir


# ---------------------------------------------------------------------------
# quality.py
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestHandleConfigurePrecommit:
    def test_creates_precommit_config(self, tmp_path: Path):
        from codex_django_cli.commands.quality import handle_configure_precommit

        handle_configure_precommit(str(tmp_path))

        config = tmp_path / ".pre-commit-config.yaml"
        assert config.exists()
        content = config.read_text(encoding="utf-8")
        assert "ruff" in content
        assert "bandit" in content

    def test_creates_secrets_baseline_if_missing(self, tmp_path: Path):
        from codex_django_cli.commands.quality import handle_configure_precommit

        handle_configure_precommit(str(tmp_path))

        baseline = tmp_path / ".secrets.baseline"
        assert baseline.exists()

    def test_does_not_overwrite_existing_baseline(self, tmp_path: Path):
        import json

        baseline = tmp_path / ".secrets.baseline"
        baseline.write_text(json.dumps({"custom": True}), encoding="utf-8")

        from codex_django_cli.commands.quality import handle_configure_precommit

        handle_configure_precommit(str(tmp_path))

        # Existing baseline should not be overwritten
        content = json.loads(baseline.read_text(encoding="utf-8"))
        assert content.get("custom") is True


# ---------------------------------------------------------------------------
# utils.py
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestRunDjangoCommand:
    def test_executes_command_successfully(self):
        management = MagicMock()
        with patch("codex_django_cli.utils.import_module", return_value=management):
            from codex_django_cli.utils import run_django_command

            run_django_command(["migrate"])

            management.execute_from_command_line.assert_called_once_with(["manage.py", "migrate"])

    def test_handles_system_exit_zero(self):
        management = MagicMock()
        management.execute_from_command_line.side_effect = SystemExit(0)
        with patch("codex_django_cli.utils.import_module", return_value=management):
            from codex_django_cli.utils import run_django_command

            # Should not raise
            run_django_command(["migrate"])

    def test_handles_system_exit_nonzero(self, capsys):
        management = MagicMock()
        management.execute_from_command_line.side_effect = SystemExit(1)
        with patch("codex_django_cli.utils.import_module", return_value=management):
            from codex_django_cli.utils import run_django_command

            run_django_command(["migrate"])

            captured = capsys.readouterr()
            assert "failed" in captured.out.lower() or "1" in captured.out

    def test_handles_generic_exception(self, capsys):
        management = MagicMock()
        management.execute_from_command_line.side_effect = RuntimeError("boom")
        with patch("codex_django_cli.utils.import_module", return_value=management):
            from codex_django_cli.utils import run_django_command

            run_django_command(["migrate"])

            captured = capsys.readouterr()
            assert "boom" in captured.out
