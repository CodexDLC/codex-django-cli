"""Shared helper functions for CLI command execution and bootstrap tasks."""

from __future__ import annotations

import base64
import os
from importlib import import_module
from typing import Any, cast


def generate_secret_key() -> str:
    """Generate a Django-compatible SECRET_KEY value."""
    from secrets import token_urlsafe

    return token_urlsafe(50)


def generate_field_encryption_key() -> str:
    """Generate a Fernet-compatible key for encrypted model fields."""
    return base64.urlsafe_b64encode(os.urandom(32)).decode()


def run_django_command(args: list[str]) -> None:
    """Execute a Django management command in-process.

    Args:
        args: Command arguments without the leading program name.
    """
    management = import_module("django.core.management")
    execute_from_command_line = cast(Any, management.execute_from_command_line)

    # The first argument to execute_from_command_line should be the program name.
    full_args = ["manage.py", *args]
    try:
        execute_from_command_line(full_args)
    except SystemExit as e:
        # Django's execute_from_command_line often calls sys.exit().
        if e.code != 0:
            print(f"\n[red]Command failed with exit code: {e.code}[/red]")
    except Exception as e:
        print(f"\n[red]Error executing command: {e}[/red]")
