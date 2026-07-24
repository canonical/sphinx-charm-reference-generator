"""Sphinx directive that renders actions.yaml as docutils nodes."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.util.docutils import SphinxDirective

from .parser import ActionsValidationError, load_actions


class ActionsReferenceDirective(SphinxDirective):
    """Directive to embed Juju charm action documentation inline.

    Usage (reST)::

        .. actions-reference::

    Usage (MyST)::

        ```{actions-reference}
        ```

    Options:
        :action-sources: Path to the actions.yaml file, relative to the Sphinx
            source directory. Defaults to ``../actions.yaml``.
    """

    has_content = False
    optional_arguments = 0
    option_spec: ClassVar[dict[str, Any]] = {
        "action-sources": directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        yaml_path = self._resolve_yaml_path()

        try:
            actions_data = load_actions(yaml_path)
        except FileNotFoundError:
            return [self._error(f"actions.yaml not found at {yaml_path}")]
        except ActionsValidationError as exc:
            return [self._error(f"Validation failed:\n{exc}")]

        return self._build_nodes(actions_data)

    def _resolve_yaml_path(self) -> Path:
        """Determine which actions.yaml to read."""
        raw = self.options.get("action-sources", "../actions.yaml")
        path = Path(raw)
        if not path.is_absolute():
            path = Path(self.env.srcdir) / path
        return path

    def _error(self, message: str) -> nodes.system_message:
        """Return a Sphinx error node."""
        return self.state_machine.reporter.error(
            message,
            nodes.literal_block(message, message),
            line=self.lineno,
        )

    def _build_nodes(self, actions_data: dict[str, Any]) -> list[nodes.Node]:
        """Convert parsed actions data into docutils nodes."""
        result_nodes: list[nodes.Node] = []

        for action_name, details in actions_data.items():
            section = nodes.section(ids=[f"action-{action_name}"])
            section += nodes.title(text=action_name)

            description = details.get("description", "").strip()
            if description:
                section += nodes.paragraph(text=description)

            params = details.get("params")
            if params and isinstance(params, dict):
                section += nodes.paragraph(text="Parameters:")
                section += self._build_params_table(params)

            result_nodes.append(section)

        return result_nodes

    def _build_params_table(self, params: dict[str, Any]) -> nodes.table:
        """Build a docutils table node for action parameters."""
        table = nodes.table()
        tgroup = nodes.tgroup(cols=3)
        table += tgroup

        for width in (20, 15, 65):
            tgroup += nodes.colspec(colwidth=width)

        # Header row
        thead = nodes.thead()
        tgroup += thead
        header_row = nodes.row()
        for header_text in ("Name", "Type", "Description"):
            entry = nodes.entry()
            entry += nodes.paragraph(text=header_text)
            header_row += entry
        thead += header_row

        # Data rows
        tbody = nodes.tbody()
        tgroup += tbody
        for param_name, param_details in params.items():
            if not isinstance(param_details, dict):
                continue
            row = nodes.row()

            name_entry = nodes.entry()
            name_entry += nodes.literal(text=param_name)
            row += name_entry

            type_entry = nodes.entry()
            type_entry += nodes.paragraph(
                text=str(param_details.get("type", "string"))
            )
            row += type_entry

            desc_entry = nodes.entry()
            desc_text = str(param_details.get("description", "-")).replace("\n", " ").strip()
            desc_entry += nodes.paragraph(text=desc_text)
            row += desc_entry

            tbody += row

        return table

