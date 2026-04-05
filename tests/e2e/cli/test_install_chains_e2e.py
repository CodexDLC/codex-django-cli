"""E2E smoke tests for CLI install chains (local dev and online install paths)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

ONLINE_FLAG_ENV = "CODEX_DJANGO_E2E_ONLINE"
RUNTIME_WHEEL_ENV = "CODEX_DJANGO_WHEEL"
CLI_PYPI_SPEC_ENV = "CODEX_DJANGO_CLI_PYPI_SPEC"
RUNTIME_CHECKOUT_ENV = "CODEX_DJANGO_CHECKOUT"


def _assert_generated_structure(project_root: Path) -> Path:
    generated_root = project_root / "testproj"
    backend_root = generated_root / "src" / "testproj"

    assert generated_root.is_dir(), "Generated project root is missing"
    assert backend_root.is_dir(), "Generated backend root is missing"
    assert (backend_root / "manage.py").exists(), "manage.py was not generated"
    assert (backend_root / "core").is_dir(), "core package missing"
    assert (backend_root / "system").is_dir(), "system package missing"
    assert (backend_root / "cabinet").is_dir(), "cabinet package missing"
    assert (backend_root / "features" / "main" / "apps.py").exists(), "features.main app is missing"
    manage_content = (backend_root / "manage.py").read_text(encoding="utf-8")
    assert "codex_django.cli.main" not in manage_content
    assert 'sys.argv[1] == "menu"' not in manage_content
    assert "forced_project" not in manage_content
    assert "execute_from_command_line(sys.argv)" in manage_content

    return backend_root


def _install_local_dev_chain(
    *,
    python_bin: Path,
    work_dir: Path,
    project_root: Path,
    run_checked_subprocess,
) -> None:
    runtime_checkout = Path(
        os.environ.get(RUNTIME_CHECKOUT_ENV, str(project_root.parent / "codex-django"))
    ).expanduser()
    if not runtime_checkout.exists():
        pytest.skip(
            f"Local install-chain scenario requires checkout at {runtime_checkout}. "
            f"Override via {RUNTIME_CHECKOUT_ENV}."
        )

    run_checked_subprocess(
        [python_bin, "-m", "pip", "install", "--quiet", "-e", str(project_root)],
        cwd=work_dir,
    )
    run_checked_subprocess(
        [python_bin, "-m", "pip", "install", "--quiet", "-e", str(runtime_checkout)],
        cwd=work_dir,
    )


def _install_online_chain(
    *,
    python_bin: Path,
    work_dir: Path,
    run_checked_subprocess,
) -> None:
    if os.environ.get(ONLINE_FLAG_ENV) != "1":
        pytest.skip(f"Online scenario disabled. Set {ONLINE_FLAG_ENV}=1 to enable.")

    wheel_value = os.environ.get(RUNTIME_WHEEL_ENV)
    if not wheel_value:
        pytest.skip(f"Online scenario requires {RUNTIME_WHEEL_ENV}=<absolute wheel path>.")

    runtime_wheel = Path(wheel_value).expanduser()
    assert runtime_wheel.is_file(), f"{RUNTIME_WHEEL_ENV} points to missing file: {runtime_wheel}"

    cli_spec = os.environ.get(CLI_PYPI_SPEC_ENV, "codex-django-cli")
    run_checked_subprocess(
        [python_bin, "-m", "pip", "install", "--quiet", cli_spec],
        cwd=work_dir,
    )
    run_checked_subprocess(
        [python_bin, "-m", "pip", "install", "--quiet", str(runtime_wheel)],
        cwd=work_dir,
    )


@pytest.mark.e2e
@pytest.mark.parametrize("scenario", ["local_dev_chain", "online_install_chain"])
def test_install_chains_smoke(scenario: str, install_chain_env: dict[str, Path], run_checked_subprocess) -> None:
    work_dir = install_chain_env["work_dir"]
    python_bin = install_chain_env["python"]
    cli_bin = install_chain_env["cli"]
    project_root = install_chain_env["project_root"]

    if scenario == "local_dev_chain":
        _install_local_dev_chain(
            python_bin=python_bin,
            work_dir=work_dir,
            project_root=project_root,
            run_checked_subprocess=run_checked_subprocess,
        )
    else:
        _install_online_chain(
            python_bin=python_bin,
            work_dir=work_dir,
            run_checked_subprocess=run_checked_subprocess,
        )

    assert cli_bin.exists(), f"CLI executable not found: {cli_bin}"

    run_checked_subprocess([cli_bin, "init", "testproj"], cwd=work_dir)
    backend_root = _assert_generated_structure(work_dir)
    generated_project_root = work_dir / "testproj"

    run_checked_subprocess(
        [python_bin, "-m", "pip", "install", "--quiet", "-e", "."],
        cwd=generated_project_root,
    )

    manage_py = backend_root / "manage.py"
    run_checked_subprocess([python_bin, str(manage_py), "check"], cwd=generated_project_root)
    run_checked_subprocess([python_bin, str(manage_py), "startserver", "--help"], cwd=generated_project_root)
