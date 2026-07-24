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

"""Load and validate Juju charm actions.yaml files."""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml


class ActionsValidationError(Exception):
    """Raised when actions.yaml fails structural validation."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("\n".join(errors))


def validate_actions(
    actions_data: object,
    source_path: str | Path = "<unknown>",
) -> list[str]:
    """Validate the structure of actions.yaml data.

    Returns a list of error strings. An empty list means valid.
    """
    errors: list[str] = []

    if not isinstance(actions_data, dict):
        errors.append(
            f"{source_path}: top-level structure must be a mapping, "
            f"got {type(actions_data).__name__}"
        )
        return errors

    typed_actions = cast("dict[str, Any]", actions_data)
    for action_name, details in typed_actions.items():
        if not isinstance(details, dict):
            errors.append(
                f"Action '{action_name}': value must be a mapping, "
                f"got {type(details).__name__}"
            )
            continue

        typed_details = cast("dict[str, Any]", details)
        if "description" not in typed_details:
            errors.append(
                f"Action '{action_name}': missing required 'description' field"
            )
        elif not isinstance(typed_details["description"], str):
            errors.append(
                f"Action '{action_name}': 'description' must be a string, "
                f"got {type(typed_details['description']).__name__}"
            )

        if "params" in typed_details:
            if not isinstance(typed_details["params"], dict):
                errors.append(
                    f"Action '{action_name}': 'params' must be a mapping, "
                    f"got {type(typed_details['params']).__name__}"
                )
            else:
                typed_params = cast("dict[str, Any]", typed_details["params"])
                for param_name, param_details in typed_params.items():
                    if not isinstance(param_details, dict):
                        errors.append(
                            f"Action '{action_name}', param '{param_name}': "
                            f"value must be a mapping, "
                            f"got {type(param_details).__name__}"
                        )

    return errors


def load_actions(yaml_path: str | Path) -> dict[str, Any]:
    """Load and validate an actions.yaml file.

    Returns the parsed actions dict.
    Raises FileNotFoundError if the file does not exist.
    Raises ActionsValidationError if validation fails.
    """
    yaml_path = Path(yaml_path)

    if not yaml_path.exists():
        raise FileNotFoundError(f"Could not find {yaml_path}")

    with yaml_path.open(encoding="utf-8") as f:
        actions_data: dict[str, Any] = yaml.safe_load(f)

    errors = validate_actions(actions_data, yaml_path)
    if errors:
        raise ActionsValidationError(errors)

    return actions_data
