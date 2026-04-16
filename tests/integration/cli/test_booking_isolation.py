"""Integration tests: booking files must not appear in standard init without booking."""

from __future__ import annotations

from pathlib import Path

import pytest

from codex_django_cli.commands.init import handle_init

# Paths relative to backend_dir (src/<name>/) that belong exclusively to cabinet_booking.
_BOOKING_ONLY_PATHS = [
    "cabinet/booking_bridge.py",
    "cabinet/views/booking.py",
    "cabinet/services/booking.py",
]
_BOOKING_TEMPLATES_DIR = "cabinet/templates/cabinet/booking"


def _backend_dir(project_root: Path, name: str) -> Path:
    return project_root / name / "src" / name


@pytest.mark.integration
class TestBookingIsolation:
    """Verify that booking scaffold is fully isolated behind the with_booking flag."""

    def test_standard_init_without_booking_no_booking_files(self, tmp_path: Path) -> None:
        """Standard init (no booking) must not generate any cabinet_booking artefacts."""
        handle_init("testproj", str(tmp_path), with_booking=False)
        backend = _backend_dir(tmp_path, "testproj")

        for rel in _BOOKING_ONLY_PATHS:
            assert not (backend / rel).exists(), f"Unexpected booking file on disk: {rel}"

        assert not (backend / _BOOKING_TEMPLATES_DIR).exists(), (
            f"Unexpected booking templates directory on disk: {_BOOKING_TEMPLATES_DIR}"
        )

    def test_standard_init_without_booking_urls_has_no_booking_import(self, tmp_path: Path) -> None:
        """Generated cabinet/urls.py must not import from .views.booking when booking=False."""
        handle_init("testproj", str(tmp_path), with_booking=False)
        urls_file = _backend_dir(tmp_path, "testproj") / "cabinet" / "urls.py"

        assert urls_file.exists(), "cabinet/urls.py was not generated"
        content = urls_file.read_text(encoding="utf-8")
        assert "from .views.booking" not in content, (
            "cabinet/urls.py contains booking import but booking was not requested"
        )

    def test_standard_init_without_booking_apps_has_no_booking_app(self, tmp_path: Path) -> None:
        """Generated apps.py must not list features.booking when booking=False."""
        handle_init("testproj", str(tmp_path), with_booking=False)
        apps_file = _backend_dir(tmp_path, "testproj") / "core" / "settings" / "modules" / "apps.py"

        assert apps_file.exists(), "core/settings/modules/apps.py was not generated"
        content = apps_file.read_text(encoding="utf-8")
        assert '"features.booking"' not in content, "apps.py contains features.booking but booking was not requested"

    def test_standard_init_with_booking_includes_cabinet_booking_files(self, tmp_path: Path) -> None:
        """Init with booking must generate all cabinet_booking artefacts."""
        handle_init("testproj", str(tmp_path), with_booking=True)
        backend = _backend_dir(tmp_path, "testproj")

        for rel in _BOOKING_ONLY_PATHS:
            assert (backend / rel).exists(), f"Expected booking file missing on disk: {rel}"

        assert (backend / _BOOKING_TEMPLATES_DIR).is_dir(), (
            f"Expected booking templates directory missing: {_BOOKING_TEMPLATES_DIR}"
        )

    def test_standard_init_with_booking_urls_has_booking_import(self, tmp_path: Path) -> None:
        """Generated cabinet/urls.py must import from .views.booking when booking=True."""
        handle_init("testproj", str(tmp_path), with_booking=True)
        urls_file = _backend_dir(tmp_path, "testproj") / "cabinet" / "urls.py"

        assert urls_file.exists(), "cabinet/urls.py was not generated"
        content = urls_file.read_text(encoding="utf-8")
        assert "from .views.booking" in content, "cabinet/urls.py is missing booking import but booking was requested"

    def test_standard_init_with_booking_apps_lists_booking_app(self, tmp_path: Path) -> None:
        """Generated apps.py must list features.booking when booking=True."""
        handle_init("testproj", str(tmp_path), with_booking=True)
        apps_file = _backend_dir(tmp_path, "testproj") / "core" / "settings" / "modules" / "apps.py"

        assert apps_file.exists(), "core/settings/modules/apps.py was not generated"
        content = apps_file.read_text(encoding="utf-8")
        assert '"features.booking"' in content, "apps.py is missing features.booking but booking was requested"

    def test_analytics_service_has_no_booking_when_not_requested(self, tmp_path: Path) -> None:
        """Generated analytics service must not mention booking when booking=False."""
        import re

        handle_init("testproj", str(tmp_path), with_booking=False)
        analytics_file = _backend_dir(tmp_path, "testproj") / "cabinet" / "services" / "analytics.py"

        assert analytics_file.exists(), "cabinet/services/analytics.py was not generated"
        content = analytics_file.read_text(encoding="utf-8")
        assert not re.search(r"booking", content, re.IGNORECASE), (
            "analytics.py contains 'booking' references but booking was not requested"
        )

    def test_analytics_service_has_booking_metrics_when_requested(self, tmp_path: Path) -> None:
        """Generated analytics service must include booking metric when booking=True."""
        handle_init("testproj", str(tmp_path), with_booking=True)
        analytics_file = _backend_dir(tmp_path, "testproj") / "cabinet" / "services" / "analytics.py"

        assert analytics_file.exists(), "cabinet/services/analytics.py was not generated"
        content = analytics_file.read_text(encoding="utf-8")
        assert '"bookings"' in content, "analytics.py is missing booking metric but booking was requested"
