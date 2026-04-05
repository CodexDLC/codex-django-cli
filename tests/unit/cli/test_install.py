"""Unit tests for install orchestrator."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from codex_django_cli.commands.install import (
    InstallSelection,
    _normalize_languages,
    _resolve_scaffold_paths,
    describe_plan,
    resolve_install_selection,
)


@pytest.mark.unit
def test_resolve_install_selection_base_mode_forces_conversations_and_cabinet_for_booking():
    plan = resolve_install_selection(
        InstallSelection(cabinet=False, booking=False, conversations=False, public_booking=True, sw=True),
        base_mode=True,
    )

    assert plan.cabinet is True
    assert plan.booking is True
    assert plan.conversations is True
    assert plan.public_booking is True
    assert plan.sw is True
    assert plan.module_labels() == ["base", "cabinet", "conversations", "booking", "public-booking", "sw"]
    assert describe_plan(plan) == "base, cabinet, conversations, booking, public-booking, sw"


@pytest.mark.unit
def test_resolve_install_selection_existing_project_respects_conversations_flag():
    plan = resolve_install_selection(
        InstallSelection(cabinet=False, booking=False, conversations=False, public_booking=False, sw=False),
        base_mode=False,
    )

    assert plan.cabinet is False
    assert plan.booking is False
    assert plan.conversations is False
    assert plan.public_booking is False
    assert plan.sw is False
    assert plan.module_labels() == ["base"]


@pytest.mark.unit
def test_normalize_languages_deduplicates_and_normalizes():
    assert _normalize_languages([" EN ", "de_AT", "en", "ru"]) == ["en", "de-at", "ru"]
    assert _normalize_languages([]) == ["en"]
    assert _normalize_languages(None) == ["en"]


@pytest.mark.unit
def test_resolve_scaffold_paths_default_and_explicit_target(tmp_path: Path):
    project_root, backend_dir = _resolve_scaffold_paths("demo", str(tmp_path), None, False)
    assert project_root == str(tmp_path / "demo")
    assert backend_dir == str(tmp_path / "demo" / "src" / "demo")

    project_root, backend_dir = _resolve_scaffold_paths("demo", str(tmp_path), str(tmp_path / "custom"), False)
    assert project_root == str(tmp_path / "custom")
    assert backend_dir == str(tmp_path / "custom" / "src" / "demo")


@pytest.mark.unit
def test_scaffold_new_project_with_booking_and_public_booking(tmp_path: Path):
    with (
        patch('codex_django_cli.commands.install._resolve_scaffold_paths', return_value=(str(tmp_path / 'root'), str(tmp_path / 'root' / 'src' / 'demo'))),
        patch('codex_django_cli.commands.install.os.path.exists', return_value=False),
        patch('codex_django_cli.commands.repo.handle_generate_repo_config') as mock_repo_config,
        patch('codex_django_cli.commands.install.console.print') as mock_print,
        patch('codex_django_cli.engine.CLIEngine') as mock_engine_cls,
    ):
        mock_engine = MagicMock()
        mock_engine_cls.return_value = mock_engine

        from codex_django_cli.commands.install import scaffold_new_project

        plan = scaffold_new_project(
            name='demo',
            base_dir=str(tmp_path),
            target_dir=None,
            selection=InstallSelection(cabinet=False, booking=False, public_booking=True, sw=True),
            languages=['ru', 'en'],
        )

        assert plan is not None
        assert plan.booking is True
        assert plan.public_booking is True
        assert plan.cabinet is True
        assert plan.sw is True
        calls = mock_engine.scaffold.call_args_list
        names = [call.args[0] for call in calls]
        assert names == ['project', 'cabinet', 'features/conversations', 'features/booking_core', 'features/booking_public']
        context = calls[-1].kwargs['context']
        assert context['with_booking'] is True
        assert context['with_public_booking'] is True
        assert context['with_sw'] is True
        assert context['languages'] == ['ru', 'en']
        mock_repo_config.assert_called_once_with(
            name='demo',
            project_root=str(tmp_path / 'root'),
            include_pyproject=True,
            include_env_example=True,
            overwrite=False,
        )
        assert any('Modules:' in str(call.args[0]) for call in mock_print.call_args_list if call.args)


@pytest.mark.unit
def test_scaffold_new_project_returns_none_when_dev_mode_invalid(tmp_path: Path):
    with (
        patch('codex_django_cli.commands.install._resolve_scaffold_paths', side_effect=ValueError('bad dev mode')),
        patch('codex_django_cli.commands.install.console.print') as mock_print,
    ):
        from codex_django_cli.commands.install import scaffold_new_project

        plan = scaffold_new_project(
            name='demo',
            base_dir=str(tmp_path),
            target_dir=None,
            selection=InstallSelection(dev_mode=True),
            languages=None,
        )

        assert plan is None
        assert 'bad dev mode' in str(mock_print.call_args.args[0])


@pytest.mark.unit
def test_scaffold_existing_project_scaffolds_requested_modules(tmp_path: Path):
    with (
        patch('codex_django_cli.engine.CLIEngine') as mock_engine_cls,
        patch('codex_django_cli.commands.install.console.print') as mock_print,
    ):
        mock_engine = MagicMock()
        mock_engine_cls.return_value = mock_engine

        from codex_django_cli.commands.install import scaffold_existing_project

        plan = scaffold_existing_project(
            project_dir=str(tmp_path),
            selection=InstallSelection(cabinet=False, booking=False, conversations=True, public_booking=True, overwrite=True, i18n=True),
        )

        assert plan.cabinet is True
        assert plan.booking is True
        assert plan.conversations is True
        assert plan.public_booking is True
        calls = mock_engine.scaffold.call_args_list
        names = [call.args[0] for call in calls]
        assert names == ['cabinet', 'features/conversations', 'features/booking_core', 'features/booking_public']
        assert calls[0].kwargs['overwrite'] is True
        assert calls[0].kwargs['context']['enable_i18n'] is True
        assert any('Modules installed' in str(call.args[0]) for call in mock_print.call_args_list if call.args)
