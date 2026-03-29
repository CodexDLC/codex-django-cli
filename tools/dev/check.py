"""Quality gate for codex-django-cli."""

import sys
from pathlib import Path

from codex_core.dev.check_runner import BaseCheckRunner


class CheckRunner(BaseCheckRunner):
    PROJECT_NAME = "codex-django-cli"
    INTEGRATION_REQUIRES = "filesystem only"
    RUN_EXTRA_CHECKS = False
    # CVE-2026-4539: pygments — no fix available yet (latest version)
    AUDIT_FLAGS = "--skip-editable --ignore-vuln CVE-2026-4539"

    def run_tests(self, marker: str = "unit") -> bool:
        self.print_step(f"Running {marker.capitalize()} Tests")
        no_cov = " --no-cov" if marker != "unit" else ""
        cmd = f'"{sys.executable}" -m pytest {self.tests_dir} -m {marker} -v --tb=short{no_cov}'
        success, _ = self.run_command(cmd)
        if success:
            self.print_success(f"{marker.capitalize()} tests passed.")
        else:
            self.print_error(f"{marker.capitalize()} tests failed.")
        return success

    def check_security(self) -> bool:
        self.print_step("Security Audit (pip-audit)")
        success, out = self.run_command(
            f'"{sys.executable}" -m pip_audit {self.AUDIT_FLAGS}',
            capture_output=True,
        )
        if not success:
            self.print_error(f"Security audit failed:\n{out}")
        else:
            self.print_success("Security audit passed.")
        return success


if __name__ == "__main__":
    CheckRunner(Path(__file__).parent.parent.parent).main()
