"""Load and validate Juju charm actions.yaml files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class ActionsValidationError(Exception):
    """Raised when actions.yaml fails structural validation."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("\n".join(errors))


def validate_actions(actions_data: Any, source_path: str | Path = "<unknown>") -> list[str]:
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

    for action_name, details in actions_data.items():
        if not isinstance(details, dict):
            errors.append(
                f"Action '{action_name}': value must be a mapping, "
                f"got {type(details).__name__}"
            )
            continue

        if "description" not in details:
            errors.append(
                f"Action '{action_name}': missing required 'description' field"
            )
        elif not isinstance(details["description"], str):
            errors.append(
                f"Action '{action_name}': 'description' must be a string, "
                f"got {type(details['description']).__name__}"
            )

        if "params" in details:
            if not isinstance(details["params"], dict):
                errors.append(
                    f"Action '{action_name}': 'params' must be a mapping, "
                    f"got {type(details['params']).__name__}"
                )
            else:
                for param_name, param_details in details["params"].items():
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

    with open(yaml_path, "r", encoding="utf-8") as f:
        actions_data = yaml.safe_load(f)

    errors = validate_actions(actions_data, yaml_path)
    if errors:
        raise ActionsValidationError(errors)

    return actions_data
