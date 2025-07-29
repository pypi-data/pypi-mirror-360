# Contributing to covmapy

Thank you for your interest in contributing to covmapy! This document provides guidelines and information for contributors to help maintain high code quality and ensure a smooth development experience.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Submitting Contributions](#submitting-contributions)
- [Code of Conduct](#code-of-conduct)
- [Recognition](#recognition)

## Getting Started

covmapy is a Python CLI tool that converts coverage.xml files into interactive treemap visualizations using Plotly. We welcome contributions of all kinds, including:

- Bug fixes
- New features
- Documentation improvements
- Performance optimizations
- Test coverage improvements

## Development Setup

### Prerequisites

- Python 3.9 or higher
- [uv](https://docs.astral.sh/uv/) package manager (or use standard `pip` if you prefer)
- Git

### Installation

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:

   ```bash
   git clone https://github.com/YOUR_USERNAME/covmapy.git
   cd covmapy
   ```

3. **Set up the development environment**:

   ```bash
   # Install dependencies
   uv sync

   # Alternatively, if you don't have uv installed:
   # python -m pip install -r requirements.txt  # install deps
   # python -m pip install -e .                 # install covmapy itself
   #
   # Replace subsequent `uv run …` commands with the bare command
   # (e.g., `pytest`, `mypy .`, `ruff …`) or prefix with
   # `python -m` when needed.

   # Install pre-commit hooks
   uv run pre-commit install
   ```

4. **Verify the setup**:

   ```bash
   # Run tests
   uv run pytest

   # Run type checking
   uv run mypy .

   # Run linting
   uv run ruff check .
   ```

## Development Workflow

### Core Development Commands

```bash
# Sync dependencies
uv sync

# Run tests with coverage
uv run pytest

# Type checking (strict mode)
uv run mypy .

# Linting and formatting
uv run ruff check --fix .
uv run ruff format .

# Comprehensive lint script
./scripts/lint.sh [--fix] [--log]

# Pre-commit hooks (run on all files)
uv run pre-commit run --all-files
```

### CLI Testing

```bash
# Test the CLI (skip if already installed above)
uv run covmapy coverage.xml --output test-report.html
```

### Project Architecture

covmapy follows a modular architecture with dependency injection:

- **Parser Layer**: `XMLCoverageParser` handles coverage.xml parsing
- **Data Models**: `FileCoverage`, `CoverageReport`, `HierarchicalCoverageReport`
- **Visualization**: `PlotlyTreemapLayout` generates interactive treemaps
- **CLI**: Click-based command-line interface
- **Core Orchestrator**: `PlotlyCoveragePlotter` coordinates components

## Code Standards

### Type Safety

- **Complete type annotations** are required for all functions, methods, and variables
- **Strict mypy configuration** - all code must pass type checking
- Use specific types rather than generic containers when possible

### Code Style

- **Line length**: 120 characters maximum (configured in `pyproject.toml`)
- **Naming conventions**:
  - `snake_case` for functions and variables
  - `PascalCase` for classes
  - `UPPER_SNAKE_CASE` for constants
- **Docstrings**: Google-style docstrings for all public functions and classes
- **Import organization**: Absolute imports, grouped and sorted alphabetically

### Code Quality Tools

All code must pass the following automated checks:

- **ruff** – linting & formatting
- **mypy** – static type checking (strict)
- **pytest** – unit & integration tests with coverage
- **pre-commit** – automatic hook runner

See [Core Development Commands](#core-development-commands) for full command details.

### Error Handling

- Use specific exception types rather than generic `Exception`
- Create custom exceptions for library-specific errors (see `src/covmapy/exceptions.py`)
- Include helpful error messages with context

## Testing

### Test Structure

- **Unit tests**: Located in `tests/unit/`, test individual components in isolation
- **Integration tests**: Located in `tests/integration/`, test component interactions
- **Fixtures**: Common test data and setup in `tests/fixtures/`

### Testing Requirements

- **Coverage**: Maintain >95% test coverage
- **Type annotations**: All test functions must be type-annotated
- **Parametrized tests**: Use `pytest.mark.parametrize` for comprehensive testing
- **Descriptive names**: Use clear, descriptive test function names

### Running Tests

```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/unit/covmapy/test_parser.py

# Run with verbose output
uv run pytest -v

# Generate coverage report
uv run pytest --cov-report=html
```

## Submitting Contributions

### Before Submitting

1. **Ensure all tests pass**:

   ```bash
   uv run pytest
   ```

2. **Run quality checks**:

   ```bash
   uv run mypy .
   uv run ruff check .
   uv run ruff format .
   ```

3. **Run pre-commit hooks**:

   ```bash
   uv run pre-commit run --all-files
   ```

### Pull Request Process

1. **Create a feature branch** from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code standards above

3. **Add tests** for new functionality

4. **Update documentation** if needed

5. **Commit your changes** with clear, descriptive messages:

   ```bash
   git add .
   git commit -m "feat: add support for branch coverage visualization"
   ```

6. **Push to your fork**:

   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub with:
   - Clear title and description
   - Reference to any related issues
   - Screenshots for UI changes (if applicable)
   - Confirmation that all checks pass

### PR Guidelines

- **Small, focused changes**: Keep PRs focused on a single feature or fix
- **Clear descriptions**: Explain what the change does and why
- **Test coverage**: Include tests for new functionality
- **Documentation**: Update docs for API changes
- **Backward compatibility**: Avoid breaking changes when possible

## Code of Conduct

Please note that this project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating in this project, you agree to abide by its terms.

## Recognition

### Contributors

We appreciate all contributions to covmapy! Contributors are recognized in several ways:

- **GitHub Contributors**: All contributors are automatically listed on the repository's contributors page
- **Release Notes**: Significant contributions are mentioned in release notes
- **Documentation**: Major contributors may be listed in project documentation

### Types of Contributions

We value all types of contributions:

- **Code**: Bug fixes, new features, performance improvements
- **Documentation**: README updates, API documentation, tutorials
- **Testing**: Additional test cases, improved test coverage
- **Design**: UX improvements, visual enhancements
- **Community**: Answering questions, helping other contributors

### Getting Help

If you need help contributing:

- **Issues**: Check existing issues or create a new one
- **Discussions**: Use GitHub Discussions for general questions
- **Documentation**: Refer to the [coding style guide](docs/coding_style.md)

## Development Tips

### Performance Considerations

- Use generators for large data processing
- Cache expensive computations appropriately
- Profile performance-critical code paths

### Debugging

- Use the `--verbose` flag for detailed CLI output
- Check the `test_outputs/` directory for generated files during development
- Use `pdb` or your IDE's debugger for complex issues

### Documentation

- Update docstrings for any API changes
- Add examples for new features
- Keep README.md current with feature additions

Thank you for contributing to covmapy! Your efforts help make coverage visualization better for everyone.
