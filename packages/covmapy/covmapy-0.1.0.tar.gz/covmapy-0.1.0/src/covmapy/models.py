from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union


class OutputFormat(Enum):
    """Supported output formats for coverage visualizations."""

    HTML = "html"

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get list of supported format strings."""
        return [fmt.value for fmt in cls]


@dataclass
class FileCoverage:
    """Represents coverage data for a single file."""

    filename: str
    total_lines: int
    covered_lines: int

    @property
    def coverage_rate(self) -> float:
        """Calculate coverage rate as a value between 0.0 and 1.0."""
        return self.covered_lines / self.total_lines if self.total_lines > 0 else 0.0


@dataclass
class CoverageReport:
    """Represents coverage data for multiple files."""

    files: list[FileCoverage]


@dataclass
class DirectoryNode:
    """Represents a directory node in the hierarchical coverage tree."""

    name: str
    path: str
    children: list[Union[DirectoryNode, FileNode]]
    parent: Optional[DirectoryNode] = None

    @property
    def total_lines(self) -> int:
        """Calculate total lines in this directory and all subdirectories."""
        total = 0
        for child in self.children:
            total += child.total_lines
        return total

    @property
    def covered_lines(self) -> int:
        """Calculate covered lines in this directory and all subdirectories."""
        total = 0
        for child in self.children:
            total += child.covered_lines
        return total

    @property
    def coverage_rate(self) -> float:
        """Calculate coverage rate for this directory."""
        if self.total_lines == 0:
            return 0.0
        return self.covered_lines / self.total_lines

    def add_child(self, child: Union[DirectoryNode, FileNode]) -> None:
        """Add a child node to this directory."""
        child.parent = self
        self.children.append(child)


@dataclass
class FileNode:
    """Represents a file node in the hierarchical coverage tree."""

    name: str
    path: str
    file_coverage: FileCoverage
    parent: Optional[DirectoryNode] = None

    @property
    def total_lines(self) -> int:
        """Get total lines for this file."""
        return self.file_coverage.total_lines

    @property
    def covered_lines(self) -> int:
        """Get covered lines for this file."""
        return self.file_coverage.covered_lines

    @property
    def coverage_rate(self) -> float:
        """Get coverage rate for this file."""
        return self.file_coverage.coverage_rate


@dataclass
class HierarchicalCoverageReport:
    """Represents hierarchical coverage data with directory structure."""

    root: DirectoryNode
