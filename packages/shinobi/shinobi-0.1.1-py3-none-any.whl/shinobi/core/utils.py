"""Core utility functions for Shinobi."""

import subprocess
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


def run_command(command: list[str], cwd: Optional[Path] = None) -> None:
    """Run a shell command and handle errors.

    Args:
        command: The command to run as a list of strings
        cwd: The current working directory to run the command in

    Raises:
        typer.Exit: If the command fails
    """
    # Replace pip commands with uv pip to ensure we use uv
    if command[0] == "pip":
        command = ["uv", "pip"] + command[1:]
    elif command[0] == "python" and command[1] == "-m" and command[2] == "pip":
        command = ["uv", "pip"] + command[3:]

    try:
        subprocess.run(command, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running command: {' '.join(command)}[/red]")
        import typer

        raise typer.Exit(1) from e
