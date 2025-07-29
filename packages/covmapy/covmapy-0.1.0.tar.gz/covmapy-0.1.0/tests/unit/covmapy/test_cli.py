"""Unit tests for CLI module."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from covmapy.cli import (
    PlotOptions,
    _create_plotter,
    _generate_coverage_plot,
    covmapy,
    main,
)
from covmapy.core import CoveragePlotter, PlotlyCoveragePlotter
from covmapy.exceptions import UnsupportedFormatError
from covmapy.models import OutputFormat
from covmapy.parser import XMLCoverageParser
from covmapy.plotly_treemap import PlotlyTreemapLayout


class TestPlotOptions:
    """Test PlotOptions dataclass."""

    def test_default_values(self) -> None:
        """Test PlotOptions default values."""
        options = PlotOptions()

        assert options.output == "coverage.html"
        assert options.width == 1200
        assert options.height == 800
        assert options.colorscale == "Spectral"
        assert options.format == OutputFormat.HTML.value

    def test_custom_values(self) -> None:
        """Test PlotOptions with custom values."""
        options = PlotOptions(
            output="custom.html",
            width=1024,
            height=768,
            colorscale="Viridis",
            format="html",
        )

        assert options.output == "custom.html"
        assert options.width == 1024
        assert options.height == 768
        assert options.colorscale == "Viridis"
        assert options.format == "html"

    def test_validation_positive_width(self) -> None:
        """Test width validation."""
        with pytest.raises(ValueError, match="width must be positive"):
            PlotOptions(width=0)

        with pytest.raises(ValueError, match="width must be positive"):
            PlotOptions(width=-100)

    def test_validation_positive_height(self) -> None:
        """Test height validation."""
        with pytest.raises(ValueError, match="height must be positive"):
            PlotOptions(height=0)

        with pytest.raises(ValueError, match="height must be positive"):
            PlotOptions(height=-50)

    @pytest.mark.parametrize(
        "invalid_format",
        ["pdf", "png", "json", "svg", "invalid"],
    )
    def test_validation_invalid_format(self, invalid_format: str) -> None:
        """Test format validation with invalid formats."""
        with pytest.raises(ValueError) as exc_info:
            PlotOptions(format=invalid_format)

        assert f"Invalid format: {invalid_format}" in str(exc_info.value)
        assert "Supported formats: 'html'" in str(exc_info.value)

    def test_validation_valid_format(self) -> None:
        """Test format validation with valid format."""
        # Should not raise
        options = PlotOptions(format="html")
        assert options.format == "html"

    @pytest.mark.parametrize(
        "invalid_colorscale",
        ["invalid", "NotAColorscale", "random"],
    )
    def test_validation_invalid_colorscale(self, invalid_colorscale: str) -> None:
        """Test colorscale validation with invalid values."""
        with pytest.raises(ValueError) as exc_info:
            PlotOptions(colorscale=invalid_colorscale)

        assert f"Invalid colorscale: {invalid_colorscale}" in str(exc_info.value)

    @pytest.mark.parametrize(
        "valid_colorscale",
        ["RdYlGn", "Viridis", "Blues", "Reds", "YlOrRd", "YlGnBu", "RdBu", "Spectral"],
    )
    def test_validation_valid_colorscale(self, valid_colorscale: str) -> None:
        """Test colorscale validation with valid values."""
        # Should not raise
        options = PlotOptions(colorscale=valid_colorscale)
        assert options.colorscale == valid_colorscale


class TestCreatePlotter:
    """Test _create_plotter function."""

    def test_create_plotter(self) -> None:
        """Test creating coverage plotter."""
        options = PlotOptions(colorscale="Viridis")
        plotter = _create_plotter(options)

        assert isinstance(plotter, PlotlyCoveragePlotter)
        assert isinstance(plotter.parser, XMLCoverageParser)
        assert isinstance(plotter.layout_engine, PlotlyTreemapLayout)
        assert plotter.layout_engine.colorscale == "Viridis"


class TestGenerateCoveragePlot:
    """Test _generate_coverage_plot function."""

    @pytest.fixture
    def mock_plotter(self) -> Mock:
        """Create mock CoveragePlotter."""
        return Mock(spec=CoveragePlotter)

    @pytest.fixture
    def coverage_file(self, tmp_path: Path) -> Path:
        """Create test coverage file."""
        file_path = tmp_path / "coverage.xml"
        file_path.write_text("<coverage>test</coverage>")
        return file_path

    def test_generate_coverage_plot(
        self,
        coverage_file: Path,
        mock_plotter: Mock,
    ) -> None:
        """Test _generate_coverage_plot with mock plotter."""
        options = PlotOptions(output="test.html", width=1024, height=768, format="html")

        with patch("covmapy.cli.click.echo") as mock_echo:
            _generate_coverage_plot(coverage_file, options, mock_plotter)

        # Verify plotter was called
        mock_plotter.plot_from_file.assert_called_once_with(
            coverage_file,
            "test.html",
            width=1024,
            height=768,
            format_="html",
        )

        # Verify echo calls
        assert mock_echo.call_count == 2
        mock_echo.assert_any_call(f"Generating coverage visualization from {coverage_file}...")
        mock_echo.assert_any_call("Coverage visualization saved to test.html")

    def test_generate_coverage_plot_plotter_error(
        self,
        coverage_file: Path,
        mock_plotter: Mock,
    ) -> None:
        """Test _generate_coverage_plot when plotter raises error."""
        options = PlotOptions()
        mock_plotter.plot_from_file.side_effect = Exception("Plotter error")

        with pytest.raises(Exception, match="Plotter error"):
            _generate_coverage_plot(coverage_file, options, mock_plotter)


class TestCoveragePlotCommand:
    """Test covmapy Click command."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create Click test runner."""
        return CliRunner()

    @pytest.fixture
    def coverage_file(self, tmp_path: Path) -> Path:
        """Create test coverage file."""
        file_path = tmp_path / "coverage.xml"
        file_path.write_text(
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
        return file_path

    def test_coverage_plot_success(self, runner: CliRunner, coverage_file: Path, tmp_path: Path) -> None:
        """Test successful coverage plot generation."""
        output_file = tmp_path / "output.html"

        result = runner.invoke(
            covmapy,
            [str(coverage_file), "--output", str(output_file)],
        )

        assert result.exit_code == 0
        assert "Generating coverage visualization" in result.output
        assert "Coverage visualization saved" in result.output
        assert output_file.exists()

    def test_coverage_plot_nonexistent_file(self, runner: CliRunner) -> None:
        """Test coverage plot with non-existent file."""
        result = runner.invoke(covmapy, ["nonexistent.xml"])

        assert result.exit_code != 0
        # Click should handle the file not found error

    def test_coverage_plot_custom_options(self, runner: CliRunner, coverage_file: Path, tmp_path: Path) -> None:
        """Test coverage plot with custom options."""
        output_file = tmp_path / "custom.html"

        result = runner.invoke(
            covmapy,
            [
                str(coverage_file),
                "--output",
                str(output_file),
                "--width",
                "1024",
                "--height",
                "768",
                "--colorscale",
                "Viridis",
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()

    @pytest.mark.parametrize(
        "width,height",
        [
            ("0", "800"),
            ("-100", "800"),
            ("1200", "0"),
            ("1200", "-50"),
        ],
    )
    def test_coverage_plot_invalid_dimensions(
        self,
        runner: CliRunner,
        coverage_file: Path,
        width: str,
        height: str,
    ) -> None:
        """Test coverage plot with invalid dimensions."""
        result = runner.invoke(
            covmapy,
            [str(coverage_file), "--width", width, "--height", height],
        )

        assert result.exit_code != 0
        assert "Error:" in result.output

    def test_coverage_plot_invalid_colorscale(self, runner: CliRunner, coverage_file: Path) -> None:
        """Test coverage plot with invalid colorscale."""
        result = runner.invoke(
            covmapy,
            [str(coverage_file), "--colorscale", "InvalidColorscale"],
        )

        # This should fail during Click validation, not reach our validation
        assert result.exit_code != 0

    def test_coverage_plot_exception_handling(self, runner: CliRunner, coverage_file: Path) -> None:
        """Test coverage plot exception handling."""
        with patch("covmapy.cli._generate_coverage_plot") as mock_generate:
            mock_generate.side_effect = UnsupportedFormatError("test", ["html"])

            result = runner.invoke(covmapy, [str(coverage_file)])

            assert result.exit_code != 0
            assert "Error:" in result.output

    def test_coverage_plot_short_options(self, runner: CliRunner, coverage_file: Path, tmp_path: Path) -> None:
        """Test coverage plot with short option flags."""
        output_file = tmp_path / "short.html"

        result = runner.invoke(
            covmapy,
            [
                str(coverage_file),
                "-o",
                str(output_file),
                "-w",
                "1200",
                "-h",
                "800",
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_coverage_plot_help(self, runner: CliRunner) -> None:
        """Test coverage plot help output."""
        result = runner.invoke(covmapy, ["--help"])

        assert result.exit_code == 0
        assert "Generate coverage visualization from XML coverage file" in result.output
        assert "--output" in result.output
        assert "--width" in result.output
        assert "--height" in result.output
        assert "--colorscale" in result.output

    def test_coverage_plot_valid_colorscales(self, runner: CliRunner, coverage_file: Path) -> None:
        """Test that all valid colorscales work."""
        valid_colorscales = ["RdYlGn", "Viridis", "Blues", "Reds", "YlOrRd", "YlGnBu", "RdBu", "Spectral"]

        for colorscale in valid_colorscales:
            result = runner.invoke(
                covmapy,
                [str(coverage_file), "--colorscale", colorscale],
            )
            assert result.exit_code == 0, f"Failed with colorscale: {colorscale}"


class TestMainFunction:
    """Test main function."""

    def test_main_calls_coverage_plot(self) -> None:
        """Test that main function calls covmapy."""
        with patch("covmapy.cli.covmapy") as mock_coverage_plot:
            main()
            mock_coverage_plot.assert_called_once()


class TestIntegration:
    """Integration tests for CLI module."""

    def test_end_to_end_workflow(self, tmp_path: Path) -> None:
        """Test complete end-to-end workflow."""
        # Create coverage file
        coverage_file = tmp_path / "coverage.xml"
        coverage_file.write_text(
            """<?xml version="1.0" ?>
<coverage version="7.3.2">
    <packages>
        <package name="src">
            <classes>
                <class filename="src/main.py" name="main.py">
                    <lines>
                        <line hits="1" number="1"/>
                        <line hits="1" number="2"/>
                        <line hits="0" number="3"/>
                    </lines>
                </class>
                <class filename="src/utils.py" name="utils.py">
                    <lines>
                        <line hits="1" number="1"/>
                        <line hits="0" number="2"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""
        )

        output_file = tmp_path / "result.html"
        options = PlotOptions(output=str(output_file), width=1024, height=768, colorscale="Viridis")

        # Create plotter dependencies
        parser = XMLCoverageParser()
        layout_engine = PlotlyTreemapLayout(colorscale=options.colorscale)
        plotter = PlotlyCoveragePlotter(parser, layout_engine)

        # Run the workflow
        _generate_coverage_plot(coverage_file, options, plotter)

        # Verify results
        assert output_file.exists()
        assert output_file.stat().st_size > 0

        # Verify content contains expected HTML structure
        content = output_file.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content or "<html>" in content
        assert "plotly" in content.lower()

    def test_cli_command_integration(self, tmp_path: Path) -> None:
        """Test CLI command integration."""
        # Create test file
        coverage_file = tmp_path / "test.xml"
        coverage_file.write_text(
            """<?xml version="1.0" ?>
<coverage>
    <packages>
        <package name="test">
            <classes>
                <class filename="test.py">
                    <lines>
                        <line hits="1" number="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""
        )

        output_file = tmp_path / "cli_test.html"

        runner = CliRunner()
        result = runner.invoke(
            covmapy,
            [
                str(coverage_file),
                "--output",
                str(output_file),
                "--width",
                "1200",
                "--height",
                "800",
                "--colorscale",
                "RdYlGn",
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()
        assert "saved" in result.output
