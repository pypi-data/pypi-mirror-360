"""Test cases for project validation."""

import pytest

from shinobi.validation.validators import validate_project_name


@pytest.mark.parametrize(
    "name,is_valid,error_msg",
    [
        ("valid-name", True, ""),
        ("valid_name", True, ""),
        ("valid.name", True, ""),
        ("valid123", True, ""),
        ("123valid", True, ""),
        ("", False, "Project name cannot be empty"),
        ("-invalid", False, "Project name must start and end with a letter or digit"),
        ("invalid-", False, "Project name must start and end with a letter or digit"),
        (
            "invalid@name",
            False,
            "Project name may only contain letters, digits, '-', '_', and '.'",
        ),
        (
            "invalid name",
            False,
            "Project name may only contain letters, digits, '-', '_', and '.'",
        ),
    ],
)
def test_validate_project_name(name: str, is_valid: bool, error_msg: str):
    """Test project name validation with various inputs."""
    result_is_valid, result_error = validate_project_name(name)
    assert result_is_valid == is_valid
    assert result_error == error_msg
