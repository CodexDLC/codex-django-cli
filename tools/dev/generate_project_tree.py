"""Generate project structure tree."""

import sys
import os
from pathlib import Path

# Add src to sys.path to allow importing codex_django_cli
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from codex_django_cli.dev.project_tree import ProjectTreeGenerator

if __name__ == "__main__":
    ProjectTreeGenerator(Path(__file__).parent.parent.parent).interactive()
