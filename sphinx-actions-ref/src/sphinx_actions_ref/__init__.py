"""Sphinx extension to render Juju charm actions.yaml inline."""

from __future__ import annotations

from typing import Any

from sphinx.application import Sphinx

__version__ = "0.1.0"


def setup(app: Sphinx) -> dict[str, Any]:
    """Register the extension with Sphinx."""
    from .directive import ActionsReferenceDirective

    # Config values
    app.add_config_value("actions_sources", default="actions.yaml", rebuild="env")
    app.add_config_value("actions_confdir", default=str(app.confdir), rebuild="env")

    # Directive
    app.add_directive("actions-reference", ActionsReferenceDirective)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
