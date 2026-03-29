"""Quality gate for codex-django-cli."""

import os
import sys
from pathlib import Path

from codex_core.dev.check_runner import BaseCheckRunner, Colors


class CheckRunner(BaseCheckRunner):
    PROJECT_NAME = "codex-django-cli"
    INTEGRATION_REQUIRES = "filesystem only"
    E2E_REQUIRES = "isolated venv + local filesystem"
    RUN_EXTRA_CHECKS = False
    # CVE-2026-4539: pygments — no fix available yet (latest version)
    AUDIT_FLAGS = "--skip-editable --ignore-vuln CVE-2026-4539"

    def run_tests(self, marker: str = "unit") -> bool:
        self.print_step(f"Running {marker.capitalize()} Tests")
        cov_args = " --cov=src/codex_django_cli --cov-report=term-missing" if marker == "unit" else ""
        no_cov = " --no-cov" if marker != "unit" else ""
        live_output = " -s" if marker == "e2e" else ""
        cmd = f'"{sys.executable}" -m pytest {self.tests_dir} -m {marker} -v --tb=short{cov_args}{no_cov}{live_output}'
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

    def run_all(self) -> None:
        """Developer mode with optional integration and optional e2e prompts."""
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")

        print(f"{Colors.HEADER}{Colors.BOLD}=== {self.PROJECT_NAME} quality gate ==={Colors.ENDC}")

        if self.RUN_LINT and not self.check_quality():
            sys.exit(1)
        if not self.RUN_LINT:
            self.print_skip("Skipping quality hooks (RUN_LINT=False).")

        if self.RUN_TYPES and not self.check_types():
            sys.exit(1)
        if not self.RUN_TYPES:
            self.print_skip("Skipping mypy (RUN_TYPES=False).")

        if self.RUN_SECURITY and not self.check_security():
            sys.exit(1)
        if not self.RUN_SECURITY:
            self.print_skip("Skipping security audit (RUN_SECURITY=False).")

        if self.RUN_EXTRA_CHECKS and not self.extra_checks():
            sys.exit(1)
        if not self.RUN_EXTRA_CHECKS:
            self.print_skip("Skipping extra checks (RUN_EXTRA_CHECKS=False).")

        if self.RUN_UNIT_TESTS and not self.run_tests("unit"):
            sys.exit(1)
        if not self.RUN_UNIT_TESTS:
            self.print_skip("Skipping unit tests (RUN_UNIT_TESTS=False).")

        if self.RUN_INTEGRATION_TESTS:
            integration_prompt = (
                f"\n{Colors.YELLOW}🚀 Run Integration Tests? "
                f"(Requires: {self.INTEGRATION_REQUIRES}) [y/N]: {Colors.ENDC}"
            )
            if input(integration_prompt).lower() == "y" and not self.run_tests("integration"):
                sys.exit(1)
        else:
            self.print_skip("Skipping integration tests (RUN_INTEGRATION_TESTS=False).")

        e2e_prompt = f"\n{Colors.YELLOW}🚀 Run E2E Tests? (Requires: {self.E2E_REQUIRES}) [y/N]: {Colors.ENDC}"
        if input(e2e_prompt).lower() == "y" and not self.run_tests("e2e"):
            sys.exit(1)

        print(f"\n{Colors.GREEN}{Colors.BOLD}ALL CHECKS PASSED!{Colors.ENDC}")


if __name__ == "__main__":
    CheckRunner(Path(__file__).parent.parent.parent).main()
