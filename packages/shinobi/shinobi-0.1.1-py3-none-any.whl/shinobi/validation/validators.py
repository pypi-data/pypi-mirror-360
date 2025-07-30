"""Validation functions for project configuration."""

import re


def validate_project_name(name: str) -> tuple[bool, str]:
    """Validate project name according to Python package naming rules.

    Rules:
    - Must start and end with a letter or digit
    - May only contain -, _, ., and alphanumeric characters

    Args:
        name: The project name to validate

    Returns:
        A tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Project name cannot be empty"

    # Check if starts and ends with letter/digit
    if not (name[0].isalnum() and name[-1].isalnum()):
        return False, "Project name must start and end with a letter or digit"

    # Check if contains only allowed characters
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]$", name):
        return False, "Project name may only contain letters, digits, '-', '_', and '.'"

    return True, ""
