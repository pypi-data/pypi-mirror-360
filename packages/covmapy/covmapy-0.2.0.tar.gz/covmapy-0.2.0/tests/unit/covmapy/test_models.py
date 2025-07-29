from typing import Union, cast

import pytest

from covmapy.models import (
    CoverageReport,
    DirectoryNode,
    FileCoverage,
    FileNode,
    HierarchicalCoverageReport,
)


class TestFileCoverage:
    """Test FileCoverage model."""

    @pytest.mark.parametrize(
        "filename,total_lines,covered_lines,expected_rate",
        [
            ("test.py", 100, 80, 0.8),
            ("test.py", 100, 100, 1.0),
            ("test.py", 100, 0, 0.0),
            ("test.py", 50, 25, 0.5),
            ("test.py", 1, 1, 1.0),
        ],
    )
    def test_file_coverage_rate_calculation(
        self, filename: str, total_lines: int, covered_lines: int, expected_rate: float
    ) -> None:
        """Test coverage rate calculation with various inputs."""
        file_coverage = FileCoverage(filename=filename, total_lines=total_lines, covered_lines=covered_lines)
        assert file_coverage.coverage_rate == expected_rate

    def test_file_coverage_rate_zero_total_lines(self) -> None:
        """Test coverage rate when total_lines is zero."""
        file_coverage = FileCoverage(filename="empty.py", total_lines=0, covered_lines=0)
        assert file_coverage.coverage_rate == 0.0

    @pytest.mark.parametrize(
        "total_lines,covered_lines",
        [
            (100, 80),
            (50, 50),
            (1, 0),
            (1000, 999),
        ],
    )
    def test_file_coverage_dataclass_attributes(self, total_lines: int, covered_lines: int) -> None:
        """Test that dataclass attributes are properly set."""
        filename = "test_file.py"
        file_coverage = FileCoverage(filename=filename, total_lines=total_lines, covered_lines=covered_lines)
        assert file_coverage.filename == filename
        assert file_coverage.total_lines == total_lines
        assert file_coverage.covered_lines == covered_lines


class TestCoverageReport:
    """Test CoverageReport model."""

    def test_coverage_report_empty_files_list(self) -> None:
        """Test CoverageReport with empty files list."""
        report = CoverageReport(files=[])
        assert report.files == []

    def test_coverage_report_single_file(self) -> None:
        """Test CoverageReport with single file."""
        file_coverage = FileCoverage("test.py", 100, 80)
        report = CoverageReport(files=[file_coverage])
        assert len(report.files) == 1
        assert report.files[0] == file_coverage

    def test_coverage_report_multiple_files(self) -> None:
        """Test CoverageReport with multiple files."""
        files = [
            FileCoverage("test1.py", 100, 80),
            FileCoverage("test2.py", 200, 150),
            FileCoverage("test3.py", 50, 25),
        ]
        report = CoverageReport(files=files)
        assert len(report.files) == 3
        assert report.files == files

    def test_coverage_report_files_list_mutability(self) -> None:
        """Test that the files list can be modified after creation."""
        report = CoverageReport(files=[])
        new_file = FileCoverage("new.py", 50, 40)
        report.files.append(new_file)
        assert len(report.files) == 1
        assert report.files[0] == new_file


class TestDirectoryNode:
    """Test DirectoryNode model."""

    def test_directory_node_empty_aggregation(self) -> None:
        """Test directory with no children has zero aggregation values."""
        directory = DirectoryNode(name="empty", path="empty", children=[])

        assert directory.total_lines == 0
        assert directory.covered_lines == 0
        assert directory.coverage_rate == 0.0

    def test_directory_node_single_file_aggregation(self) -> None:
        """Test directory aggregation with single file."""
        file_coverage = FileCoverage("file1.py", 100, 80)
        file_node = FileNode("file1.py", "dir/file1.py", file_coverage)
        directory = DirectoryNode(name="dir", path="dir", children=[file_node])

        assert directory.total_lines == 100
        assert directory.covered_lines == 80
        assert directory.coverage_rate == 0.8

    def test_directory_node_multiple_files_aggregation(self) -> None:
        """Test directory aggregation with multiple files."""
        file1_coverage = FileCoverage("file1.py", 100, 80)
        file2_coverage = FileCoverage("file2.py", 50, 25)
        file1 = FileNode("file1.py", "dir/file1.py", file1_coverage)
        file2 = FileNode("file2.py", "dir/file2.py", file2_coverage)
        directory = DirectoryNode(name="dir", path="dir", children=[file1, file2])

        assert directory.total_lines == 150  # 100 + 50
        assert directory.covered_lines == 105  # 80 + 25
        assert directory.coverage_rate == 0.7  # 105/150

    def test_directory_node_nested_aggregation(self) -> None:
        """Test nested directory aggregation."""
        file1_coverage = FileCoverage("file1.py", 100, 80)
        file2_coverage = FileCoverage("file2.py", 50, 25)
        file3_coverage = FileCoverage("file3.py", 200, 150)

        # Create nested structure: root -> subdir -> files
        file1 = FileNode("file1.py", "root/file1.py", file1_coverage)
        file2 = FileNode("file2.py", "root/subdir/file2.py", file2_coverage)
        file3 = FileNode("file3.py", "root/subdir/file3.py", file3_coverage)

        subdir = DirectoryNode(name="subdir", path="root/subdir", children=[file2, file3])
        root = DirectoryNode(name="root", path="root", children=[file1, subdir])

        # Test subdir aggregation
        assert subdir.total_lines == 250  # 50 + 200
        assert subdir.covered_lines == 175  # 25 + 150
        assert subdir.coverage_rate == 0.7  # 175/250

        # Test root aggregation (includes all children)
        assert root.total_lines == 350  # 100 + 250
        assert root.covered_lines == 255  # 80 + 175
        assert root.coverage_rate == 255 / 350  # approximately 0.729

    def test_directory_node_mixed_children(self) -> None:
        """Test directory with mix of file and directory children."""
        file1_coverage = FileCoverage("file1.py", 100, 80)
        file2_coverage = FileCoverage("file2.py", 50, 25)
        file1 = FileNode("file1.py", "root/file1.py", file1_coverage)

        # Create subdirectory with its own file
        file2 = FileNode("file2.py", "root/subdir/file2.py", file2_coverage)
        subdir = DirectoryNode(name="subdir", path="root/subdir", children=[file2])

        root = DirectoryNode(name="root", path="root", children=[file1, subdir])

        assert root.total_lines == 150  # 100 + 50
        assert root.covered_lines == 105  # 80 + 25
        assert root.coverage_rate == 0.7

    def test_directory_node_add_child_sets_parent(self) -> None:
        """Test that add_child method sets parent relationship correctly."""
        parent = DirectoryNode(name="parent", path="parent", children=[])
        file_coverage = FileCoverage("child.py", 10, 8)
        child = FileNode("child.py", "parent/child.py", file_coverage)

        assert child.parent is None

        parent.add_child(child)

        assert child.parent == parent
        assert len(parent.children) == 1
        assert parent.children[0] is child

    def test_directory_node_add_child_directory(self) -> None:
        """Test that add_child works for directory children."""
        parent = DirectoryNode(name="parent", path="parent", children=[])
        child_dir = DirectoryNode(name="child", path="parent/child", children=[])

        parent.add_child(child_dir)

        assert child_dir.parent is parent

    @pytest.mark.parametrize(
        "child_coverages,expected_total,expected_covered,expected_rate",
        [
            # Single file scenarios
            ([(100, 80)], 100, 80, 0.8),
            ([(0, 0)], 0, 0, 0.0),  # Zero lines edge case
            ([(10, 10)], 10, 10, 1.0),  # Perfect coverage
            ([(50, 0)], 50, 0, 0.0),  # No coverage
            # Multiple file scenarios
            ([(100, 80), (50, 25)], 150, 105, 0.7),
            ([(100, 50), (200, 100), (300, 150)], 600, 300, 0.5),
            ([(0, 0), (100, 50)], 100, 50, 0.5),  # Mix with zero lines
        ],
    )
    def test_directory_node_aggregation_parametrized(
        self,
        child_coverages: list[tuple[int, int]],
        expected_total: int,
        expected_covered: int,
        expected_rate: float,
    ) -> None:
        """Test directory aggregation with various child combinations."""
        children = []
        for i, (total, covered) in enumerate(child_coverages):
            file_coverage = FileCoverage(f"file{i}.py", total, covered)
            file_node = FileNode(f"file{i}.py", f"dir/file{i}.py", file_coverage)
            children.append(file_node)

        directory = DirectoryNode(
            name="dir", path="dir", children=cast("list[Union[DirectoryNode, FileNode]]", children)
        )

        assert directory.total_lines == expected_total
        assert directory.covered_lines == expected_covered
        assert directory.coverage_rate == pytest.approx(expected_rate)


class TestFileNode:
    """Test FileNode model."""

    def test_file_node_property_delegation(self) -> None:
        """Test that FileNode correctly delegates properties to FileCoverage."""
        file_coverage = FileCoverage("test.py", 100, 75)
        file_node = FileNode("test.py", "path/test.py", file_coverage)

        assert file_node.total_lines == file_coverage.total_lines
        assert file_node.covered_lines == file_coverage.covered_lines
        assert file_node.coverage_rate == file_coverage.coverage_rate

    def test_file_node_delegation_with_zero_lines(self) -> None:
        """Test property delegation with zero lines edge case."""
        file_coverage = FileCoverage("empty.py", 0, 0)
        file_node = FileNode("empty.py", "path/empty.py", file_coverage)

        assert file_node.total_lines == 0
        assert file_node.covered_lines == 0
        assert file_node.coverage_rate == 0.0

    @pytest.mark.parametrize(
        "total_lines,covered_lines,expected_rate",
        [
            (100, 75, 0.75),
            (50, 50, 1.0),
            (200, 0, 0.0),
            (1, 1, 1.0),
            (10, 5, 0.5),
        ],
    )
    def test_file_node_delegation_parametrized(
        self,
        total_lines: int,
        covered_lines: int,
        expected_rate: float,
    ) -> None:
        """Test FileNode property delegation with various coverage values."""
        file_coverage = FileCoverage("test.py", total_lines, covered_lines)
        file_node = FileNode("test.py", "path/test.py", file_coverage)

        assert file_node.total_lines == total_lines
        assert file_node.covered_lines == covered_lines
        assert file_node.coverage_rate == expected_rate

    def test_file_node_parent_initialization(self) -> None:
        """Test FileNode parent relationship initialization."""
        file_coverage = FileCoverage("test.py", 100, 75)
        file_node = FileNode("test.py", "path/test.py", file_coverage)

        assert file_node.parent is None

        # Test with parent
        parent = DirectoryNode("dir", "path", [])
        file_node_with_parent = FileNode("test.py", "path/test.py", file_coverage, parent)

        assert file_node_with_parent.parent is parent


class TestHierarchicalCoverageReport:
    """Test HierarchicalCoverageReport model."""

    def test_hierarchical_coverage_report_creation(self) -> None:
        """Test creation of hierarchical coverage report."""
        root = DirectoryNode(name="src", path="src", children=[])
        report = HierarchicalCoverageReport(root=root)

        assert report.root is root
        assert isinstance(report.root, DirectoryNode)

    def test_hierarchical_coverage_report_with_complex_structure(self) -> None:
        """Test hierarchical report with complex directory structure."""
        # Create files
        file1_coverage = FileCoverage("main.py", 100, 80)
        file2_coverage = FileCoverage("utils.py", 50, 40)
        file3_coverage = FileCoverage("models.py", 200, 160)

        # Create nodes
        file1 = FileNode("main.py", "src/main.py", file1_coverage)
        file2 = FileNode("utils.py", "src/lib/utils.py", file2_coverage)
        file3 = FileNode("models.py", "src/lib/models.py", file3_coverage)

        # Create directory structure
        lib_dir = DirectoryNode("lib", "src/lib", [file2, file3])
        root = DirectoryNode("src", "src", [file1, lib_dir])

        report = HierarchicalCoverageReport(root=root)

        # Validate structure
        assert report.root.name == "src"
        assert len(report.root.children) == 2

        # Check aggregated values at root level
        assert report.root.total_lines == 350  # 100 + 50 + 200
        assert report.root.covered_lines == 280  # 80 + 40 + 160
        assert report.root.coverage_rate == 0.8  # 280/350

    def test_hierarchical_coverage_report_empty_structure(self) -> None:
        """Test hierarchical report with empty root directory."""
        root = DirectoryNode(name="", path="", children=[])
        report = HierarchicalCoverageReport(root=root)

        assert report.root.total_lines == 0
        assert report.root.covered_lines == 0
        assert report.root.coverage_rate == 0.0

    def test_deep_nesting_aggregation_correctness(self) -> None:
        """Test correctness of aggregation in deeply nested structures."""
        # Create a deeply nested structure: root/a/b/c/d/file.py
        file_coverage = FileCoverage("deep.py", 100, 60)
        file_node = FileNode("deep.py", "root/a/b/c/d/deep.py", file_coverage)

        d_dir = DirectoryNode("d", "root/a/b/c/d", [file_node])
        c_dir = DirectoryNode("c", "root/a/b/c", [d_dir])
        b_dir = DirectoryNode("b", "root/a/b", [c_dir])
        a_dir = DirectoryNode("a", "root/a", [b_dir])
        root = DirectoryNode("root", "root", [a_dir])

        # Each level should aggregate correctly
        assert d_dir.total_lines == 100
        assert d_dir.covered_lines == 60
        assert d_dir.coverage_rate == 0.6

        assert c_dir.total_lines == 100
        assert c_dir.covered_lines == 60
        assert c_dir.coverage_rate == 0.6

        assert b_dir.total_lines == 100
        assert b_dir.covered_lines == 60
        assert b_dir.coverage_rate == 0.6

        assert a_dir.total_lines == 100
        assert a_dir.covered_lines == 60
        assert a_dir.coverage_rate == 0.6

        assert root.total_lines == 100
        assert root.covered_lines == 60
        assert root.coverage_rate == 0.6

    def test_parent_child_relationship_consistency(self) -> None:
        """Test that parent-child relationships are maintained correctly."""
        file_coverage = FileCoverage("test.py", 50, 30)
        file_node = FileNode("test.py", "dir/test.py", file_coverage)

        child_dir = DirectoryNode("child", "dir/child", [])
        parent_dir = DirectoryNode("parent", "dir", [])

        # Add children and verify relationships
        parent_dir.add_child(file_node)
        parent_dir.add_child(child_dir)

        assert file_node.parent is parent_dir
        assert child_dir.parent is parent_dir
        assert len(parent_dir.children) == 2

        # Verify aggregation still works
        assert parent_dir.total_lines == 50
        assert parent_dir.covered_lines == 30

    def test_mixed_coverage_scenarios(self) -> None:
        """Test various realistic coverage scenarios."""
        # Perfect coverage file
        perfect_file = FileNode("perfect.py", "src/perfect.py", FileCoverage("perfect.py", 100, 100))

        # No coverage file
        no_coverage_file = FileNode("uncovered.py", "src/uncovered.py", FileCoverage("uncovered.py", 50, 0))

        # Empty file
        empty_file = FileNode("empty.py", "src/empty.py", FileCoverage("empty.py", 0, 0))

        # Partial coverage file
        partial_file = FileNode("partial.py", "src/partial.py", FileCoverage("partial.py", 200, 75))

        root = DirectoryNode("src", "src", [perfect_file, no_coverage_file, empty_file, partial_file])

        # Total: 100 + 50 + 0 + 200 = 350
        # Covered: 100 + 0 + 0 + 75 = 175
        # Rate: 175/350 = 0.5
        assert root.total_lines == 350
        assert root.covered_lines == 175
        assert root.coverage_rate == 0.5
