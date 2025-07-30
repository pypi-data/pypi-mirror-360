"""Test cases for the shinobi CLI."""

import pytest
from typer.testing import CliRunner

from shinobi.cli import app


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


def test_cli_help(runner):
    """Test that the CLI shows help text."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Shinobi - Enhanced Python project initialization tool" in result.stdout
    assert "init" in result.stdout


def test_cli_init_help(runner):
    """Test that the init command shows help text."""
    result = runner.invoke(app, ["init", "--help"])
    assert result.exit_code == 0
    assert "Initialize a new Python project" in result.stdout
