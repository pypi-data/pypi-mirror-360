"""Test cases for file generation functions."""

import pytest

from shinobi.commands.init import (
    create_cursor_rules,
    create_license,
    create_readme,
    create_vscode_settings,
    setup_github_workflows,
    setup_ruff,
    update_pyproject_description,
)


@pytest.fixture
def project_path(tmp_path):
    """Create a temporary project directory."""
    return tmp_path / "test-project"


def test_create_readme(project_path):
    """Test README generation."""
    project_path.mkdir(parents=True, exist_ok=True)
    config = {
        "project_name": "test-project",
        "description": "A test project",
        "github_owner": "testuser",
        "github_repo": "test-project",
    }
    create_readme(project_path, config)

    readme_path = project_path / "README.md"
    assert readme_path.exists()
    content = readme_path.read_text()
    assert "test-project" in content
    assert "A test project" in content
    assert "## Features" in content
    assert "## Installation" in content
    # Check for badges
    assert "[![Unit Tests]" in content
    assert "[![Ruff]" in content
    assert "[![License: MIT]" in content
    # Check for GitHub-specific content
    assert "https://github.com/testuser/test-project" in content


def test_create_license(project_path):
    """Test license file generation."""
    project_path.mkdir(parents=True, exist_ok=True)
    create_license(project_path)

    license_path = project_path / "LICENSE"
    assert license_path.exists()
    content = license_path.read_text()
    assert "MIT License" in content
    assert "Copyright" in content


def test_create_vscode_settings(project_path):
    """Test VS Code settings.json generation."""
    project_path.mkdir(parents=True, exist_ok=True)
    create_vscode_settings(project_path)

    settings_path = project_path / ".vscode" / "settings.json"
    assert settings_path.exists()
    content = settings_path.read_text()
    assert '"editor.formatOnSave"' in content
    assert '"charliermarsh.ruff"' in content
    assert '"editor.codeActionsOnSave"' in content
    assert '"source.fixAll"' in content
    assert '"source.organizeImports"' in content


def test_create_vscode_extensions(project_path):
    """Test VS Code extensions.json generation."""
    project_path.mkdir(parents=True, exist_ok=True)
    create_vscode_settings(project_path)

    extensions_path = project_path / ".vscode" / "extensions.json"
    assert extensions_path.exists()
    content = extensions_path.read_text().strip()  # Remove trailing whitespace

    # Check JSON structure
    assert content.startswith("{")
    assert content.endswith("}")
    assert '"recommendations"' in content

    # Check all required extensions are present
    required_extensions = [
        "ms-python.python",
        "charliermarsh.ruff",
        "ms-python.mypy-type-checker",
        "ms-toolsai.jupyter",
    ]
    for extension in required_extensions:
        assert f'"{extension}"' in content

    # Verify the extensions are in an array
    assert content.count("[") == 1  # One opening bracket for the array
    assert content.count("]") == 1  # One closing bracket for the array


def test_create_cursor_rules(project_path):
    """Test Cursor rules generation."""
    create_cursor_rules(project_path)

    rules_path = project_path / ".cursor" / "rules" / "use-uv-always.mdc"
    assert rules_path.exists()
    content = rules_path.read_text()
    assert "Always Use UV for Python" in content
    assert "Package Management" in content


def test_setup_github_workflows(project_path):
    """Test GitHub workflows setup."""
    setup_github_workflows(project_path)

    # Check lint workflow
    lint_path = project_path / ".github" / "workflows" / "lint.yml"
    assert lint_path.exists()
    lint_content = lint_path.read_text()
    assert "name: Ruff Lint" in lint_content
    assert "astral-sh/ruff-action" in lint_content

    # Check test workflow
    test_path = project_path / ".github" / "workflows" / "test.yml"
    assert test_path.exists()
    test_content = test_path.read_text()
    assert "name: Test" in test_content
    assert "pytest" in test_content


def test_setup_ruff(project_path):
    """Test Ruff and pre-commit setup."""
    project_path.mkdir(parents=True, exist_ok=True)
    # Create a basic pyproject.toml
    pyproject_path = project_path / "pyproject.toml"
    pyproject_path.write_text("""[project]
name = "test-project"
version = "0.1.0"
""")

    setup_ruff(project_path)

    # Check pre-commit config
    pre_commit_path = project_path / ".pre-commit-config.yaml"
    assert pre_commit_path.exists()
    pre_commit_content = pre_commit_path.read_text()
    assert "ruff-pre-commit" in pre_commit_content

    # Check pyproject.toml update
    pyproject_content = pyproject_path.read_text()
    assert "pre-commit" in pyproject_content


def test_update_pyproject_description(project_path):
    """Test pyproject.toml description update."""
    project_path.mkdir(parents=True, exist_ok=True)
    # Test with empty description
    pyproject_path = project_path / "pyproject.toml"
    pyproject_path.write_text("""[project]
name = "test-project"
version = "0.1.0"
description = ""
""")

    update_pyproject_description(pyproject_path, "")
    content = pyproject_path.read_text()
    assert 'description = ""' in content

    # Test with new description
    update_pyproject_description(pyproject_path, "A test project")
    content = pyproject_path.read_text()
    assert 'description = "A test project"' in content

    # Test with multiline description
    multiline_desc = "A test project\nwith multiple lines"
    update_pyproject_description(pyproject_path, multiline_desc)
    content = pyproject_path.read_text()
    # Check that the multiline description is there - doesn't have to be escaped exactly
    assert "A test project" in content
    assert "with multiple lines" in content

    # Test with quotes in description
    quoted_desc = 'A "quoted" description'
    update_pyproject_description(pyproject_path, quoted_desc)
    content = pyproject_path.read_text()
    assert 'A \\"quoted\\" description' in content
