"""Tests for the auto-generation module."""

from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from sphinx_actions_ref.generator import generate_actions_pages

SAMPLE_ACTIONS_YAML = textwrap.dedent("""\
    pause:
      description: Pause the application.
      params:
        force:
          type: boolean
          description: Force pause even if active connections exist.
    resume:
      description: Resume the application after a pause.
    backup:
      description: Create a backup of the current state.
      params:
        target:
          type: string
          description: Target path for the backup file.
        compress:
          type: boolean
          description: Whether to compress the backup.
""")

SAMPLE_ACTIONS_YAML_MINIMAL = textwrap.dedent("""\
    check-health:
      description: Run a health check on the unit.
""")


def _make_app(
    tmp_path: Path,
    *,
    sources: str | list[dict[str, str]] = "actions.yaml",
    output_format: str = "myst",
    autogenerate: bool = True,
) -> MagicMock:
    """Create a mock Sphinx app with the given config."""
    confdir = tmp_path / "conf"
    srcdir = tmp_path / "src"
    confdir.mkdir(exist_ok=True)
    srcdir.mkdir(exist_ok=True)

    app = MagicMock()
    app.confdir = str(confdir)
    app.srcdir = str(srcdir)
    app.config.actions_sources = sources
    app.config.actions_output_format = output_format
    app.config.actions_autogenerate = autogenerate
    return app


class TestGenerateActionsPages:
    """Tests for the builder-inited handler."""

    def test_skip_when_disabled(self, tmp_path: Path) -> None:
        app = _make_app(tmp_path, autogenerate=False)
        generate_actions_pages(app)
        srcdir = Path(app.srcdir)
        assert not list(srcdir.rglob("*.md"))
        assert not list(srcdir.rglob("*.rst"))

    def test_single_source_string_myst(self, tmp_path: Path) -> None:
        app = _make_app(tmp_path, sources="actions.yaml", output_format="myst")
        confdir = Path(app.confdir)
        (confdir / "actions.yaml").write_text(SAMPLE_ACTIONS_YAML, encoding="utf-8")

        generate_actions_pages(app)

        output = Path(app.srcdir) / "reference" / "actions.md"
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "pause" in content
        assert "resume" in content

    def test_single_source_string_rst(self, tmp_path: Path) -> None:
        app = _make_app(tmp_path, sources="actions.yaml", output_format="rst")
        confdir = Path(app.confdir)
        (confdir / "actions.yaml").write_text(SAMPLE_ACTIONS_YAML, encoding="utf-8")

        generate_actions_pages(app)

        output = Path(app.srcdir) / "reference" / "actions.rst"
        assert output.exists()
        content = output.read_text(encoding="utf-8")
        assert "pause" in content
        assert ".. list-table::" in content

    def test_multiple_sources(self, tmp_path: Path) -> None:
        sources = [
            {"yaml_path": "charms/foo/actions.yaml", "output_path": "reference/foo-actions"},
            {"yaml_path": "charms/bar/actions.yaml", "output_path": "reference/bar-actions"},
        ]
        app = _make_app(tmp_path, sources=sources, output_format="myst")
        confdir = Path(app.confdir)

        foo_dir = confdir / "charms" / "foo"
        foo_dir.mkdir(parents=True)
        (foo_dir / "actions.yaml").write_text(SAMPLE_ACTIONS_YAML, encoding="utf-8")

        bar_dir = confdir / "charms" / "bar"
        bar_dir.mkdir(parents=True)
        (bar_dir / "actions.yaml").write_text(SAMPLE_ACTIONS_YAML_MINIMAL, encoding="utf-8")

        generate_actions_pages(app)

        srcdir = Path(app.srcdir)
        foo_out = srcdir / "reference" / "foo-actions.md"
        bar_out = srcdir / "reference" / "bar-actions.md"
        assert foo_out.exists()
        assert bar_out.exists()
        assert "pause" in foo_out.read_text(encoding="utf-8")
        assert "check-health" in bar_out.read_text(encoding="utf-8")

    def test_no_overwrite_when_unchanged(self, tmp_path: Path) -> None:
        app = _make_app(tmp_path, sources="actions.yaml", output_format="myst")
        confdir = Path(app.confdir)
        (confdir / "actions.yaml").write_text(SAMPLE_ACTIONS_YAML, encoding="utf-8")

        generate_actions_pages(app)
        output = Path(app.srcdir) / "reference" / "actions.md"
        mtime_first = output.stat().st_mtime_ns

        # Run again — file should not be rewritten
        generate_actions_pages(app)
        mtime_second = output.stat().st_mtime_ns
        assert mtime_first == mtime_second

    def test_missing_yaml_skips(self, tmp_path: Path) -> None:
        app = _make_app(tmp_path, sources="nonexistent.yaml")
        generate_actions_pages(app)
        srcdir = Path(app.srcdir)
        assert not list(srcdir.rglob("*.md"))

    def test_invalid_format_skips(self, tmp_path: Path) -> None:
        app = _make_app(tmp_path, sources="actions.yaml", output_format="html")
        generate_actions_pages(app)
        srcdir = Path(app.srcdir)
        assert not list(srcdir.rglob("*"))
