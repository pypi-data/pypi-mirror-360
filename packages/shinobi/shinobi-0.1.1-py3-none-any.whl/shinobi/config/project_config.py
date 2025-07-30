"""Project configuration utilities."""

from typing import Optional

import questionary

from shinobi.core.utils import console
from shinobi.validation.validators import validate_project_name


def get_project_config() -> Optional[dict]:
    """Get project configuration through interactive prompts.

    Returns:
        A dictionary with project configuration or None if cancelled
    """
    console.print(
        "\n[bold blue]Welcome to Shinobi! Let's set up your project.[/bold blue]\n"
    )

    try:
        # Get project name with validation
        while True:
            project_name = questionary.text(
                "What's the name of your project?",
                validate=lambda text: len(text) > 0,
            ).ask()

            if project_name is None:  # User pressed Ctrl+C
                return None

            is_valid, error_msg = validate_project_name(project_name)
            if is_valid:
                break

            console.print(f"[red]Invalid project name: {error_msg}[/red]")
            console.print("[yellow]Project names must:[/yellow]")
            console.print("- Start and end with a letter or digit")
            console.print("- May only contain letters, digits, '-', '_', and '.'")
            console.print("Please try again.\n")

        # Get project description
        description = questionary.text(
            "What's the description of your project?",
            default="",
        ).ask()

        if description is None:  # User pressed Ctrl+C
            return None

        # Get GitHub repository details
        github_owner = questionary.text(
            "What's your GitHub username or organization name? (leave empty if not using GitHub)",
            default="",
        ).ask()

        if github_owner is None:  # User pressed Ctrl+C
            return None

        github_repo = ""
        github_url = ""
        if github_owner:
            github_repo = questionary.text(
                "What's your GitHub repository name?",
                default=project_name,
            ).ask()

            if github_repo is None:  # User pressed Ctrl+C
                return None

            github_url = f"https://github.com/{github_owner}/{github_repo}"

        # Get Python version
        python_version = questionary.select(
            "Which Python version would you like to use?",
            choices=["3.13", "3.12", "3.11"],
            default="3.13",
        ).ask()

        if python_version is None:  # User pressed Ctrl+C
            return None

        # Get IDE preference
        ide = questionary.select(
            "Which IDE are you using?",
            choices=["Cursor", "VS Code", "Other"],
            default="VS Code",
        ).ask()

        if ide is None:  # User pressed Ctrl+C
            return None

        # Get additional features
        features = questionary.checkbox(
            "Select additional features to include:",
            choices=[
                {
                    "name": "GitHub Actions",
                    "value": "github",
                    "checked": True,
                    "description": "Set up GitHub Actions workflows for linting and testing",
                },
                {
                    "name": "Pre-commit hooks",
                    "value": "precommit",
                    "checked": True,
                    "description": "Set up pre-commit hooks for Ruff",
                },
            ],
        ).ask()

        if features is None:  # User pressed Ctrl+C
            return None

        # Create python_version without dots for use in template
        python_version_nodot = python_version.replace(".", "")

        return {
            "project_name": project_name,
            "description": description,
            "python_version": python_version,
            "python_version_nodot": python_version_nodot,
            "ide": ide,
            "features": features,
            "github_url": github_url,
            "github_owner": github_owner,
            "github_repo": github_repo,
        }
    except KeyboardInterrupt:
        return None
