"""Unit tests for coverage parser module."""

from pathlib import Path

import pytest

from covmapy.models import CoverageReport, DirectoryNode, FileCoverage, FileNode, HierarchicalCoverageReport
from covmapy.parser import (
    CoverageParseError,
    CoverageParser,
    InvalidXMLError,
    XMLCoverageParser,
    parse_coverage_file,
)


class TestXMLCoverageParser:
    """Test XMLCoverageParser class."""

    @pytest.fixture
    def parser(self) -> XMLCoverageParser:
        """Create XMLCoverageParser instance."""
        return XMLCoverageParser()

    @pytest.fixture
    def valid_xml(self) -> str:
        """Create valid coverage XML content."""
        return """<?xml version="1.0" ?>
<coverage version="7.3.2">
    <packages>
        <package name="src">
            <classes>
                <class filename="src/module1.py" name="module1.py">
                    <methods/>
                    <lines>
                        <line hits="1" number="1"/>
                        <line hits="1" number="2"/>
                        <line hits="0" number="3"/>
                        <line hits="1" number="4"/>
                    </lines>
                </class>
                <class filename="src/module2.py" name="module2.py">
                    <methods/>
                    <lines>
                        <line hits="1" number="1"/>
                        <line hits="0" number="2"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""

    @pytest.fixture
    def empty_xml(self) -> str:
        """Create empty coverage XML content."""
        return """<?xml version="1.0" ?>
<coverage version="7.3.2">
    <packages/>
</coverage>"""

    def test_parse_valid_xml(self, parser: XMLCoverageParser, valid_xml: str) -> None:
        """Test parsing valid XML content."""
        report = parser.parse(valid_xml)

        assert isinstance(report, CoverageReport)
        assert len(report.files) == 2

        # Check first file
        file1 = report.files[0]
        assert file1.filename == "src/module1.py"
        assert file1.total_lines == 4
        assert file1.covered_lines == 3
        assert file1.coverage_rate == 0.75

        # Check second file
        file2 = report.files[1]
        assert file2.filename == "src/module2.py"
        assert file2.total_lines == 2
        assert file2.covered_lines == 1
        assert file2.coverage_rate == 0.5

    def test_parse_empty_xml(self, parser: XMLCoverageParser, empty_xml: str) -> None:
        """Test parsing empty XML content."""
        report = parser.parse(empty_xml)

        assert isinstance(report, CoverageReport)
        assert len(report.files) == 0

    def test_parse_invalid_xml(self, parser: XMLCoverageParser) -> None:
        """Test parsing invalid XML content."""
        invalid_xml = "This is not XML"

        with pytest.raises(InvalidXMLError):
            parser.parse(invalid_xml)

    def test_parse_malformed_xml(self, parser: XMLCoverageParser) -> None:
        """Test parsing malformed XML content."""
        malformed_xml = """<?xml version="1.0" ?>
<coverage version="7.3.2">
    <packages>
        <unclosed_tag>
</coverage>"""

        with pytest.raises(InvalidXMLError):
            parser.parse(malformed_xml)

    @pytest.mark.parametrize(
        "xml_content",
        [
            # XML with class without filename
            """<?xml version="1.0" ?>
<coverage version="7.3.2">
    <packages>
        <package name="src">
            <classes>
                <class name="module1.py">
                    <lines>
                        <line hits="1" number="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>""",
            # XML with class without lines
            """<?xml version="1.0" ?>
<coverage version="7.3.2">
    <packages>
        <package name="src">
            <classes>
                <class filename="src/module1.py" name="module1.py">
                    <methods/>
                </class>
            </classes>
        </package>
    </packages>
</coverage>""",
        ],
    )
    def test_parse_xml_missing_data(self, parser: XMLCoverageParser, xml_content: str) -> None:
        """Test parsing XML with missing data."""
        report = parser.parse(xml_content)

        assert isinstance(report, CoverageReport)
        assert len(report.files) == 0

    @pytest.mark.parametrize(
        "hits,expected_covered",
        [
            ("0", 0),
            ("1", 1),
            ("5", 1),
            ("100", 1),
        ],
    )
    def test_parse_line_hits(self, parser: XMLCoverageParser, hits: str, expected_covered: int) -> None:
        """Test parsing different line hit values."""
        xml_content = f"""<?xml version="1.0" ?>
<coverage version="7.3.2">
    <packages>
        <package name="src">
            <classes>
                <class filename="src/test.py" name="test.py">
                    <lines>
                        <line hits="{hits}" number="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""

        report = parser.parse(xml_content)
        assert len(report.files) == 1
        assert report.files[0].covered_lines == expected_covered

    def test_parse_hierarchical(self, parser: XMLCoverageParser, valid_xml: str) -> None:
        """Test parsing into hierarchical structure."""
        hierarchical_report = parser.parse_hierarchical(valid_xml)

        assert isinstance(hierarchical_report, HierarchicalCoverageReport)
        assert isinstance(hierarchical_report.root, DirectoryNode)

        # Check root
        root = hierarchical_report.root
        assert root.name == "src"
        assert root.path == "src"
        assert len(root.children) == 2

        # Check children
        for child in root.children:
            assert isinstance(child, FileNode)
            assert child.name in ["module1.py", "module2.py"]

    def test_parse_hierarchical_empty(self, parser: XMLCoverageParser, empty_xml: str) -> None:
        """Test parsing empty XML into hierarchical structure."""
        hierarchical_report = parser.parse_hierarchical(empty_xml)

        assert isinstance(hierarchical_report, HierarchicalCoverageReport)
        assert isinstance(hierarchical_report.root, DirectoryNode)
        assert hierarchical_report.root.name == ""
        assert hierarchical_report.root.path == ""
        assert len(hierarchical_report.root.children) == 0

    def test_parse_hierarchical_complex_structure(self, parser: XMLCoverageParser) -> None:
        """Test parsing complex directory structure."""
        xml_content = """<?xml version="1.0" ?>
<coverage version="7.3.2">
    <packages>
        <package name="src">
            <classes>
                <class filename="src/module1.py" name="module1.py">
                    <lines>
                        <line hits="1" number="1"/>
                    </lines>
                </class>
                <class filename="src/subdir/module2.py" name="module2.py">
                    <lines>
                        <line hits="1" number="1"/>
                    </lines>
                </class>
                <class filename="src/subdir/subsubdir/module3.py" name="module3.py">
                    <lines>
                        <line hits="1" number="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""

        hierarchical_report = parser.parse_hierarchical(xml_content)
        root = hierarchical_report.root

        # Check structure
        assert root.name == "src"
        assert len(root.children) == 2  # module1.py and subdir/

        # Find subdir
        subdir = next(child for child in root.children if isinstance(child, DirectoryNode))
        assert subdir.name == "subdir"
        assert len(subdir.children) == 2  # module2.py and subsubdir/

        # Find subsubdir
        subsubdir = next(child for child in subdir.children if isinstance(child, DirectoryNode))
        assert subsubdir.name == "subsubdir"
        assert len(subsubdir.children) == 1  # module3.py

    def test_find_common_root_empty(self, parser: XMLCoverageParser) -> None:
        """Test finding common root with empty list."""
        result = parser._find_common_root([])
        assert result == ""

    def test_find_common_root_single_file(self, parser: XMLCoverageParser) -> None:
        """Test finding common root with single file."""
        result = parser._find_common_root(["src/module.py"])
        assert result == "src"

    def test_find_common_root_no_common_path_at_start(self, parser: XMLCoverageParser) -> None:
        """Test finding common root when files have no common path from the start."""
        # This should ensure the `if not common_parts:` branch is covered
        result = parser._find_common_root(["file1.py", "file2.py"])
        assert result == ""

        # Another case with different first level directories
        result = parser._find_common_root(["apple/test.py", "banana/test.py"])
        assert result == ""

        # Edge case: files at root level (no directory parts)
        # This should ensure min_parts=1 but paths have only 1 part, forcing loop to run with i=0
        # and different first parts should make common_parts empty
        result = parser._find_common_root(["a.py", "b.py", "c.py"])
        assert result == ""

    def test_find_common_root_empty_paths_edge_case(self, parser: XMLCoverageParser) -> None:
        """Test edge case to ensure coverage of specific branch conditions."""
        # Test case that should hit the specific branch: 167->177
        # This creates a scenario where min_parts > 0, but first comparison fails
        result = parser._find_common_root(["x.py", "y.py"])
        assert result == ""

        # Another edge case with very different first elements
        result = parser._find_common_root(["aaaa.py", "bbbb.py"])
        assert result == ""

        # Edge case: Empty paths should make min_parts = 0, testing the direct path from for to if
        result = parser._find_common_root(["", ""])
        assert result == ""

    @pytest.mark.parametrize(
        "filepaths,expected",
        [
            (["src/module1.py", "src/module2.py"], "src"),
            (["src/sub/module1.py", "src/sub/module2.py"], str(Path("src/sub"))),
            (["src/module1.py", "tests/test1.py"], ""),
            (["a/b/c/d.py", "a/b/e/f.py"], str(Path("a/b"))),
            (["/abs/path/file.py", "/abs/path/other.py"], str(Path("/abs/path"))),
            # Additional test cases for edge cases that might not be covered
            (["module1.py", "module2.py"], ""),
            (["a.py", "b.py"], ""),
            (["foo/bar.py", "baz/qux.py"], ""),
        ],
    )
    def test_find_common_root_multiple_files(
        self, parser: XMLCoverageParser, filepaths: list[str], expected: str
    ) -> None:
        """Test finding common root with multiple files."""
        result = parser._find_common_root(filepaths)
        assert result == expected

    def test_add_file_to_tree(self, parser: XMLCoverageParser) -> None:
        """Test adding file to directory tree."""
        root = DirectoryNode(name="root", path="", children=[])
        directory_map: dict[str, DirectoryNode] = {"": root}
        file_coverage = FileCoverage(filename="src/module.py", total_lines=10, covered_lines=8)

        parser._add_file_to_tree(file_coverage, root, directory_map, "")

        # Check directory was created
        assert len(root.children) == 1
        src_dir = root.children[0]
        assert isinstance(src_dir, DirectoryNode)
        assert src_dir.name == "src"

        # Check file was added
        assert len(src_dir.children) == 1
        file_node = src_dir.children[0]
        assert isinstance(file_node, FileNode)
        assert file_node.name == "module.py"
        assert file_node.file_coverage == file_coverage

    def test_add_file_to_tree_with_common_root(self, parser: XMLCoverageParser) -> None:
        """Test adding file to tree with common root."""
        root = DirectoryNode(name="project", path="project", children=[])
        directory_map: dict[str, DirectoryNode] = {"project": root}
        file_coverage = FileCoverage(filename="project/src/module.py", total_lines=10, covered_lines=8)

        parser._add_file_to_tree(file_coverage, root, directory_map, "project")

        # Check structure
        assert len(root.children) == 1
        src_dir = root.children[0]
        assert isinstance(src_dir, DirectoryNode)  # Type narrowing for mypy
        assert src_dir.name == "src"
        assert len(src_dir.children) == 1
        assert src_dir.children[0].name == "module.py"

    def test_add_file_to_tree_outside_common_root(self, parser: XMLCoverageParser) -> None:
        """Test adding file outside common root."""
        root = DirectoryNode(name="project", path="project", children=[])
        directory_map: dict[str, DirectoryNode] = {"project": root}
        file_coverage = FileCoverage(filename="other/module.py", total_lines=10, covered_lines=8)

        parser._add_file_to_tree(file_coverage, root, directory_map, "project")

        # File should be added with full path
        assert len(root.children) == 1
        other_dir = root.children[0]
        assert other_dir.name == "other"


class TestParseCoverageFile:
    """Test parse_coverage_file function."""

    def test_parse_existing_file(self, tmp_path: Path) -> None:
        """Test parsing existing file."""
        # Create test file
        coverage_file = tmp_path / "coverage.xml"
        coverage_file.write_text(
            """<?xml version="1.0" ?>
<coverage version="7.3.2">
    <packages>
        <package name="src">
            <classes>
                <class filename="src/test.py" name="test.py">
                    <lines>
                        <line hits="1" number="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""
        )

        report = parse_coverage_file(coverage_file)

        assert isinstance(report, CoverageReport)
        assert len(report.files) == 1
        assert report.files[0].filename == "src/test.py"

    def test_parse_nonexistent_file(self, tmp_path: Path) -> None:
        """Test parsing non-existent file."""
        coverage_file = tmp_path / "nonexistent.xml"

        with pytest.raises(FileNotFoundError, match="Coverage file not found"):
            parse_coverage_file(coverage_file)

    def test_parse_file_with_unicode_error(self, tmp_path: Path) -> None:
        """Test parsing file with unicode error."""
        # Create file with invalid encoding
        coverage_file = tmp_path / "bad_encoding.xml"
        coverage_file.write_bytes(b"\xff\xfe Invalid UTF-8")

        with pytest.raises(CoverageParseError) as exc_info:
            parse_coverage_file(coverage_file)

        assert str(coverage_file) in str(exc_info.value)


class TestCoverageParseError:
    """Test CoverageParseError exception."""

    def test_coverage_parse_error_message(self) -> None:
        """Test CoverageParseError message formatting."""
        error = CoverageParseError("test.xml", "Invalid format")
        assert str(error) == "Failed to parse coverage from test.xml: Invalid format"
        assert error.file_path == "test.xml"
        assert error.reason == "Invalid format"


class TestInvalidXMLError:
    """Test InvalidXMLError exception."""

    def test_invalid_xml_error_message(self) -> None:
        """Test InvalidXMLError message."""
        error = InvalidXMLError()
        assert "Invalid XML format" in str(error)


class TestCoverageParserABC:
    """Test CoverageParser abstract base class."""

    def test_cannot_instantiate_abstract_class(self) -> None:
        """Test that abstract base class cannot be instantiated."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            CoverageParser()  # type: ignore[abstract]

    def test_subclass_must_implement_parse(self) -> None:
        """Test that subclass must implement parse method."""

        class IncompletParser(CoverageParser):
            pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompletParser()  # type: ignore[abstract]

    def test_subclass_with_parse_method(self) -> None:
        """Test that subclass with parse method can be instantiated."""

        class CompleteParser(CoverageParser):
            def parse(self, content: str) -> CoverageReport:
                return CoverageReport(files=[])

        parser = CompleteParser()
        assert isinstance(parser, CoverageParser)
