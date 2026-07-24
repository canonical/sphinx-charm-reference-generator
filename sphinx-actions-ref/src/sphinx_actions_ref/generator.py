"""Auto-generate standalone reference files from actions.yaml at build time."""

from __future__ import annotations

import logging
from pathlib import Path

from jinja2 import Template
from sphinx.application import Sphinx

from .directive import _normalize_sources
from .parser import ActionsValidationError, load_actions

logger = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).parent / "templates"


def generate_actions_pages(app: Sphinx) -> None:
    """Builder-inited handler: write reference files for each configured source."""
    if not app.config.actions_autogenerate:
        return

    fmt = app.config.actions_output_format
    if fmt not in ("myst", "rst"):
        logger.warning(
            "actions_output_format must be 'myst' or 'rst', got %r; skipping generation",
            fmt,
        )
        return

    ext = ".md" if fmt == "myst" else ".rst"
    template_name = "actions.md.j2" if fmt == "myst" else "actions.rst.j2"
    template_path = _TEMPLATE_DIR / template_name

    with open(template_path, "r", encoding="utf-8") as f:
        template = Template(f.read())

    sources = _normalize_sources(app.config.actions_sources)
    if not sources:
        logger.warning("actions_autogenerate is True but actions_sources is empty")
        return

    confdir = Path(app.confdir)
    srcdir = Path(app.srcdir)

    for source in sources:
        yaml_path = Path(source["yaml_path"])
        if not yaml_path.is_absolute():
            yaml_path = confdir / yaml_path

        output_rel = source["output_path"] + ext
        output_path = srcdir / output_rel

        try:
            actions_data = load_actions(yaml_path)
        except FileNotFoundError:
            logger.warning("actions.yaml not found at %s; skipping", yaml_path)
            continue
        except ActionsValidationError as exc:
            logger.warning("Validation failed for %s: %s", yaml_path, exc)
            continue

        rendered = template.render(actions=actions_data)

        # Only write if content changed to avoid unnecessary rebuilds
        if output_path.exists():
            existing = output_path.read_text(encoding="utf-8")
            if existing == rendered:
                logger.debug("No changes for %s; skipping write", output_rel)
                continue

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
        logger.info("Generated %s from %s", output_rel, yaml_path)
