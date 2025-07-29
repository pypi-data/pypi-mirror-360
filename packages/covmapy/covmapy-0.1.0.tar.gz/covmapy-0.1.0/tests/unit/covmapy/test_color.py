import pytest

from covmapy.color import GradientColorMapper, ThreeStageColorMapper
from covmapy.constants import ColorValues


class TestGradientColorMapper:
    """Test GradientColorMapper class."""

    def test_gradient_color_mapper_default_colors(self) -> None:
        """Test mapper with default red to green gradient."""
        mapper = GradientColorMapper()
        assert mapper.low_color == ColorValues.RED
        assert mapper.high_color == ColorValues.GREEN

    def test_gradient_color_mapper_custom_colors(self) -> None:
        """Test mapper with custom colors."""
        low_color = (100, 100, 100)
        high_color = (200, 200, 200)
        mapper = GradientColorMapper(low_color=low_color, high_color=high_color)
        assert mapper.low_color == low_color
        assert mapper.high_color == high_color

    @pytest.mark.parametrize(
        "coverage_rate,expected_color",
        [
            (0.0, ColorValues.RED),
            (1.0, ColorValues.GREEN),
            (0.5, (127, 127, 0)),
            (0.25, (191, 63, 0)),
            (0.75, (63, 191, 0)),
        ],
    )
    def test_gradient_color_mapper_interpolation_default_gradient(
        self, coverage_rate: float, expected_color: tuple[int, int, int]
    ) -> None:
        """Test color interpolation with default gradient."""
        mapper = GradientColorMapper()
        color = mapper.get_color(coverage_rate)
        assert color == expected_color

    @pytest.mark.parametrize("coverage_rate", [-0.5, -0.1, 1.1, 2.0])
    def test_gradient_color_mapper_coverage_rate_clamping(self, coverage_rate: float) -> None:
        """Test that coverage rates are clamped to [0, 1]."""
        mapper = GradientColorMapper()
        color = mapper.get_color(coverage_rate)

        if coverage_rate < 0:
            assert color == ColorValues.RED
        else:
            assert color == ColorValues.GREEN

    def test_gradient_color_mapper_custom_gradient_interpolation(self) -> None:
        """Test interpolation with custom gradient."""
        mapper = GradientColorMapper(low_color=(0, 0, 0), high_color=(100, 200, 255))

        assert mapper.get_color(0.0) == (0, 0, 0)
        assert mapper.get_color(1.0) == (100, 200, 255)
        assert mapper.get_color(0.5) == (50, 100, 127)

    @pytest.mark.parametrize(
        "low_color,high_color",
        [
            ((255, 255, 255), (0, 0, 0)),
            ((100, 50, 200), (200, 100, 50)),
            ((0, 0, 0), (255, 255, 255)),
        ],
    )
    def test_gradient_color_mapper_various_color_gradients(
        self, low_color: tuple[int, int, int], high_color: tuple[int, int, int]
    ) -> None:
        """Test various color gradient combinations."""
        mapper = GradientColorMapper(low_color=low_color, high_color=high_color)

        assert mapper.get_color(0.0) == low_color
        assert mapper.get_color(1.0) == high_color

        mid_r = int(low_color[0] + (high_color[0] - low_color[0]) * 0.5)
        mid_g = int(low_color[1] + (high_color[1] - low_color[1]) * 0.5)
        mid_b = int(low_color[2] + (high_color[2] - low_color[2]) * 0.5)
        assert mapper.get_color(0.5) == (mid_r, mid_g, mid_b)


class TestThreeStageColorMapper:
    """Test ThreeStageColorMapper class."""

    def test_three_stage_color_mapper_thresholds(self) -> None:
        """Test that thresholds are correctly defined."""
        assert ThreeStageColorMapper.LOW_THRESHOLD == 0.3
        assert ThreeStageColorMapper.HIGH_THRESHOLD == 0.7

    @pytest.mark.parametrize(
        "coverage_rate,expected_color",
        [
            (0.0, ColorValues.RED),
            (0.15, (ColorValues.RGB_MAX_VALUE, 64, ColorValues.BLUE_COMPONENT)),
            (0.3, (ColorValues.RGB_MAX_VALUE, ColorValues.ORANGE_GREEN_BASE, ColorValues.BLUE_COMPONENT)),
            (0.5, (ColorValues.RGB_MAX_VALUE, 191, ColorValues.BLUE_COMPONENT)),
            (0.7, (ColorValues.RGB_MAX_VALUE, ColorValues.RGB_MAX_VALUE, ColorValues.BLUE_COMPONENT)),
            (0.85, (ColorValues.YELLOW_GREEN_OFFSET, ColorValues.RGB_MAX_VALUE, ColorValues.BLUE_COMPONENT)),
            (1.0, ColorValues.GREEN),
        ],
    )
    def test_three_stage_color_mapper_gradient(
        self, coverage_rate: float, expected_color: tuple[int, int, int]
    ) -> None:
        """Test three-stage gradient color mapping."""
        mapper = ThreeStageColorMapper()
        color = mapper.get_color(coverage_rate)
        assert color == expected_color

    @pytest.mark.parametrize("coverage_rate", [-0.5, -0.1, 1.1, 2.0])
    def test_three_stage_color_mapper_coverage_rate_clamping(self, coverage_rate: float) -> None:
        """Test that coverage rates are clamped to [0, 1]."""
        mapper = ThreeStageColorMapper()
        color = mapper.get_color(coverage_rate)

        if coverage_rate < 0:
            assert color == ColorValues.RED
        else:
            assert color == ColorValues.GREEN

    def test_three_stage_color_mapper_stage_boundaries(self) -> None:
        """Test color values at stage boundaries."""
        mapper = ThreeStageColorMapper()

        assert mapper.get_color(0.0) == ColorValues.RED
        assert mapper.get_color(0.3) == (
            ColorValues.RGB_MAX_VALUE,
            ColorValues.ORANGE_GREEN_BASE,
            ColorValues.BLUE_COMPONENT,
        )
        assert mapper.get_color(0.7) == (
            ColorValues.RGB_MAX_VALUE,
            ColorValues.RGB_MAX_VALUE,
            ColorValues.BLUE_COMPONENT,
        )
        assert mapper.get_color(1.0) == ColorValues.GREEN

    @pytest.mark.parametrize(
        "rate,stage",
        [
            (0.1, "low"),
            (0.2, "low"),
            (0.29, "low"),
            (0.31, "middle"),
            (0.5, "middle"),
            (0.69, "middle"),
            (0.71, "high"),
            (0.9, "high"),
            (0.99, "high"),
        ],
    )
    def test_three_stage_color_mapper_stage_detection(self, rate: float, stage: str) -> None:
        """Test that rates fall into correct stages."""
        mapper = ThreeStageColorMapper()
        color = mapper.get_color(rate)

        if stage == "low":
            assert color[0] == ColorValues.RGB_MAX_VALUE
            assert ColorValues.BLUE_COMPONENT <= color[1] <= ColorValues.ORANGE_GREEN_BASE
            assert color[2] == ColorValues.BLUE_COMPONENT
        elif stage == "middle":
            assert color[0] == ColorValues.RGB_MAX_VALUE
            assert ColorValues.ORANGE_GREEN_BASE < color[1] < ColorValues.RGB_MAX_VALUE
            assert color[2] == ColorValues.BLUE_COMPONENT
        else:
            assert ColorValues.BLUE_COMPONENT <= color[0] < ColorValues.RGB_MAX_VALUE
            assert color[1] == ColorValues.RGB_MAX_VALUE
            assert color[2] == ColorValues.BLUE_COMPONENT

    def test_three_stage_color_mapper_smooth_transitions(self) -> None:
        """Test that color transitions are smooth between stages within each stage."""
        mapper = ThreeStageColorMapper()

        for i in range(100):
            rate = i / 100.0
            color = mapper.get_color(rate)
            next_color = mapper.get_color(min(1.0, rate + 0.01))

            if 0.3 < rate < 0.7 or rate > 0.7:
                assert abs(color[0] - next_color[0]) <= 10

            assert abs(color[1] - next_color[1]) <= 10
            assert abs(color[2] - next_color[2]) <= 10
