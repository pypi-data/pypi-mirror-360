from pathlib import Path
from typing import Protocol

from covmapy.constants import DefaultValues
from covmapy.exceptions import UnsupportedFormatError
from covmapy.models import OutputFormat
from covmapy.parser import XMLCoverageParser
from covmapy.plotly_treemap import PlotlyTreemapLayout


class CoveragePlotter(Protocol):
    """Protocol for coverage visualization plotters."""

    def plot(
        self,
        coverage_xml: str,
        output_path: str,
        *,
        width: int = DefaultValues.WIDTH,
        height: int = DefaultValues.HEIGHT,
        format_: str = DefaultValues.FORMAT,
    ) -> None:
        """Generate coverage visualization plot.

        Args:
            coverage_xml: Coverage data as XML string
            output_path: Path to save the output file
            width: Figure width in pixels
            height: Figure height in pixels
            format_: Output format
        """

    def plot_from_file(
        self,
        coverage_file: Path,
        output_path: str,
        *,
        width: int = DefaultValues.WIDTH,
        height: int = DefaultValues.HEIGHT,
        format_: str = DefaultValues.FORMAT,
    ) -> None:
        """Generate coverage visualization from file.

        Args:
            coverage_file: Path to coverage XML file
            output_path: Path to save the output file
            width: Figure width in pixels
            height: Figure height in pixels
            format_: Output format
        """


class PlotlyCoveragePlotter:
    """Plotly-based interface for generating coverage visualizations."""

    def __init__(
        self,
        parser: XMLCoverageParser,
        layout_engine: PlotlyTreemapLayout,
    ) -> None:
        """Initialize Plotly coverage plotter with dependencies.

        Args:
            parser: XML coverage data parser
            layout_engine: Plotly treemap layout engine
        """
        self.parser = parser
        self.layout_engine = layout_engine

    def plot(
        self,
        coverage_xml: str,
        output_path: str,
        *,
        width: int = DefaultValues.WIDTH,
        height: int = DefaultValues.HEIGHT,
        format_: str = DefaultValues.FORMAT,
    ) -> None:
        """Generate Plotly coverage visualization plot.

        Args:
            coverage_xml: Coverage data as XML string
            output_path: Path to save the output file
            width: Figure width in pixels
            height: Figure height in pixels
            format_: Output format (only 'html' is supported)
        """
        # Parse coverage data into hierarchical structure
        hierarchical_report = self.parser.parse_hierarchical(coverage_xml)

        # Generate Plotly figure
        figure = self.layout_engine.generate_figure(hierarchical_report, width, height)

        # Save figure
        try:
            output_format = OutputFormat(format_.lower())
            if output_format == OutputFormat.HTML:
                figure.write_html(output_path)
            else:
                raise NotImplementedError(f"Format '{format_}' is not yet implemented")
        except ValueError as err:
            raise UnsupportedFormatError(format_, OutputFormat.get_supported_formats()) from err

    def plot_from_file(
        self,
        coverage_file: Path,
        output_path: str,
        *,
        width: int = DefaultValues.WIDTH,
        height: int = DefaultValues.HEIGHT,
        format_: str = DefaultValues.FORMAT,
    ) -> None:
        """Generate Plotly coverage visualization from file.

        Args:
            coverage_file: Path to coverage XML file
            output_path: Path to save the output file
            width: Figure width in pixels
            height: Figure height in pixels
            format: Output format (only 'html' is supported)
        """
        coverage_xml = coverage_file.read_text(encoding="utf-8")
        self.plot(coverage_xml, output_path, width=width, height=height, format_=format_)
