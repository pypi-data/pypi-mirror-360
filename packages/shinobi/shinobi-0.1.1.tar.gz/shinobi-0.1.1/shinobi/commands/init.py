"""Implementation of the init command."""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import typer
from rich.prompt import Confirm

from shinobi.core.utils import console, run_command
from shinobi.templates import TEMPLATES_DIR


def setup_ruff(project_path: Path) -> None:
    """Set up Ruff configuration and pre-commit hook.

    Args:
        project_path: Path to the project directory
    """
    # Copy pre-commit-config.yaml
    pre_commit_source = TEMPLATES_DIR / "project" / "pre-commit-config.yaml"
    pre_commit_dest = project_path / ".pre-commit-config.yaml"
    shutil.copy(pre_commit_source, pre_commit_dest)

    # Update pyproject.toml to include pre-commit and ruff in dev dependencies
    pyproject_path = project_path / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text()

        # Check if dev dependencies section exists
        if "[dependency-groups]" not in content:
            # Add dev dependencies section with pre-commit and ruff
            dev_section = """
[dependency-groups]
dev = [
    "pre-commit>=3.0.0",
    "ruff>=0.3.0",
]
"""
            # Find the right spot to insert it (after [project] section)
            if "[build-system]" in content:
                content = content.replace(
                    "[build-system]", dev_section + "\n[build-system]"
                )
            else:
                content += dev_section

        # Check if pre-commit and ruff are already in dev dependencies
        elif "pre-commit" not in content or "ruff" not in content:
            # Insert pre-commit and ruff into existing dev dependencies
            import re

            dev_pattern = r"(\[dependency-groups\]\s*\ndev\s*=\s*\[(?:[^\]]*\n)?)(\])"
            if "pre-commit" not in content:
                content = re.sub(
                    dev_pattern, r'\1    "pre-commit>=3.0.0",\n\2', content
                )
            if "ruff" not in content:
                content = re.sub(dev_pattern, r'\1    "ruff>=0.3.0",\n\2', content)

        # Add Ruff configuration at the end of the file
        ruff_config = """
[tool.ruff]
line-length = 88
target-version = "py312"
fix = true

[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = ["E501"]  # Example: ignore line length

[tool.ruff.format]
quote-style = "double"
"""
        content += ruff_config

        pyproject_path.write_text(content)

    console.print(
        "[yellow]Added pre-commit and ruff to dev dependencies. To install them, run:[/yellow]"
    )
    console.print(
        f"[green]cd {project_path} && uv pip install -e '.[dev]' && pre-commit install[/green]"
    )


def setup_github_workflows(project_path: Path) -> None:
    """Set up GitHub Actions workflows for linting and testing.

    Args:
        project_path: Path to the project directory
    """
    workflows_dir = project_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    # Copy lint workflow
    lint_source = TEMPLATES_DIR / "ci" / "github_workflows" / "lint.yml"
    lint_dest = workflows_dir / "lint.yml"
    shutil.copy(lint_source, lint_dest)

    # Copy test workflow
    test_source = TEMPLATES_DIR / "ci" / "github_workflows" / "test.yml"
    test_dest = workflows_dir / "test.yml"
    shutil.copy(test_source, test_dest)


def create_vscode_settings(project_path: Path) -> None:
    """Create VS Code settings.json file.

    Args:
        project_path: Path to the project directory
    """
    vscode_dir = project_path / ".vscode"
    vscode_dir.mkdir(exist_ok=True)

    # Copy settings.json
    settings_source = TEMPLATES_DIR / "ide" / "vscode" / "settings.json"
    settings_dest = vscode_dir / "settings.json"
    shutil.copy(settings_source, settings_dest)

    # Copy extensions.json
    extensions_source = TEMPLATES_DIR / "ide" / "vscode" / "extensions.json"
    extensions_dest = vscode_dir / "extensions.json"
    shutil.copy(extensions_source, extensions_dest)


def create_cursor_rules(project_path: Path) -> None:
    """Create Cursor rules file.

    Args:
        project_path: Path to the project directory
    """
    cursor_dir = project_path / ".cursor" / "rules"
    cursor_dir.mkdir(parents=True, exist_ok=True)

    # Copy cursor rules from template
    rules_source = TEMPLATES_DIR / "ide" / "cursor" / "rules" / "use-uv-always.mdc"
    rules_dest = cursor_dir / "use-uv-always.mdc"
    shutil.copy(rules_source, rules_dest)


def create_readme(project_path: Path, config: dict) -> None:
    """Create a comprehensive README.md file for the project.

    Args:
        project_path: Path to the project directory
        config: Project configuration
    """
    # Generate badges
    badges = []

    # Add GitHub-specific badges if owner and repo are provided
    github_owner = config.get("github_owner")
    github_repo = config.get("github_repo")

    if github_owner and github_repo:
        badges.append(
            f"[![Unit Tests](https://github.com/{github_owner}/{github_repo}/actions/workflows/test.yml/badge.svg)](https://github.com/{github_owner}/{github_repo}/actions/workflows/test.yml)"
        )

    # Always include these badges
    badges.append(
        "[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)"
    )
    badges.append(
        "[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)"
    )

    badges_section = "\n".join(badges)

    # Read template and substitute variables
    readme_template_path = TEMPLATES_DIR / "docs" / "README.md.template"
    with open(readme_template_path, "r") as f:
        readme_template = f.read()

    # Set default values
    github_url = (
        config.get("github_url")
        or f"https://github.com/yourusername/{config['project_name']}.git"
    )
    description = (
        config.get("description") or "A Python project initialized with Shinobi."
    )

    # Render the template using simple string replacement
    readme_content = readme_template
    readme_content = readme_content.replace("{project_name}", config["project_name"])
    readme_content = readme_content.replace("{description}", description)
    readme_content = readme_content.replace("{badges}", badges_section)
    readme_content = readme_content.replace("{github_url}", github_url)

    # Write the output
    readme_dest = project_path / "README.md"
    readme_dest.write_text(readme_content)


def create_license(project_path: Path) -> None:
    """Create an MIT license file for the project.

    Args:
        project_path: Path to the project directory
    """
    current_year = datetime.now().year

    # Read template and substitute variables
    license_template_path = TEMPLATES_DIR / "license" / "mit.template"
    with open(license_template_path, "r") as f:
        license_template = f.read()

    # Render the template using simple string replacement
    license_content = license_template.replace("{year}", str(current_year))

    # Write the output
    license_dest = project_path / "LICENSE"
    license_dest.write_text(license_content)


def update_pyproject_description(pyproject_path: Path, description: str) -> None:
    """Update the project description in pyproject.toml.

    Args:
        pyproject_path: Path to the pyproject.toml file
        description: Project description
    """
    if not description:
        return

    if pyproject_path.exists():
        content = pyproject_path.read_text()

        # Escape quotes and handle multiline descriptions
        escaped_description = description.replace('"', '\\"').replace("\n", "\\n")

        # Try to replace empty description first
        if 'description = ""' in content:
            content = content.replace(
                'description = ""', f'description = "{escaped_description}"'
            )
        # If no empty description, try to replace existing one
        elif 'description = "' in content:
            import re

            content = re.sub(
                r'description = "[^"]*"',
                f'description = "{escaped_description}"',
                content,
            )
        # If no description field exists, add it after the name field
        else:
            content = content.replace(
                'name = "', f'name = "\ndescription = "{escaped_description}"'
            )

        pyproject_path.write_text(content)


def create_gitignore(project_path: Path) -> None:
    """Create a comprehensive .gitignore file for Python projects.

    Args:
        project_path: Path to the project directory
    """
    # Copy gitignore template
    gitignore_source = TEMPLATES_DIR / "gitignore.template"
    gitignore_dest = project_path / ".gitignore"
    shutil.copy(gitignore_source, gitignore_dest)


def create_pyproject_toml(project_path: Path, config: Dict[str, Any]) -> None:
    """Create a pyproject.toml file for the project.

    Args:
        project_path: Path to the project directory
        config: Project configuration
    """
    # Check if we should create a new pyproject.toml or update the existing one
    pyproject_path = project_path / "pyproject.toml"

    if not pyproject_path.exists():
        # Read template and substitute variables
        pyproject_template_path = TEMPLATES_DIR / "project" / "pyproject.toml.template"
        with open(pyproject_template_path, "r") as f:
            pyproject_template = f.read()

        # Set default values
        description = config.get("description") or ""
        python_version = config.get("python_version") or "3.13"
        python_version_nodot = python_version.replace(".", "")

        # Render the template using simple string replacement
        pyproject_content = pyproject_template
        pyproject_content = pyproject_content.replace(
            "{project_name}", config["project_name"]
        )
        pyproject_content = pyproject_content.replace("{description}", description)
        pyproject_content = pyproject_content.replace(
            "{python_version}", python_version
        )
        pyproject_content = pyproject_content.replace(
            "{python_version_nodot}", python_version_nodot
        )

        # Write the output
        pyproject_path.write_text(pyproject_content)
    else:
        # Update existing pyproject.toml
        update_pyproject_description(pyproject_path, config.get("description", ""))


def initialize_project(config: Dict[str, Any]) -> None:
    """Initialize a new Python project with enhanced features.

    Args:
        config: Project configuration
    """
    project_path = Path(config["project_name"])

    if project_path.exists():
        if not Confirm.ask(
            f"Directory {config['project_name']} already exists. Continue?"
        ):
            raise typer.Exit()

    # Run uv init
    console.print("\n[yellow]Running uv init...[/yellow]")
    run_command(["uv", "init", config["project_name"]])

    # Move hello.py to main.py if it exists
    hello_py = project_path / "hello.py"
    if hello_py.exists():
        hello_py.rename(project_path / "main.py")

    # Create src directory and move main.py into it
    src_dir = project_path / "src"
    src_dir.mkdir(exist_ok=True)
    main_py = project_path / "main.py"
    if main_py.exists():
        main_py.rename(src_dir / "main.py")

    # Create tests directory
    tests_dir = project_path / "tests"
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / "__init__.py").touch()

    # Create .gitignore
    create_gitignore(project_path)

    # Set up features based on selection
    if "precommit" in config["features"]:
        console.print("[yellow]Setting up Ruff and pre-commit hooks...[/yellow]")
        setup_ruff(project_path)

    if "github" in config["features"]:
        console.print("[yellow]Setting up GitHub workflows...[/yellow]")
        setup_github_workflows(project_path)

    # Always set up pytest
    console.print("[yellow]Setting up pytest...[/yellow]")

    # Add pytest to dev dependencies in pyproject.toml if not already present
    pyproject_path = project_path / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text()

        # Check if dev dependencies section exists
        if "[dependency-groups]" not in content:
            # Add dev dependencies section with pytest
            dev_section = """
[dependency-groups]
dev = [
    "pytest>=7.0.0",
]
"""
            # Find the right spot to insert it (after [project] section)
            if "[build-system]" in content:
                content = content.replace(
                    "[build-system]", dev_section + "\n[build-system]"
                )
            else:
                content += dev_section

        # Check if pytest is already in dev dependencies
        elif "pytest" not in content:
            # Insert pytest into existing dev dependencies
            import re

            dev_pattern = r"(\[dependency-groups\]\s*\ndev\s*=\s*\[(?:[^\]]*\n)?)(\])"
            content = re.sub(dev_pattern, r'\1    "pytest>=7.0.0",\n\2', content)

        # Add pytest configuration if not already present
        if "[tool.pytest.ini_options]" not in content:
            pytest_config = """
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
python_files = ["test_*.py"]
"""
            content += pytest_config

        pyproject_path.write_text(content)

    # Create a basic test file
    test_file = tests_dir / "test_main.py"
    test_file.write_text('''def test_example():
    """Example test."""
    assert True
''')

    # Update pyproject.toml with project description
    update_pyproject_description(project_path / "pyproject.toml", config["description"])

    # Create a comprehensive README.md
    create_readme(project_path, config)

    # Create LICENSE file
    create_license(project_path)

    # Set up IDE configuration
    if config["ide"] == "VS Code":
        create_vscode_settings(project_path)
    elif config["ide"] == "Cursor":
        create_vscode_settings(project_path)  # Cursor also uses VS Code settings
        create_cursor_rules(project_path)

    console.print("\n[green]Project initialized successfully![/green]")
    console.print("\nNext steps:")
    console.print(f"1. cd {config['project_name']}")
    console.print("2. Install dependencies: uv pip install -e '.[dev]'")
    if "precommit" in config["features"]:
        console.print("3. Set up pre-commit: pre-commit install")
    if "github" in config["features"]:
        console.print(
            "4. Initialize git repository: git init && git add . && git commit -m 'Initial commit'"
        )
