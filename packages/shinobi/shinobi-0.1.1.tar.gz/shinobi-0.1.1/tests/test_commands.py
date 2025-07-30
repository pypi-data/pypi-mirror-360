"""Test cases for CLI commands."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from shinobi.core.utils import run_command


def test_run_command_success():
    """Test that run_command succeeds with valid command."""
    with patch("subprocess.run") as mock_run:
        run_command(["echo", "hello"])
        mock_run.assert_called_once()


def test_run_command_pip_replacement():
    """Test that pip commands are replaced with uv pip."""
    with patch("subprocess.run") as mock_run:
        run_command(["pip", "install", "package"])
        mock_run.assert_called_once_with(
            ["uv", "pip", "install", "package"], check=True, cwd=None
        )

        run_command(["python", "-m", "pip", "install", "package"])
        mock_run.assert_called_with(
            ["uv", "pip", "install", "package"], check=True, cwd=None
        )


def test_run_command_with_cwd():
    """Test run_command with custom working directory."""
    with (
        tempfile.TemporaryDirectory() as tmpdir,
        patch("subprocess.run") as mock_run,
    ):
        cwd = Path(tmpdir)
        run_command(["ls"], cwd=cwd)
        mock_run.assert_called_once_with(["ls"], check=True, cwd=cwd)
