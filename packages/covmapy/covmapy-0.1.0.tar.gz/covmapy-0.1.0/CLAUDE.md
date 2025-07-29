# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

covmapy is a Python CLI tool that converts coverage.xml files into interactive treemap visualizations using Plotly. It transforms flat coverage data into hierarchical structures for better visualization.

## Development Commands

### Core Development Workflow

```bash
# Sync dependencies
uv sync

# Run tests with coverage
uv run pytest

# Type checking (strict mode)
uv run mypy .

# Linting and formatting (all Python files)
uv run ruff check --fix .
uv run ruff format .

# Comprehensive lint script (targets src/tests only)
./scripts/lint.sh [--fix] [--log]

# Pre-commit hooks
uv run pre-commit install
uv run pre-commit run --all-files
```

### CLI Usage

```bash
# Install package for development
uv run pip install -e .

# Run the CLI
uv run covmapy coverage.xml --output report.html
```

## Architecture Overview

### Core Components

**Dependency Injection Pattern**: The main `PlotlyCoveragePlotter` class uses dependency injection for parser and layout engine components, enabling flexible testing and extensibility.

**Data Flow**:

1. `XMLCoverageParser` parses coverage.xml into `FileCoverage` objects
2. `CoverageReport` aggregates individual file coverage data
3. `HierarchicalCoverageReport` converts flat data to tree structure via `DirectoryNode`/`FileNode`
4. `PlotlyTreemapLayout` generates interactive Plotly visualizations

**Key Data Models**:

- `FileCoverage`: Individual file coverage metrics
- `CoverageReport`/`HierarchicalCoverageReport`: Collection and hierarchical views
- `DirectoryNode`/`FileNode`: Tree structure for hierarchical data
- `PlotOptions`: CLI configuration via Click

### Code Organization

```t
src/covmapy/
├── cli.py              # Click-based CLI interface
├── core.py             # Main PlotlyCoveragePlotter orchestrator
├── models.py           # Data models and enums
├── parser.py           # XML coverage file parser
├── plotly_treemap.py   # Plotly visualization engine
├── color.py            # Color utilities
└── exceptions.py       # Custom exceptions
```

## Development Standards

### Type Safety

- **Strict mypy configuration** - all code must pass type checking
- **Complete type annotations** required for all functions, methods, and variables
- **Type-safe data models** using dataclasses and enums

### Code Quality

- **Ruff configuration** with comprehensive rule set and 120-character line length
- **Google-style docstrings** for all public functions and classes
- **Pre-commit hooks** enforce quality standards automatically

### Testing Strategy

- **Unit tests** in `tests/unit/` test individual components in isolation
- **Parametrized tests** using `pytest.mark.parametrize` for comprehensive coverage
- **Type-annotated tests** maintain same type safety standards as source code
- **Coverage reporting** configured for HTML, XML, and terminal output

## Key Development Patterns

### CLI Development

- Use **Click framework** for command-line interface
- **PlotOptions dataclass** for configuration management
- **Input validation** with meaningful error messages

### Error Handling

- **Custom exception classes** in `exceptions.py` with descriptive messages
- **Graceful error handling** throughout the pipeline with contextual information

### Data Model Design

- **Hierarchical data structures** using recursive node patterns
- **Immutable data models** where possible using dataclasses
- **Clear separation** between flat and hierarchical data representations

## Package Management

This project uses **uv** (modern Python package manager) instead of pip. Always use `uv install`, `uv run`, and `uv add` commands. The project targets Python 3.9+ with development on Python 3.13.
