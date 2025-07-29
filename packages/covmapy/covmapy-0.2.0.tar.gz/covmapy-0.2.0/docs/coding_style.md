# Python Coding Style Guide(**WIP**)

This document outlines the coding standards and conventions for the covmapy library. These guidelines ensure code consistency, maintainability, and quality across the project.

## General Principles

- **Clarity over cleverness**: Write code that is easy to read and understand
- **Consistency**: Follow established patterns within the codebase
- **Type safety**: Leverage Python's type system for better code reliability
- **Library-first approach**: Design APIs that are intuitive for library users


### Import Organization

- Use absolute imports for modules within the library
- Separate import groups with a blank line
- Sort imports alphabetically within each group
- Use `from __future__ import annotations` for forward compatibility when needed

## Type Annotations

### Function and Method Signatures

- **All functions and methods must have complete type annotations**
- Include return types for all functions, even if they return `None`
- Use specific types rather than generic containers when possible

```python
# Good
def parse_coverage_file(file_path: Path) -> CoverageData:
    """Parse a coverage XML file and return structured data."""
    ...

def process_coverage_data(
    data: CoverageData,
    output_dir: Path,
    *,
    format: str = "png"
) -> None:
    """Process coverage data and generate visualization."""
    ...

# Bad
def parse_coverage_file(file_path):
    ...
```


## Code Structure

### Classes
- Use PascalCase for class names
- Keep classes focused on a single responsibility
- Use dataclasses for simple data containers
- Implement `__str__` and `__repr__` methods when appropriate

```python
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class CoverageData:
    """Represents coverage data for a single file or module."""

    file_path: str
    line_coverage: float
    branch_coverage: float
    missed_lines: List[int]

    def __post_init__(self) -> None:
        if not 0 <= self.line_coverage <= 100:
            raise ValueError("Line coverage must be between 0 and 100")
```

### Functions
- Use snake_case for function names
- Keep functions small and focused (typically under 20 lines)
- Use descriptive parameter names
- Prefer keyword-only arguments for configuration parameters

```python
def generate_treemap(
    coverage_data: CoverageData,
    *,
    width: int = 800,
    height: int = 600,
    color_scheme: str = "default"
) -> Image.Image:
    """Generate a treemap visualization of coverage data."""
    ...
```

### Variables and Constants
- Use snake_case for variables and function names
- Use UPPER_SNAKE_CASE for module-level constants
- Use descriptive names, avoid abbreviations unless they're well-known

```python
# Constants
DEFAULT_IMAGE_WIDTH = 800
MAX_RECURSION_DEPTH = 100
SUPPORTED_FORMATS = ("png", "svg", "pdf")

# Variables
coverage_percentage = calculate_coverage(data)
output_file_path = output_dir / f"coverage_{timestamp}.png"
```

## Documentation

### Docstrings
- Use Google-style docstrings for all public functions, classes, and methods
- Include type information in docstrings only when it adds clarity beyond type hints
- Provide examples for complex functions

```python
def calculate_treemap_layout(
    data: List[CoverageItem],
    *,
    width: int,
    height: int,
    algorithm: str = "squarified"
) -> List[Rectangle]:
    """Calculate the layout for treemap rectangles.

    Args:
        data: List of coverage items to visualize
        width: Total width of the treemap
        height: Total height of the treemap
        algorithm: Layout algorithm to use ('squarified' or 'strip')

    Returns:
        List of rectangles with calculated positions and sizes

    Raises:
        ValueError: If algorithm is not supported

    Example:
        >>> items = [CoverageItem("file1.py", 0.8), CoverageItem("file2.py", 0.6)]
        >>> layout = calculate_treemap_layout(items, width=800, height=600)
        >>> len(layout) == len(items)
        True
    """
    ...
```

## Error Handling

### Exceptions
- Use specific exception types rather than generic `Exception`
- Create custom exceptions for library-specific errors
- Include helpful error messages with context

```python
class CoverageParseError(Exception):
    """Raised when coverage data cannot be parsed."""

    def __init__(self, file_path: str, reason: str) -> None:
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Failed to parse coverage from {file_path}: {reason}")

def parse_xml_coverage(file_path: Path) -> CoverageData:
    """Parse coverage data from XML file."""
    if not file_path.exists():
        raise FileNotFoundError(f"Coverage file not found: {file_path}")

    try:
        # Parse XML content
        ...
    except ET.ParseError as e:
        raise CoverageParseError(str(file_path), f"Invalid XML: {e}") from e
```

## Testing Guidelines

### Test Structure
- Use descriptive test function names with `test_` prefix
- Group related tests in classes when appropriate
- Use fixtures for common test data and setup

```python
import pytest
from pathlib import Path

from covmapy.core import parse_coverage_file
from covmapy.models import CoverageData

class TestCoverageParser:
    """Tests for coverage file parsing functionality."""

    def test_parse_valid_xml_file(self, sample_coverage_xml: Path) -> None:
        """Should successfully parse a valid coverage XML file."""
        result = parse_coverage_file(sample_coverage_xml)

        assert isinstance(result, CoverageData)
        assert result.line_coverage >= 0
        assert result.line_coverage <= 100

    def test_parse_nonexistent_file_raises_error(self) -> None:
        """Should raise FileNotFoundError for non-existent files."""
        with pytest.raises(FileNotFoundError, match="Coverage file not found"):
            parse_coverage_file(Path("nonexistent.xml"))
```

## Library API Design

### Public Interface
- Mark private functions and classes with leading underscore
- Use properties for computed attributes
- Provide sensible defaults for optional parameters
- Design for extensibility where appropriate

```python
class CoveragePlotter:
    """Main interface for generating coverage visualizations."""

    def __init__(self, coverage_data: CoverageData) -> None:
        self._data = coverage_data
        self._cache: Dict[str, Any] = {}

    @property
    def total_coverage(self) -> float:
        """Calculate total coverage percentage."""
        return self._calculate_total_coverage()

    def generate_plot(
        self,
        output_path: Path,
        *,
        format: str = "png",
        theme: str = "default",
        **kwargs: Any
    ) -> None:
        """Generate and save coverage plot."""
        ...

    def _calculate_total_coverage(self) -> float:
        """Internal method to calculate coverage."""
        ...
```

## Performance Considerations

### Efficiency Guidelines
- Use generators for large data processing when possible
- Cache expensive computations appropriately
- Prefer built-in functions and libraries for common operations
- Profile performance-critical code paths

```python
from functools import lru_cache
from typing import Iterator

def process_coverage_files(file_paths: List[Path]) -> Iterator[CoverageData]:
    """Process multiple coverage files efficiently."""
    for file_path in file_paths:
        yield parse_coverage_file(file_path)

@lru_cache(maxsize=128)
def calculate_color_for_coverage(coverage: float) -> tuple[int, int, int]:
    """Calculate RGB color for coverage percentage (cached)."""
    ...
```

## Code Quality Tools

The project uses several tools to maintain code quality:

- **pyright**: Static type checking with strict mode enabled
- **ruff**: Fast Python linter and formatter
- **pytest**: Testing framework with coverage reporting
- **pre-commit**: Git hooks for code quality checks

Ensure all code passes these checks before committing:

```bash
# Run type checking
pyright src tests

# Run linting and formatting
ruff check --fix .
ruff format .

# Run tests with coverage
pytest
```

## Summary

Following these guidelines will help maintain high code quality and consistency across the covmapy library. The emphasis on type safety, clear documentation, and thoughtful API design ensures the library remains maintainable and user-friendly as it grows.
