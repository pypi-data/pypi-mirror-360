from abc import ABC, abstractmethod

from covmapy.constants import ColorValues, CoverageThresholds


class ColorMapper(ABC):
    """Abstract base class for color mapping strategies."""

    @abstractmethod
    def get_color(self, coverage_rate: float) -> tuple[int, int, int]:
        """Map coverage rate to RGB color.

        Args:
            coverage_rate: Coverage rate between 0.0 and 1.0

        Returns:
            RGB color tuple (r, g, b) with values 0-255
        """


class GradientColorMapper(ColorMapper):
    """Maps coverage rate to color using linear interpolation between two colors."""

    def __init__(
        self,
        low_color: tuple[int, int, int] = ColorValues.RED,  # Red
        high_color: tuple[int, int, int] = ColorValues.GREEN,  # Green
    ) -> None:
        """Initialize color mapper with gradient colors.

        Args:
            low_color: RGB color for 0% coverage (default: red)
            high_color: RGB color for 100% coverage (default: green)
        """
        super().__init__()
        self.low_color = low_color
        self.high_color = high_color

    def get_color(self, coverage_rate: float) -> tuple[int, int, int]:
        """Map coverage rate to color using linear interpolation.

        Args:
            coverage_rate: Coverage rate between 0.0 and 1.0

        Returns:
            RGB color tuple (r, g, b) with values 0-255
        """
        # Clamp coverage rate to valid range
        rate = max(0.0, min(1.0, coverage_rate))

        # Linear interpolation between low_color and high_color
        r = int(self.low_color[0] + (self.high_color[0] - self.low_color[0]) * rate)
        g = int(self.low_color[1] + (self.high_color[1] - self.low_color[1]) * rate)
        b = int(self.low_color[2] + (self.high_color[2] - self.low_color[2]) * rate)

        return (r, g, b)


class ThreeStageColorMapper(ColorMapper):
    """Maps coverage rate to color using three-stage gradient as per architecture."""

    # Coverage thresholds
    LOW_THRESHOLD = CoverageThresholds.LOW_COVERAGE
    HIGH_THRESHOLD = CoverageThresholds.HIGH_COVERAGE

    def __init__(self) -> None:
        """Initialize three-stage color mapper."""
        super().__init__()

    def get_color(self, coverage_rate: float) -> tuple[int, int, int]:
        """Map coverage rate to color using three-stage gradient.

        Stages:
        - 0-30%: red → orange
        - 30-70%: orange → yellow
        - 70-100%: yellow → green

        Args:
            coverage_rate: Coverage rate between 0.0 and 1.0

        Returns:
            RGB color tuple (r, g, b) with values 0-255
        """
        # Clamp coverage rate to valid range
        rate = max(0.0, min(1.0, coverage_rate))

        if rate <= self.LOW_THRESHOLD:
            # Red to orange (0-30%)
            local_rate = rate / self.LOW_THRESHOLD
            r = ColorValues.RGB_MAX_VALUE
            g = int(ColorValues.ORANGE_GREEN_BASE * local_rate)
            b = ColorValues.BLUE_COMPONENT
        elif rate <= self.HIGH_THRESHOLD:
            # Orange to yellow (30-70%)
            local_rate = (rate - self.LOW_THRESHOLD) / (self.HIGH_THRESHOLD - self.LOW_THRESHOLD)
            r = ColorValues.RGB_MAX_VALUE
            g = int(ColorValues.ORANGE_GREEN_BASE + ColorValues.YELLOW_GREEN_OFFSET * local_rate)
            b = ColorValues.BLUE_COMPONENT
        else:
            # Yellow to green (70-100%)
            local_rate = (rate - self.HIGH_THRESHOLD) / (1.0 - self.HIGH_THRESHOLD)
            r = int(ColorValues.RGB_MAX_VALUE * (1 - local_rate))
            g = ColorValues.RGB_MAX_VALUE
            b = ColorValues.BLUE_COMPONENT

        return (r, g, b)
