"""Template rendering and file generation engine for the CLI.

Examples:
    Render a blueprint template manually::

        from codex_django_cli.engine import CLIEngine

        engine = CLIEngine()
        content = engine.render_template("repo/README.md.j2", {"project_name": "demo"})
"""

import logging
import os
import shutil
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape


class CLIEngine:
    """Core engine for CLI template rendering and scaffold generation."""

    def __init__(self, blueprints_dir: str | None = None):
        """Initialize the engine and Jinja environment.

        Args:
            blueprints_dir: Optional path to the blueprint root. Defaults to
                the bundled ``blueprints`` directory next to this module.
        """
        if blueprints_dir is None:
            # Default to the blueprints directory relative to this file
            blueprints_dir = os.path.join(os.path.dirname(__file__), "blueprints")
        self.blueprints_dir = blueprints_dir
        self.env = Environment(
            loader=FileSystemLoader(self.blueprints_dir),
            autoescape=select_autoescape(),
            keep_trailing_newline=True,
        )
        self.logger = logging.getLogger(__name__)

    def render_template(self, template_name: str, context: dict[str, Any]) -> str:
        """Render a blueprint template with the provided context.

        Args:
            template_name: Template path relative to the blueprint root.
            context: Render context passed into Jinja.

        Returns:
            Rendered template text.

        Raises:
            ValueError: If the template cannot be found.
        """
        try:
            template = self.env.get_template(template_name)
        except TemplateNotFound as exc:
            raise ValueError(f"Template not found: {template_name}") from exc
        return template.render(**context)

    def scaffold(self, blueprint_name: str, target_dir: str, context: dict[str, Any], overwrite: bool = False) -> None:
        """Copy a blueprint tree to the target directory.

        The method renders ``.j2`` files through Jinja and copies all other
        files verbatim.

        Args:
            blueprint_name: Blueprint path relative to the blueprint root.
            target_dir: Filesystem directory where files should be written.
            context: Render context passed into Jinja templates.
            overwrite: Whether existing files may be replaced.

        Raises:
            ValueError: If the named blueprint directory does not exist.
        """
        source_dir = os.path.join(self.blueprints_dir, blueprint_name)
        if not os.path.exists(source_dir):
            raise ValueError(f"Blueprint '{blueprint_name}' not found in {self.blueprints_dir}")

        for root, _, files in os.walk(source_dir):
            # Calculate relative path from source_dir
            rel_path = os.path.relpath(root, source_dir)

            # Destination directory
            dest_dir = os.path.normpath(os.path.join(target_dir, rel_path))
            os.makedirs(dest_dir, exist_ok=True)

            # Prefer templated sources when both `foo` and `foo.j2` exist.
            # This keeps scaffold output deterministic and renders the variant.
            preferred_files: dict[str, str] = {}
            for file in sorted(files):
                output_name = file[:-3] if file.endswith(".j2") else file
                current = preferred_files.get(output_name)
                if current is None or file.endswith(".j2"):
                    preferred_files[output_name] = file

            for dest_file_name, file in preferred_files.items():
                source_file = os.path.join(root, file)

                # Determine destination filename
                is_template = bool(file.endswith(".j2"))

                dest_file_path = os.path.join(dest_dir, dest_file_name)

                if os.path.exists(dest_file_path) and not overwrite:
                    self.logger.info(f"Skipping existing file: {dest_file_path}")
                    continue

                if is_template:
                    # Template path relative to blueprints_dir
                    rel_template_path = os.path.relpath(source_file, self.blueprints_dir).replace("\\", "/")
                    content = self.render_template(rel_template_path, context)
                    with open(dest_file_path, "w", encoding="utf-8") as f:
                        f.write(content)
                else:
                    shutil.copy2(source_file, dest_file_path)

                self.logger.info(f"Generated: {dest_file_path}")
