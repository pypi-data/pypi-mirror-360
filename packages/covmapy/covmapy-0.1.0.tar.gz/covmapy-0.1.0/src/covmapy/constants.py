"""Constants for coverage plot configuration and visualization."""

from typing import Final


class PlotlyConfig:
    """Configuration constants for Plotly treemap visualization."""

    # Layout algorithm constants
    GOLDEN_RATIO: Final[float] = 1.618
    TILING_PADDING: Final[int] = 2
    TILING_PACKING: Final[str] = "squarify"

    # Color scale configuration
    COVERAGE_MIN: Final[int] = 0
    COVERAGE_MID: Final[int] = 50
    COVERAGE_MAX: Final[int] = 100

    # Visual styling
    BORDER_WIDTH: Final[int] = 1
    BORDER_COLOR: Final[str] = "white"
    FONT_SIZE: Final[int] = 12

    # Layout margins
    MARGIN_TOP: Final[int] = 60
    MARGIN_BOTTOM: Final[int] = 20
    MARGIN_LEFT: Final[int] = 20
    MARGIN_RIGHT: Final[int] = 20

    # Title configuration
    TITLE_X_POSITION: Final[float] = 0.5
    TITLE_X_ANCHOR: Final[str] = "center"
    DEFAULT_TITLE: Final[str] = "Hierarchical Test Coverage Treemap"

    # Default dimensions
    DEFAULT_WIDTH: Final[int] = 1200
    DEFAULT_HEIGHT: Final[int] = 800

    # Empty directory defaults
    EMPTY_DIRECTORY_VALUE: Final[int] = 1
    EMPTY_DIRECTORY_COLOR: Final[int] = 0


class CoverageThresholds:
    """Coverage rate thresholds for color mapping."""

    LOW_COVERAGE: Final[float] = 0.3
    HIGH_COVERAGE: Final[float] = 0.7


class ColorValues:
    """RGB color values for gradient color mapping."""

    # Basic gradient colors
    RED: Final[tuple[int, int, int]] = (255, 0, 0)
    GREEN: Final[tuple[int, int, int]] = (0, 255, 0)

    # RGB component limits
    RGB_MAX_VALUE: Final[int] = 255

    # Three-stage gradient colors
    ORANGE_RED: Final[int] = 255
    ORANGE_GREEN_BASE: Final[int] = 128
    ORANGE_GREEN_FULL: Final[int] = 255
    YELLOW_GREEN_OFFSET: Final[int] = 127
    BLUE_COMPONENT: Final[int] = 0


class SupportedColorscales:
    """Supported Plotly colorscales for treemap visualization."""

    SCALES: Final[list[str]] = [
        "RdYlGn",
        "Viridis",
        "Blues",
        "Reds",
        "YlOrRd",
        "YlGnBu",
        "RdBu",
        "Spectral",
    ]

    DEFAULT: Final[str] = "Spectral"


class DefaultValues:
    """Default values for CLI and configuration."""

    OUTPUT_FILENAME: Final[str] = "coverage.html"
    WIDTH: Final[int] = PlotlyConfig.DEFAULT_WIDTH
    HEIGHT: Final[int] = PlotlyConfig.DEFAULT_HEIGHT
    COLORSCALE: Final[str] = SupportedColorscales.DEFAULT
    FORMAT: Final[str] = "html"
