"""Integration tests: generated cabinet.py files must use Cabinet 2.0 declare() API."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from codex_django_cli.commands.init import handle_init

# Internal paths that must NOT appear in generated cabinet.py files.
_FORBIDDEN_IMPORT_PREFIXES = [
    "codex_django.cabinet._internal",
    "codex_django.cabinet.declare.api",
    "codex_django.cabinet.registry.api",
]

# Internal import path that was used before Cabinet 2.0.
_FORBIDDEN_BOOKING_CABINET_TYPES = "codex_django.booking.cabinet.types"


def _backend_dir(project_root: Path, name: str) -> Path:
    return project_root / name / "src" / name


def _find_cabinet_registration_files(backend: Path) -> list[Path]:
    """Return cabinet.py files that are module registration entrypoints (not service files)."""
    results = []
    for p in backend.rglob("cabinet.py"):
        # cabinet/cabinet.py — stub placeholder, no declarations needed
        if p.parent.name == "cabinet":
            continue
        # services/cabinet.py — workflow/service layer, not a registration file
        if p.parent.name == "services":
            continue
        results.append(p)
    return results


def _find_cabinet_py_files(backend: Path) -> list[Path]:
    return list(backend.rglob("cabinet.py"))


@pytest.mark.integration
class TestCabinetApiSurface:
    """Verify generated cabinet.py files conform to Cabinet 2.0 public API."""

    def test_cabinet_py_files_use_declare(self, tmp_path: Path) -> None:
        """All non-empty generated cabinet.py registration files must call declare(...)."""
        handle_init("testproj", str(tmp_path), with_booking=True, with_conversations=True)
        backend = _backend_dir(tmp_path, "testproj")

        files = _find_cabinet_registration_files(backend)
        assert files, "No cabinet.py registration files were generated"

        for path in files:
            content = path.read_text(encoding="utf-8").strip()
            if not content:
                continue
            # Skip files that are intentionally empty stubs (comment-only)
            code_lines = [ln for ln in content.splitlines() if ln.strip() and not ln.strip().startswith("#")]
            if not code_lines:
                continue
            assert "declare(" in content, f"{path.relative_to(backend)}: expected declare() call but not found"

    def test_cabinet_py_imports_from_public_api(self, tmp_path: Path) -> None:
        """cabinet.py files must import from codex_django.cabinet (public), not internal paths."""
        handle_init("testproj", str(tmp_path), with_booking=True, with_conversations=True)
        backend = _backend_dir(tmp_path, "testproj")

        for path in _find_cabinet_registration_files(backend):
            content = path.read_text(encoding="utf-8")
            for forbidden in _FORBIDDEN_IMPORT_PREFIXES:
                assert forbidden not in content, f"{path.relative_to(backend)}: forbidden internal import '{forbidden}'"

    def test_booking_cabinet_service_no_internal_types_import(self, tmp_path: Path) -> None:
        """features/booking/services/cabinet.py must not import from booking.cabinet.types directly."""
        handle_init("testproj", str(tmp_path), with_booking=True)
        backend = _backend_dir(tmp_path, "testproj")

        cabinet_svc = backend / "features" / "booking" / "services" / "cabinet.py"
        assert cabinet_svc.exists(), "features/booking/services/cabinet.py not generated"

        content = cabinet_svc.read_text(encoding="utf-8")
        assert _FORBIDDEN_BOOKING_CABINET_TYPES not in content, (
            "booking services/cabinet.py imports from internal .cabinet.types path; "
            "use codex_django.booking.cabinet instead"
        )

    def test_analytics_dashboard_selector_has_cache_ttl(self, tmp_path: Path) -> None:
        """DashboardSelector providers in analytics.py must declare cache_ttl > 0."""
        handle_init("testproj", str(tmp_path))
        backend = _backend_dir(tmp_path, "testproj")

        analytics = backend / "cabinet" / "services" / "analytics.py"
        assert analytics.exists(), "cabinet/services/analytics.py not generated"

        content = analytics.read_text(encoding="utf-8")
        ttl_values = re.findall(r"cache_ttl\s*=\s*(\d+)", content)
        assert ttl_values, "No cache_ttl found in DashboardSelector.extend() calls"
        assert all(int(v) > 0 for v in ttl_values), (
            f"All DashboardSelector providers should have cache_ttl > 0, got: {ttl_values}"
        )
