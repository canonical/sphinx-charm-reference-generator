"""Tests for the parser module."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest
import yaml

from sphinx_actions_ref.parser import (
    ActionsValidationError,
    load_actions,
    validate_actions,
)


class TestValidateActions:
    """Unit tests for validate_actions()."""

    def test_valid_actions(self) -> None:
        data = {
            "pause": {
                "description": "Pause the app.",
                "params": {
                    "force": {"type": "boolean", "description": "Force it."},
                },
            },
            "resume": {"description": "Resume the app."},
        }
        assert validate_actions(data) == []

    def test_top_level_not_dict(self) -> None:
        errors = validate_actions(["not", "a", "dict"])
        assert len(errors) == 1
        assert "top-level structure must be a mapping" in errors[0]

    def test_action_value_not_dict(self) -> None:
        errors = validate_actions({"bad_action": "just a string"})
        assert len(errors) == 1
        assert "value must be a mapping" in errors[0]

    def test_missing_description(self) -> None:
        errors = validate_actions({"myaction": {"params": {}}})
        assert len(errors) == 1
        assert "missing required 'description' field" in errors[0]

    def test_description_not_string(self) -> None:
        errors = validate_actions({"myaction": {"description": 123}})
        assert len(errors) == 1
        assert "'description' must be a string" in errors[0]

    def test_params_not_dict(self) -> None:
        errors = validate_actions(
            {"myaction": {"description": "ok", "params": "bad"}}
        )
        assert len(errors) == 1
        assert "'params' must be a mapping" in errors[0]

    def test_param_value_not_dict(self) -> None:
        errors = validate_actions(
            {"myaction": {"description": "ok", "params": {"p": "bad"}}}
        )
        assert len(errors) == 1
        assert "param 'p'" in errors[0]

    def test_multiple_errors(self) -> None:
        data = {
            "a1": "not a dict",
            "a2": {"params": {}},
        }
        errors = validate_actions(data)
        assert len(errors) == 2


class TestLoadActions:
    """Unit tests for load_actions()."""

    def test_load_valid(self, actions_yaml_path: Path) -> None:
        data = load_actions(actions_yaml_path)
        assert "pause" in data
        assert "resume" in data

    def test_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_actions(tmp_path / "nonexistent.yaml")

    def test_validation_error(self, tmp_path: Path) -> None:
        bad = tmp_path / "bad.yaml"
        bad.write_text("- not\n- a\n- dict\n", encoding="utf-8")
        with pytest.raises(ActionsValidationError) as exc_info:
            load_actions(bad)
        assert len(exc_info.value.errors) == 1
