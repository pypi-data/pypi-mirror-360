"""Test cases for project configuration."""

from unittest.mock import MagicMock, patch

import pytest

from shinobi.config.project_config import get_project_config


@pytest.fixture
def mock_questionary_fixture():
    """Mocks questionary and its methods with unique MagicMock instances for .ask()."""
    with patch("shinobi.config.project_config.questionary") as mock_q_module:
        # Each call to text, select, checkbox returns a new mock object (mock_text_prompt, etc.)
        # This new mock object then has its 'ask' method mocked.
        mock_text_prompt = MagicMock()
        mock_q_module.text.return_value = mock_text_prompt

        mock_select_prompt = MagicMock()
        mock_q_module.select.return_value = mock_select_prompt

        mock_checkbox_prompt = MagicMock()
        mock_q_module.checkbox.return_value = mock_checkbox_prompt
        yield mock_q_module


def test_get_project_config(mock_questionary_fixture):
    """Test project configuration gathering."""
    # Configure side effects for each .ask() call on the respective prompt mock
    mock_questionary_fixture.text.return_value.ask.side_effect = [
        "test-project",  # Project name
        "A test project",  # Description
        "",  # GitHub owner (optional, empty)
    ]
    mock_questionary_fixture.select.return_value.ask.side_effect = [
        "3.11",  # Python version
        "VS Code",  # IDE
    ]
    mock_questionary_fixture.checkbox.return_value.ask.return_value = [
        "precommit",
        "github",
    ]

    config = get_project_config()

    assert config["project_name"] == "test-project"
    assert config["description"] == "A test project"
    assert config["python_version"] == "3.11"
    assert config["ide"] == "VS Code"
    assert config["features"] == ["precommit", "github"]
    assert config.get("github_url") == ""
    assert config.get("github_owner") == ""
    assert config.get("github_repo") == ""

    # Verify questionary calls
    assert mock_questionary_fixture.text.call_count == 3
    assert mock_questionary_fixture.select.call_count == 2
    assert mock_questionary_fixture.checkbox.call_count == 1


def test_get_project_config_minimal(mock_questionary_fixture):
    """Test project configuration with minimal features."""
    mock_questionary_fixture.text.return_value.ask.side_effect = [
        "minimal-project",  # Project name
        "Minimal description",  # Description
        "",  # GitHub URL (optional)
        "",  # GitHub owner (optional)
        "",  # GitHub repo (optional)
    ]
    mock_questionary_fixture.select.return_value.ask.side_effect = [
        "3.10",  # Python version
        "None",  # IDE
    ]
    mock_questionary_fixture.checkbox.return_value.ask.return_value = []  # No features

    config = get_project_config()

    assert config["project_name"] == "minimal-project"
    assert config["description"] == "Minimal description"
    assert config["python_version"] == "3.10"
    assert config["ide"] == "None"
    assert config["features"] == []
    assert config.get("github_url") == ""
    assert config.get("github_owner") == ""
    assert config.get("github_repo") == ""


def test_get_project_config_cursor_ide(mock_questionary_fixture):
    """Test project configuration with Cursor IDE."""
    mock_questionary_fixture.text.return_value.ask.side_effect = [
        "cursor-project",  # Project name
        "Cursor project description",  # Description
        "",  # GitHub URL (optional)
        "",  # GitHub owner (optional)
        "",  # GitHub repo (optional)
    ]
    mock_questionary_fixture.select.return_value.ask.side_effect = [
        "3.9",  # Python version
        "Cursor",  # IDE
    ]
    mock_questionary_fixture.checkbox.return_value.ask.return_value = [
        "precommit",
    ]  # Example features

    config = get_project_config()

    assert config["project_name"] == "cursor-project"
    assert config["description"] == "Cursor project description"
    assert config["python_version"] == "3.9"
    assert config["ide"] == "Cursor"
    assert config["features"] == ["precommit"]
    assert config.get("github_url") == ""
    assert config.get("github_owner") == ""
    assert config.get("github_repo") == ""
