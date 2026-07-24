"""Integration tests for the actions-reference directive and full Sphinx builds."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
from sphinx.application import Sphinx

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


def _build_sphinx(
    tmp_path: Path,
    *,
    conf_extra: str = "",
    index_content: str = "",
    use_myst: bool = False,
    actions_yaml: str = SAMPLE_ACTIONS_YAML,
) -> Path:
    """Build a minimal Sphinx project and return the output directory."""
    srcdir = tmp_path / "src"
    outdir = tmp_path / "out"
    doctreedir = tmp_path / "doctrees"
    srcdir.mkdir()

    ext_list = '"sphinx_actions_ref"'
    if use_myst:
        ext_list += ', "myst_parser"'

    lines = [
        f'project = "Test"',
        f"extensions = [{ext_list}]",
        'exclude_patterns = ["_build"]',
    ]
    if conf_extra:
        lines.append(conf_extra)

    (srcdir / "conf.py").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (srcdir / "actions.yaml").write_text(actions_yaml, encoding="utf-8")

    ext = ".md" if use_myst else ".rst"
    (srcdir / f"index{ext}").write_text(index_content, encoding="utf-8")

    app = Sphinx(
        srcdir=str(srcdir),
        confdir=str(srcdir),
        outdir=str(outdir),
        doctreedir=str(doctreedir),
        buildername="html",
    )
    app.build()

    return outdir


class TestDirectiveRst:
    """Test the directive in reStructuredText projects."""

    def test_basic_directive(self, tmp_path: Path) -> None:
        index = textwrap.dedent("""\
            Test
            ====

            .. actions-reference::
        """)
        outdir = _build_sphinx(tmp_path, index_content=index)
        html = (outdir / "index.html").read_text(encoding="utf-8")
        assert "pause" in html
        assert "resume" in html
        assert "backup" in html

    def test_directive_renders_params_table(self, tmp_path: Path) -> None:
        index = textwrap.dedent("""\
            Test
            ====

            .. actions-reference::
        """)
        outdir = _build_sphinx(tmp_path, index_content=index)
        html = (outdir / "index.html").read_text(encoding="utf-8")
        assert "force" in html
        assert "boolean" in html
        assert "target" in html

    def test_directive_with_yaml_path_override(self, tmp_path: Path) -> None:
        index = textwrap.dedent("""\
            Test
            ====

            .. actions-reference::
               :yaml-path: custom/actions.yaml
        """)

        srcdir = tmp_path / "src"
        srcdir.mkdir(exist_ok=True)
        custom_dir = srcdir / "custom"
        custom_dir.mkdir()
        (custom_dir / "actions.yaml").write_text(
            "custom-action:\n  description: A custom action.\n",
            encoding="utf-8",
        )

        conf = textwrap.dedent("""\
            project = "Test"
            extensions = ["sphinx_actions_ref"]
            exclude_patterns = ["_build"]
        """)
        (srcdir / "conf.py").write_text(conf, encoding="utf-8")
        (srcdir / "index.rst").write_text(index, encoding="utf-8")
        (srcdir / "actions.yaml").write_text(SAMPLE_ACTIONS_YAML, encoding="utf-8")

        outdir = tmp_path / "out"
        doctreedir = tmp_path / "doctrees"
        app = Sphinx(
            srcdir=str(srcdir),
            confdir=str(srcdir),
            outdir=str(outdir),
            doctreedir=str(doctreedir),
            buildername="html",
        )
        app.build()

        html = (outdir / "index.html").read_text(encoding="utf-8")
        assert "custom-action" in html
        assert "A custom action." in html


class TestDirectiveMyst:
    """Test the directive in MyST Markdown projects."""

    def test_basic_directive_myst(self, tmp_path: Path) -> None:
        index = textwrap.dedent("""\
            # Test

            ```{actions-reference}
            ```
        """)
        outdir = _build_sphinx(tmp_path, index_content=index, use_myst=True)
        html = (outdir / "index.html").read_text(encoding="utf-8")
        assert "pause" in html
        assert "resume" in html


class TestAutogenerationIntegration:
    """Test auto-generation with a real Sphinx build."""

    def test_autogen_creates_file_and_builds(self, tmp_path: Path) -> None:
        conf_extra = textwrap.dedent("""\
            actions_autogenerate = True
            actions_output_format = "rst"
            actions_sources = "actions.yaml"
        """)
        index = textwrap.dedent("""\
            Test
            ====

            .. toctree::

               reference/actions
        """)
        outdir = _build_sphinx(tmp_path, conf_extra=conf_extra, index_content=index)

        # The generated file should exist in the source tree
        srcdir = tmp_path / "src"
        generated = srcdir / "reference" / "actions.rst"
        assert generated.exists()

        # The HTML output should include the generated content
        html_path = outdir / "reference" / "actions.html"
        assert html_path.exists()
        html = html_path.read_text(encoding="utf-8")
        assert "pause" in html
