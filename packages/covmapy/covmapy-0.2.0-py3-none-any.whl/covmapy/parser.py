import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from pathlib import Path

from covmapy.models import (
    CoverageReport,
    DirectoryNode,
    FileCoverage,
    FileNode,
    HierarchicalCoverageReport,
)


class CoverageParseError(Exception):
    """Raised when coverage data cannot be parsed."""

    def __init__(self, file_path: str, reason: str) -> None:
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Failed to parse coverage from {file_path}: {reason}")


class InvalidXMLError(CoverageParseError):
    """Raised when XML content is invalid."""

    def __init__(self) -> None:
        super().__init__("XML content", "Invalid XML format")


class CoverageParser(ABC):
    """Abstract base class for coverage parsers."""

    @abstractmethod
    def parse(self, content: str) -> CoverageReport:
        """Parse coverage data from string content.

        Args:
            content: Raw coverage data as string

        Returns:
            Parsed coverage report

        Raises:
            CoverageParseError: If parsing fails
        """


class XMLCoverageParser(CoverageParser):
    """Parser for coverage.xml format."""

    def parse(self, content: str) -> CoverageReport:
        """Parse coverage data from XML string.

        Args:
            content: XML coverage data as string

        Returns:
            Parsed coverage report containing file coverage data

        Raises:
            CoverageParseError: If XML parsing fails or format is invalid
        """
        try:
            root = ET.fromstring(content)  # noqa: S314
        except ET.ParseError as e:
            raise InvalidXMLError from e

        files: list[FileCoverage] = []

        # Find all class elements (representing files)
        for class_elem in root.findall(".//class"):
            filename = class_elem.get("filename")
            if not filename:
                continue

            # Count lines and hits
            total_lines = 0
            covered_lines = 0

            for line_elem in class_elem.findall(".//line"):
                total_lines += 1
                hits = line_elem.get("hits", "0")
                if int(hits) > 0:
                    covered_lines += 1

            if total_lines > 0:
                file_coverage = FileCoverage(
                    filename=filename,
                    total_lines=total_lines,
                    covered_lines=covered_lines,
                )
                files.append(file_coverage)

        return CoverageReport(files=files)

    def parse_hierarchical(self, content: str) -> HierarchicalCoverageReport:
        """Parse coverage data into hierarchical structure.

        Args:
            content: XML coverage data as string

        Returns:
            Parsed hierarchical coverage report with directory structure

        Raises:
            CoverageParseError: If XML parsing fails or format is invalid
        """
        # First parse flat structure
        flat_report = self.parse(content)

        # Build hierarchical structure
        return self._build_hierarchy(flat_report)

    def _build_hierarchy(self, report: CoverageReport) -> HierarchicalCoverageReport:
        """Build hierarchical directory structure from flat file list.

        Args:
            report: Flat coverage report

        Returns:
            Hierarchical coverage report with directory tree
        """
        if not report.files:
            root = DirectoryNode(name="", path="", children=[])
            return HierarchicalCoverageReport(root=root)

        # Find common root path
        common_root = self._find_common_root([f.filename for f in report.files])

        # Create root directory
        root = DirectoryNode(
            name=Path(common_root).name if common_root else "root",
            path=common_root,
            children=[],
        )

        # Build directory tree
        directory_map: dict[str, DirectoryNode] = {common_root: root}

        for file_coverage in report.files:
            self._add_file_to_tree(file_coverage, root, directory_map, common_root)

        return HierarchicalCoverageReport(root=root)

    def _find_common_root(self, filepaths: list[str]) -> str:
        """Find common root path for all files.

        Args:
            filepaths: List of file paths

        Returns:
            Common root path string
        """
        if not filepaths:
            return ""

        if len(filepaths) == 1:
            return str(Path(filepaths[0]).parent)

        # Convert to Path objects and find common parts
        paths = [Path(fp) for fp in filepaths]
        common_parts = []

        # Find minimum number of parts
        min_parts = min(len(p.parts) for p in paths)

        for i in range(min_parts):
            # Get the i-th part from all paths
            parts_at_i = [p.parts[i] for p in paths]

            # Check if all parts are the same
            if all(part == parts_at_i[0] for part in parts_at_i):
                common_parts.append(parts_at_i[0])
            else:
                break

        if not common_parts:
            return ""

        return str(Path(*common_parts))

    def _add_file_to_tree(
        self,
        file_coverage: FileCoverage,
        root: DirectoryNode,
        directory_map: dict[str, DirectoryNode],
        common_root: str,
    ) -> None:
        """Add a file to the directory tree.

        Args:
            file_coverage: File coverage data
            root: Root directory node
            directory_map: Map of directory paths to nodes
            common_root: Common root path
        """
        file_path = Path(file_coverage.filename)

        # Remove common root from file path
        if common_root:
            try:
                relative_path = file_path.relative_to(common_root)
            except ValueError:
                # If file is not under common root, use absolute path
                relative_path = file_path
        else:
            relative_path = file_path

        # Create directory structure
        current_dir = root
        current_path = common_root

        # Process each directory component
        for _i, part in enumerate(relative_path.parts[:-1]):  # Exclude filename
            dir_path = str(Path(current_path) / part) if current_path else part

            if dir_path not in directory_map:
                # Create new directory node
                new_dir = DirectoryNode(name=part, path=dir_path, children=[])
                current_dir.add_child(new_dir)
                directory_map[dir_path] = new_dir

            current_dir = directory_map[dir_path]
            current_path = dir_path

        # Add file node
        file_node = FileNode(
            name=relative_path.name,
            path=file_coverage.filename,
            file_coverage=file_coverage,
        )
        current_dir.add_child(file_node)


def parse_coverage_file(file_path: Path) -> CoverageReport:
    """Parse coverage data from XML file.

    Args:
        file_path: Path to the coverage XML file

    Returns:
        Parsed coverage report

    Raises:
        FileNotFoundError: If the file doesn't exist
        CoverageParseError: If parsing fails
    """
    if not file_path.exists():
        msg = f"Coverage file not found: {file_path}"
        raise FileNotFoundError(msg)

    try:
        content = file_path.read_text(encoding="utf-8")
        parser = XMLCoverageParser()
        return parser.parse(content)
    except UnicodeDecodeError as e:
        raise CoverageParseError(str(file_path), str(e)) from e
