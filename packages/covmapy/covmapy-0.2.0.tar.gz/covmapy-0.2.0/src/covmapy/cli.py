from dataclasses import dataclass
from pathlib import Path
from typing import Any

import click

from covmapy.constants import DefaultValues, SupportedColorscales
from covmapy.core import CoveragePlotter, PlotlyCoveragePlotter
from covmapy.models import OutputFormat
from covmapy.parser import XMLCoverageParser
from covmapy.plotly_treemap import PlotlyTreemapLayout


@dataclass
class PlotOptions:
    """Configuration options for coverage plot generation."""

    output: str = DefaultValues.OUTPUT_FILENAME
    width: int = DefaultValues.WIDTH
    height: int = DefaultValues.HEIGHT
    colorscale: str = DefaultValues.COLORSCALE
    format: str = OutputFormat.HTML.value

    def __post_init__(self) -> None:
        """Validate configuration options."""
        if self.width <= 0:
            msg = "width must be positive"
            raise ValueError(msg)
        if self.height <= 0:
            msg = "height must be positive"
            raise ValueError(msg)
        if self.format not in OutputFormat.get_supported_formats():
            supported = ", ".join(f"'{fmt}'" for fmt in OutputFormat.get_supported_formats())
            msg = f"Invalid format: {self.format}. Supported formats: {supported}"
            raise ValueError(msg)
        if self.colorscale not in SupportedColorscales.SCALES:
            msg = f"Invalid colorscale: {self.colorscale}"
            raise ValueError(msg)


def _create_plotter(options: PlotOptions) -> CoveragePlotter:
    """Create coverage plotter with configured dependencies.

    Args:
        options: Plot configuration options

    Returns:
        Configured coverage plotter instance
    """
    parser = XMLCoverageParser()
    layout_engine = PlotlyTreemapLayout(colorscale=options.colorscale)
    return PlotlyCoveragePlotter(parser, layout_engine)


def _generate_coverage_plot(
    coverage_file: Path,
    options: PlotOptions,
    plotter: CoveragePlotter,
) -> None:
    """Internal function to generate coverage visualization.

    Args:
        coverage_file: Path to coverage XML file
        options: Plot configuration options
        plotter: Configured coverage plotter instance
    """

    # Generate visualization
    click.echo(f"Generating coverage visualization from {coverage_file}...")
    plotter.plot_from_file(
        coverage_file,
        options.output,
        width=options.width,
        height=options.height,
        format_=options.format,
    )

    click.echo(f"Coverage visualization saved to {options.output}")


@click.command()
@click.argument("coverage_file", type=click.Path(exists=True, path_type=Path))
@click.option("--output", "-o", default=DefaultValues.OUTPUT_FILENAME, help="Output HTML file path")
@click.option("--width", "-w", default=DefaultValues.WIDTH, type=int, help="Figure width in pixels")
@click.option("--height", "-h", default=DefaultValues.HEIGHT, type=int, help="Figure height in pixels")
@click.option(
    "--colorscale",
    default=DefaultValues.COLORSCALE,
    type=click.Choice(SupportedColorscales.SCALES),
    help="Plotly colorscale for treemap visualization",
)
def covmapy(coverage_file: Path, **kwargs: Any) -> None:
    """Generate coverage visualization from XML coverage file.

    COVERAGE_FILE is the path to the coverage XML file to visualize.
    """
    try:
        # Create options instance from kwargs with validation
        options = PlotOptions(**kwargs)

        # Composition Root: assemble dependencies based on renderer
        plotter = _create_plotter(options)
        _generate_coverage_plot(coverage_file, options, plotter)

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort from e


def main() -> None:
    """Entry point for the CLI application."""
    covmapy()


if __name__ == "__main__":
    main()
