"""Shinobi CLI - Enhanced project initialization tool built on top of uv."""

import typer

from shinobi.commands.init import initialize_project
from shinobi.config.project_config import get_project_config
from shinobi.core.utils import console

app = typer.Typer(
    help="Shinobi - Enhanced Python project initialization tool.",
    no_args_is_help=True,
)


@app.callback()
def callback():
    """Shinobi CLI callback."""
    pass


@app.command()
def init() -> None:
    """Initialize a new Python project with enhanced features."""
    config = get_project_config()
    if config is None:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        raise typer.Exit(0)

    initialize_project(config)


if __name__ == "__main__":
    app()
