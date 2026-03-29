from __future__ import annotations

import shlex
import subprocess
import sys
import time
import venv
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
RUNTIME_ROOT = PROJECT_ROOT.parent / "codex-django"


def _venv_binaries(venv_dir: Path) -> tuple[Path, Path]:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe", venv_dir / "Scripts" / "codex-django.exe"
    return venv_dir / "bin" / "python", venv_dir / "bin" / "codex-django"


@pytest.fixture
def blueprints_dir() -> Path:
    return PROJECT_ROOT / "src" / "codex_django_cli" / "blueprints"


@pytest.fixture
def run_checked_subprocess() -> Callable[
    [Sequence[str | Path], Path, Mapping[str, str] | None, bool, str | None],
    subprocess.CompletedProcess[str],
]:
    """Run subprocess command and fail with full diagnostics on non-zero exit."""

    def _run(
        cmd: Sequence[str | Path],
        cwd: Path,
        env: Mapping[str, str] | None = None,
        stream_output: bool = False,
        label: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        normalized_cmd = [str(part) for part in cmd]
        rendered_cmd = " ".join(shlex.quote(part) for part in normalized_cmd)
        prefix = f"[subprocess:{label}]" if label else "[subprocess]"
        print(f"{prefix} $ {rendered_cmd} (cwd={cwd})")

        start = time.perf_counter()
        result = subprocess.run(
            normalized_cmd,
            cwd=str(cwd),
            capture_output=not stream_output,
            text=True,
            env=dict(env) if env is not None else None,
        )
        elapsed = time.perf_counter() - start
        print(f"{prefix} finished rc={result.returncode} in {elapsed:.1f}s")

        if result.returncode != 0:
            if stream_output:
                pytest.fail(
                    "Command failed:\n"
                    f"  cmd: {rendered_cmd}\n"
                    f"  cwd: {cwd}\n"
                    f"  exit: {result.returncode}\n"
                    "  Output was streamed live; rerun with logs if needed."
                )
            pytest.fail(
                "Command failed:\n"
                f"  cmd: {rendered_cmd}\n"
                f"  cwd: {cwd}\n"
                f"  exit: {result.returncode}\n"
                f"  stdout:\n{result.stdout}\n"
                f"  stderr:\n{result.stderr}"
            )
        return result

    return _run


@pytest.fixture
def install_chain_env(tmp_path: Path) -> dict[str, Path]:
    """Create a clean subprocess sandbox with isolated venv, but without package installs."""
    venv_dir = tmp_path / ".venv"
    venv.create(str(venv_dir), with_pip=True)
    python, cli = _venv_binaries(venv_dir)
    work_dir = tmp_path / "project"
    work_dir.mkdir()

    return {
        "venv_dir": venv_dir,
        "work_dir": work_dir,
        "python": python,
        "cli": cli,
        "project_root": PROJECT_ROOT,
    }


@pytest.fixture
def sterile_env(
    install_chain_env: dict[str, Path],
    run_checked_subprocess: Callable[
        [Sequence[str | Path], Path, Mapping[str, str] | None, bool, str | None],
        subprocess.CompletedProcess[str],
    ],
) -> dict[str, Path]:
    """Install runtime + CLI packages into an isolated venv for subprocess tests."""
    run_checked_subprocess(
        [
            install_chain_env["python"],
            "-m",
            "pip",
            "install",
            "--quiet",
            "-e",
            str(RUNTIME_ROOT),
            "-e",
            str(PROJECT_ROOT),
        ],
        cwd=install_chain_env["work_dir"],
    )
    return install_chain_env
