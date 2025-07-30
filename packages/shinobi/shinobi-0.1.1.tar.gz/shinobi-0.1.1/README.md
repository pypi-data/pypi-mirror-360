# Shinobi

<div align="center">
  <img src="images/shinobi.png" width="500">
  <p>Enhanced project initialization tool built on top of `uv`. Shinobi helps you set up Python projects with best practices and common tools pre-configured.</p>

[![PyPI](https://badge.fury.io/py/shinobi.svg)](https://badge.fury.io/py/shinobi)
[![Unit Tests](https://github.com/iantimmis/shinobi/actions/workflows/test.yml/badge.svg)](https://github.com/iantimmis/shinobi/actions/workflows/test.yml)
[![Downloads](https://static.pepy.tech/badge/shinobi)](https://pepy.tech/project/shinobi)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

## Installation

```bash
# Install Shinobi
pip install shinobi
```

## Usage

Shinobi provides a simple CLI interface for initializing new Python projects:

```bash
# Show help
shinobi

# Initialize a new project
shinobi init

# Show help for init command
shinobi init --help
```

When you run `shinobi init`, you'll be guided through an interactive setup process that includes:

1. Project name and description
2. GitHub repository details (optional)
3. Python version selection
4. IDE preference (VS Code or Cursor)
5. Additional features:
   - GitHub Actions workflows
   - Pre-commit hooks with Ruff

## Features

- Modern Python project structure with `src` layout
- Built-in testing with pytest
- Optimized Python `.gitignore` from Toptal
- MIT License template
- Interactive project configuration with questionary

### 📦 Dependency Management

- Fast and reliable dependency management with `uv`
- Development dependencies group for testing and linting
- Pre-commit hooks for automated checks

### 🧪 Testing

- Pytest setup with comprehensive configuration
- Test directory structure with example tests
- Pre-configured test discovery and execution

### 🧰 Code Quality

- Ruff for lightning-fast linting and formatting
- Pre-commit hooks for automated code quality checks
- GitHub Actions workflows for CI/CD

### 🎯 IDE Support

- VS Code configuration with Ruff integration
- Cursor IDE rules for UV usage
- Editor-agnostic project structure

### 🔧 Development Tools

- GitHub Actions workflows for:
  - Automated linting with Ruff
  - Automated testing with pytest
- Pre-commit hooks for:
  - Ruff linting
  - Ruff formatting

## Project Structure

```
project_name/
├── src/              # Source code directory
│   └── main.py      # Main application code
├── tests/           # Test directory
│   └── __init__.py
│   └── test_main.py # Example test file
├── .github/         # GitHub Actions workflows
│   └── workflows/   # CI/CD workflows
├── .vscode/         # VS Code settings
├── .cursor/         # Cursor rules
├── .pre-commit-config.yaml
├── pyproject.toml   # Project configuration
└── README.md
```

## Development

### Running Tests

```bash
uv run pytest
```

### Code Quality

This project uses Ruff for linting and formatting. To run the checks:

```bash
# Lint
uv run ruff check

# Format
uv run ruff format
```

### Adding Dependencies

Always use `uv` for package management:

```bash
# Add a new dependency
uv add package_name

# Add a development dependency
uv add --dev package_name

# Update dependencies from requirements
uv sync
```

### Running Python Files

Always use `uv run` to execute Python files:

```bash
uv run file.py
```

## License

[MIT License](LICENSE)
