"""Unit tests for coverage core module."""

import contextlib
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import plotly.graph_objects as go  # type: ignore[import-untyped]
import pytest

from covmapy.core import PlotlyCoveragePlotter
from covmapy.exceptions import UnsupportedFormatError
from covmapy.models import (
    DirectoryNode,
    FileCoverage,
    FileNode,
    HierarchicalCoverageReport,
)
from covmapy.parser import XMLCoverageParser
from covmapy.plotly_treemap import PlotlyTreemapLayout


class TestPlotlyCoveragePlotter:
    """Test PlotlyCoveragePlotter class."""

    @pytest.fixture
    def mock_parser(self) -> Mock:
        """Create mock XMLCoverageParser."""
        return Mock(spec=XMLCoverageParser)

    @pytest.fixture
    def mock_layout_engine(self) -> Mock:
        """Create mock PlotlyTreemapLayout."""
        return Mock(spec=PlotlyTreemapLayout)

    @pytest.fixture
    def plotter(self, mock_parser: Mock, mock_layout_engine: Mock) -> PlotlyCoveragePlotter:
        """Create PlotlyCoveragePlotter instance with mocks."""
        return PlotlyCoveragePlotter(mock_parser, mock_layout_engine)

    @pytest.fixture
    def sample_hierarchical_report(self) -> HierarchicalCoverageReport:
        """Create sample hierarchical coverage report."""
        root = DirectoryNode(name="src", path="src", children=[])
        file_node = FileNode(
            name="test.py",
            path="src/test.py",
            file_coverage=FileCoverage(filename="src/test.py", total_lines=10, covered_lines=8),
        )
        root.add_child(file_node)
        return HierarchicalCoverageReport(root=root)

    @pytest.fixture
    def mock_figure(self) -> Mock:
        """Create mock Plotly figure."""
        figure = Mock(spec=go.Figure)
        figure.write_html = Mock()
        return figure

    def test_init(self, mock_parser: Mock, mock_layout_engine: Mock) -> None:
        """Test initialization with dependencies."""
        plotter = PlotlyCoveragePlotter(mock_parser, mock_layout_engine)

        assert plotter.parser is mock_parser
        assert plotter.layout_engine is mock_layout_engine

    def test_plot_success(
        self,
        plotter: PlotlyCoveragePlotter,
        mock_parser: Mock,
        mock_layout_engine: Mock,
        sample_hierarchical_report: HierarchicalCoverageReport,
        mock_figure: Mock,
    ) -> None:
        """Test successful plot generation."""
        coverage_xml = "<coverage>test</coverage>"
        output_path = "test_output.html"

        # Setup mocks
        mock_parser.parse_hierarchical.return_value = sample_hierarchical_report
        mock_layout_engine.generate_figure.return_value = mock_figure

        # Execute
        plotter.plot(coverage_xml, output_path)

        # Verify
        mock_parser.parse_hierarchical.assert_called_once_with(coverage_xml)
        mock_layout_engine.generate_figure.assert_called_once_with(sample_hierarchical_report, 1200, 800)
        mock_figure.write_html.assert_called_once_with(output_path)

    def test_plot_with_custom_dimensions(
        self,
        plotter: PlotlyCoveragePlotter,
        mock_parser: Mock,
        mock_layout_engine: Mock,
        sample_hierarchical_report: HierarchicalCoverageReport,
        mock_figure: Mock,
    ) -> None:
        """Test plot generation with custom dimensions."""
        coverage_xml = "<coverage>test</coverage>"
        output_path = "test_output.html"
        width = 1200
        height = 800

        # Setup mocks
        mock_parser.parse_hierarchical.return_value = sample_hierarchical_report
        mock_layout_engine.generate_figure.return_value = mock_figure

        # Execute
        plotter.plot(coverage_xml, output_path, width=width, height=height)

        # Verify
        mock_layout_engine.generate_figure.assert_called_once_with(sample_hierarchical_report, width, height)

    def test_plot_html_format(
        self,
        plotter: PlotlyCoveragePlotter,
        mock_parser: Mock,
        mock_layout_engine: Mock,
        sample_hierarchical_report: HierarchicalCoverageReport,
        mock_figure: Mock,
    ) -> None:
        """Test plot generation with explicit HTML format."""
        coverage_xml = "<coverage>test</coverage>"
        output_path = "test_output.html"

        # Setup mocks
        mock_parser.parse_hierarchical.return_value = sample_hierarchical_report
        mock_layout_engine.generate_figure.return_value = mock_figure

        # Execute
        plotter.plot(coverage_xml, output_path, format_="html")

        # Verify
        mock_figure.write_html.assert_called_once_with(output_path)

    @pytest.mark.parametrize(
        "format_",
        ["pdf", "png", "jpg", "svg", "json"],
    )
    def test_plot_unsupported_format(
        self,
        plotter: PlotlyCoveragePlotter,
        mock_parser: Mock,
        mock_layout_engine: Mock,
        sample_hierarchical_report: HierarchicalCoverageReport,
        mock_figure: Mock,
        format_: str,
    ) -> None:
        """Test plot generation with unsupported formats."""
        coverage_xml = "<coverage>test</coverage>"
        output_path = f"test_output.{format_}"

        # Setup mocks
        mock_parser.parse_hierarchical.return_value = sample_hierarchical_report
        mock_layout_engine.generate_figure.return_value = mock_figure

        # Execute and verify
        with pytest.raises(UnsupportedFormatError) as exc_info:
            plotter.plot(coverage_xml, output_path, format_=format_)

        assert format_ in str(exc_info.value)
        assert "html" in str(exc_info.value)

    def test_plot_invalid_format_enum(
        self,
        plotter: PlotlyCoveragePlotter,
        mock_parser: Mock,
        mock_layout_engine: Mock,
        sample_hierarchical_report: HierarchicalCoverageReport,
        mock_figure: Mock,
    ) -> None:
        """Test plot generation with invalid format that raises ValueError."""
        coverage_xml = "<coverage>test</coverage>"
        output_path = "test_output.xyz"

        # Setup mocks
        mock_parser.parse_hierarchical.return_value = sample_hierarchical_report
        mock_layout_engine.generate_figure.return_value = mock_figure

        # Execute and verify
        with pytest.raises(UnsupportedFormatError) as exc_info:
            plotter.plot(coverage_xml, output_path, format_="xyz")

        assert "xyz" in str(exc_info.value)

    def test_plot_parser_error(
        self,
        plotter: PlotlyCoveragePlotter,
        mock_parser: Mock,
        mock_layout_engine: Mock,
    ) -> None:
        """Test plot generation when parser raises error."""
        coverage_xml = "<invalid>"
        output_path = "test_output.html"

        # Setup mocks
        mock_parser.parse_hierarchical.side_effect = Exception("Parse error")

        # Execute and verify
        with pytest.raises(Exception, match="Parse error"):
            plotter.plot(coverage_xml, output_path)

        mock_layout_engine.generate_figure.assert_not_called()

    def test_plot_layout_engine_error(
        self,
        plotter: PlotlyCoveragePlotter,
        mock_parser: Mock,
        mock_layout_engine: Mock,
        sample_hierarchical_report: HierarchicalCoverageReport,
    ) -> None:
        """Test plot generation when layout engine raises error."""
        coverage_xml = "<coverage>test</coverage>"
        output_path = "test_output.html"

        # Setup mocks
        mock_parser.parse_hierarchical.return_value = sample_hierarchical_report
        mock_layout_engine.generate_figure.side_effect = Exception("Layout error")

        # Execute and verify
        with pytest.raises(Exception, match="Layout error"):
            plotter.plot(coverage_xml, output_path)

    def test_plot_write_error(
        self,
        plotter: PlotlyCoveragePlotter,
        mock_parser: Mock,
        mock_layout_engine: Mock,
        sample_hierarchical_report: HierarchicalCoverageReport,
        mock_figure: Mock,
    ) -> None:
        """Test plot generation when writing file raises error."""
        coverage_xml = "<coverage>test</coverage>"
        output_path = "test_output.html"

        # Setup mocks
        mock_parser.parse_hierarchical.return_value = sample_hierarchical_report
        mock_layout_engine.generate_figure.return_value = mock_figure
        mock_figure.write_html.side_effect = OSError("Write error")

        # Execute and verify
        with pytest.raises(IOError, match="Write error"):
            plotter.plot(coverage_xml, output_path)

    def test_plot_from_file(
        self,
        plotter: PlotlyCoveragePlotter,
        tmp_path: Path,
        mock_parser: Mock,
        mock_layout_engine: Mock,
        sample_hierarchical_report: HierarchicalCoverageReport,
        mock_figure: Mock,
    ) -> None:
        """Test plot generation from file."""
        # Create test file
        coverage_file = tmp_path / "coverage.xml"
        coverage_content = "<coverage>test content</coverage>"
        coverage_file.write_text(coverage_content, encoding="utf-8")
        output_path = str(tmp_path / "output.html")

        # Setup mocks
        mock_parser.parse_hierarchical.return_value = sample_hierarchical_report
        mock_layout_engine.generate_figure.return_value = mock_figure

        # Execute
        plotter.plot_from_file(coverage_file, output_path)

        # Verify
        mock_parser.parse_hierarchical.assert_called_once_with(coverage_content)
        mock_layout_engine.generate_figure.assert_called_once_with(sample_hierarchical_report, 1200, 800)
        mock_figure.write_html.assert_called_once_with(output_path)

    def test_plot_from_file_with_custom_params(
        self,
        plotter: PlotlyCoveragePlotter,
        tmp_path: Path,
        mock_parser: Mock,
        mock_layout_engine: Mock,
        sample_hierarchical_report: HierarchicalCoverageReport,
        mock_figure: Mock,
    ) -> None:
        """Test plot generation from file with custom parameters."""
        # Create test file
        coverage_file = tmp_path / "coverage.xml"
        coverage_file.write_text("<coverage>test</coverage>", encoding="utf-8")
        output_path = str(tmp_path / "output.html")

        # Setup mocks
        mock_parser.parse_hierarchical.return_value = sample_hierarchical_report
        mock_layout_engine.generate_figure.return_value = mock_figure

        # Execute
        plotter.plot_from_file(coverage_file, output_path, width=1024, height=768, format_="html")

        # Verify
        mock_layout_engine.generate_figure.assert_called_once_with(sample_hierarchical_report, 1024, 768)

    def test_plot_from_nonexistent_file(
        self,
        plotter: PlotlyCoveragePlotter,
        tmp_path: Path,
    ) -> None:
        """Test plot generation from non-existent file."""
        coverage_file = tmp_path / "nonexistent.xml"
        output_path = str(tmp_path / "output.html")

        # Execute and verify
        with pytest.raises(FileNotFoundError):
            plotter.plot_from_file(coverage_file, output_path)

    def test_plot_from_file_encoding_error(
        self,
        plotter: PlotlyCoveragePlotter,
        tmp_path: Path,
    ) -> None:
        """Test plot generation from file with encoding error."""
        # Create file with invalid encoding
        coverage_file = tmp_path / "bad_encoding.xml"
        coverage_file.write_bytes(b"\xff\xfe Invalid UTF-8")
        output_path = str(tmp_path / "output.html")

        # Execute and verify
        with pytest.raises(UnicodeDecodeError):
            plotter.plot_from_file(coverage_file, output_path)

    @patch("covmapy.core.OutputFormat")
    def test_plot_output_format_get_supported_formats(
        self,
        mock_output_format_class: MagicMock,
        plotter: PlotlyCoveragePlotter,
        mock_parser: Mock,
        mock_layout_engine: Mock,
        sample_hierarchical_report: HierarchicalCoverageReport,
        mock_figure: Mock,
    ) -> None:
        """Test that get_supported_formats is called when handling unsupported format."""
        coverage_xml = "<coverage>test</coverage>"
        output_path = "test_output.pdf"

        # Setup mocks
        mock_parser.parse_hierarchical.return_value = sample_hierarchical_report
        mock_layout_engine.generate_figure.return_value = mock_figure

        # Make OutputFormat constructor raise ValueError
        mock_output_format_class.side_effect = ValueError("Invalid format")
        mock_output_format_class.get_supported_formats.return_value = ["html"]

        # Execute
        with contextlib.suppress(UnsupportedFormatError):
            plotter.plot(coverage_xml, output_path, format_="pdf")

        # Verify get_supported_formats was called
        mock_output_format_class.get_supported_formats.assert_called()

    def test_integration_with_real_dependencies(self, tmp_path: Path) -> None:
        """Test integration with real parser and layout engine."""
        # Create real dependencies
        parser = XMLCoverageParser()
        layout_engine = PlotlyTreemapLayout()
        plotter = PlotlyCoveragePlotter(parser, layout_engine)

        # Create test XML
        coverage_xml = """<?xml version="1.0" ?>
<coverage version="7.3.2">
    <packages>
        <package name="src">
            <classes>
                <class filename="src/test.py" name="test.py">
                    <lines>
                        <line hits="1" number="1"/>
                        <line hits="0" number="2"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""

        output_path = str(tmp_path / "output.html")

        # Execute - should not raise
        plotter.plot(coverage_xml, output_path)

        # Verify file was created
        assert Path(output_path).exists()
        assert Path(output_path).stat().st_size > 0
