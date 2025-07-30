# Developer Guide

First off, thank you for considering contributing to `ez-animate`! We're excited to have your help. This guide provides all the necessary information to get your development environment set up and to start contributing.

<!-- ## Table of Contents

- [Prerequisites](#prerequisites)
- [Step-by-Step Setup](#step-by-step-setup)
- [Running Tests](#running-tests)
- [Code Style and Linting](#code-style-and-linting)
- [Building the Documentation](#building-the-documentation)
- [Submitting Your Changes](#submitting-your-changes)
- [Dependency Management](#dependency-management) -->

## Prerequisites

Before you begin, please make sure you have the following installed on your system:

- **Git:** For version control.
- **Python:** Version 3.8 or newer.
- **uv:** The fast project and environment manager. If you don't have it, you can install it with:
  ```bash
  pip install uv
  ```

## Step-by-Step Setup

This will guide you from cloning the repository to having a fully functional local development setup.

### 1. Fork and Clone the Repository

First, [fork the repository](https://github.com/your-username/ez-animate/fork) on GitHub. Then, clone your fork to your local machine:

```bash
git clone https://github.com/SantiagoEnriqueGA/ez-animate.git
cd ez-animate
```

### 2. Create and Activate the Virtual Environment

We use `uv` to manage our virtual environment. This keeps project dependencies isolated from your global Python installation.

```bash
# Create the virtual environment in a .venv directory
uv venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (CMD):
.venv\Scripts\activate.bat
```

You'll know the environment is active when you see `(.venv)` at the beginning of your command prompt.

### 3. Install Dependencies

Install the project in "editable" mode along with all development dependencies (for testing, linting, and documentation).

```bash
# This command installs ez-animate and all its dependencies for development
uv pip install -e .[dev]
```

**Why this command?**

-   `-e .`: Installs the package in **editable mode**. This means any changes you make to the source code in the `src/` directory will be immediately available in your environment without needing to reinstall.
-   `[dev]`: This is an "extra" defined in our `pyproject.toml`. It installs the optional groups of dependencies needed for running tests, checking code style, and building the documentation.

You are now ready to start developing!

## Running Tests

We use `pytest` for testing. High-quality, passing tests are required for any contribution to be merged.

To run the entire test suite:

```bash
uv run pytest
```

To run tests in a specific file:

```bash
uv run pytest tests/test_animator.py
```

To run tests with code coverage:

```bash
uv run pytest --cov=src/ez_animate --cov-report=term-missing
```

## Code Style and Linting

To maintain a consistent and high-quality codebase, we use **Ruff** for code formatting and linting. Before submitting any code, please run this tool.

### Ruff (Linter and Formatter)

Ruff is an extremely fast linter that helps catch common errors and style issues.

```bash
# Check for any issues
uv run ruff check .

# Automatically fix any fixable issues
uv run ruff check . --fix
```

The CI/CD pipeline will fail if your code is not properly formatted, so it's best to run this before committing.

## Building the Documentation

Our documentation is built with **MkDocs**. This allows you to preview your documentation changes locally before they are published.

To start the live-reloading local server:

```bash
uv run mkdocs serve
```

Now, open your web browser and navigate to **[http://127.0.0.1:8000](http://127.0.0.1:8000)**. The server will automatically rebuild the documentation and refresh your browser whenever you save a change in the `docs/` directory.

## Submitting Your Changes

1.  **Create a New Branch:** Start from the `main` branch and create a descriptive branch name for your feature or bugfix.
    ```bash
    git checkout main
    git pull origin main
    git checkout -b feature/my-cool-animation
    ```
2.  **Make Your Changes:** Write your code and the corresponding tests.
3.  **Test and Lint:** Run the tests and linters to ensure everything is correct.
    ```bash
    uv run pytest
    uv run ruff check . --fix
    uv run ruff format .
    ```
4.  **Commit Your Code:** Use a descriptive commit message following the [Conventional Commits](https://www.conventionalcommits.org/) standard.
    ```bash
    git add .
    git commit -m "feat: Add new FadeIn animation effect"
    ```
5.  **Push to Your Fork:**
    ```bash
    git push origin feature/my-cool-animation
    ```
6.  **Open a Pull Request:** Go to the `ez-animate` repository on GitHub and open a Pull Request from your fork's branch to the `main` branch. Provide a clear description of your changes.

## Dependency Management

The project's dependencies are defined in `pyproject.toml`.

-   **Core dependencies** are listed under `[project.dependencies]`. These are required for the package to run.
-   **Development dependencies** are listed under `[project.optional-dependencies]`.

If you need to add or remove a dependency, please update `pyproject.toml` accordingly and mention it in your Pull Request.
