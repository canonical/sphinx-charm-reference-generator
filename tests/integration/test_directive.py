# This file is part of sphinx-charm-reference-generator.
#
# Copyright 2025 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 3, as published by the Free
# Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranties of MERCHANTABILITY, SATISFACTORY
# QUALITY, or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

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
    """Build a minimal Sphinx project and return the output directory.

    Layout mirrors a typical repo::

        tmp_path/
            actions.yaml          # at the "repo root"
            src/                  # srcdir (the docs folder)
                conf.py
                index.rst|.md

    The default :action-sources: (``../actions.yaml``) resolves from srcdir
    up to tmp_path.
    """
    srcdir = tmp_path / "src"
    outdir = tmp_path / "out"
    doctreedir = tmp_path / "doctrees"
    srcdir.mkdir()

    ext_list = '"sphinx_charm_reference_generator"'
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
    # Place actions.yaml at the "repo root" (one level above srcdir)
    (tmp_path / "actions.yaml").write_text(actions_yaml, encoding="utf-8")

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


@pytest.mark.slow
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

    def test_directive_with_action_sources_option(self, tmp_path: Path) -> None:
        index = textwrap.dedent("""\
            Test
            ====

            .. actions-reference::
               :action-sources: custom/actions.yaml
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
            extensions = ["sphinx_charm_reference_generator"]
            exclude_patterns = ["_build"]
        """)
        (srcdir / "conf.py").write_text(conf, encoding="utf-8")
        (srcdir / "index.rst").write_text(index, encoding="utf-8")

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


@pytest.mark.slow
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
        assert "backup" in html
