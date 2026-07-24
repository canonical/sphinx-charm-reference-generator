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

"""Shared fixtures for sphinx-charm-reference-generator tests."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

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


@pytest.fixture()
def actions_yaml_path(tmp_path: Path) -> Path:
    """Write a sample actions.yaml and return its path."""
    p = tmp_path / "actions.yaml"
    p.write_text(SAMPLE_ACTIONS_YAML, encoding="utf-8")
    return p


@pytest.fixture()
def actions_yaml_minimal_path(tmp_path: Path) -> Path:
    """Write a minimal actions.yaml and return its path."""
    p = tmp_path / "actions_minimal.yaml"
    p.write_text(SAMPLE_ACTIONS_YAML_MINIMAL, encoding="utf-8")
    return p
