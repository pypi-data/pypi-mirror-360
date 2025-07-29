"""Integration tests for CLI functionality."""

import subprocess
import tempfile
from pathlib import Path

import pytest


class TestCLIIntegration:
    """Integration tests for the CLI installed as a package."""

    def test_cli_help_command(self) -> None:
        """Test that the CLI help command works after installation."""
        result = subprocess.run(
            ["uv", "run", "covmapy", "--help"],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0
        assert "Generate coverage visualization from XML coverage file" in result.stdout
        assert "COVERAGE_FILE is the path to the coverage XML file" in result.stdout
        assert "--output" in result.stdout
        assert "--width" in result.stdout
        assert "--height" in result.stdout
        assert "--colorscale" in result.stdout

    def test_cli_with_sample_coverage_file(self) -> None:
        """Test CLI with a sample coverage file."""
        # Create a minimal sample coverage XML file
        sample_xml = """<?xml version="1.0"?>
<coverage version="7.3.2" timestamp="1701234567890" lines-valid="100" lines-covered="80" line-rate="0.8" branches-valid="20" branches-covered="15" branch-rate="0.75" complexity="0">
    <sources>
        <source>.</source>
    </sources>
    <packages>
        <package name="src.covmapy" line-rate="0.8" branch-rate="0.75" complexity="0">
            <classes>
                <class name="src/covmapy/cli.py" filename="src/covmapy/cli.py" line-rate="0.9" branch-rate="0.8" complexity="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1"/>
                        <line number="2" hits="1"/>
                        <line number="3" hits="1"/>
                        <line number="4" hits="1"/>
                        <line number="5" hits="1"/>
                        <line number="6" hits="0"/>
                        <line number="7" hits="1"/>
                        <line number="8" hits="1"/>
                        <line number="9" hits="1"/>
                        <line number="10" hits="1"/>
                    </lines>
                </class>
                <class name="src/covmapy/core.py" filename="src/covmapy/core.py" line-rate="0.7" branch-rate="0.7" complexity="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1"/>
                        <line number="2" hits="1"/>
                        <line number="3" hits="1"/>
                        <line number="4" hits="0"/>
                        <line number="5" hits="0"/>
                        <line number="6" hits="0"/>
                        <line number="7" hits="1"/>
                        <line number="8" hits="1"/>
                        <line number="9" hits="1"/>
                        <line number="10" hits="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""  # noqa: E501

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create sample coverage file
            coverage_file = Path(tmpdir) / "coverage.xml"
            coverage_file.write_text(sample_xml, encoding="utf-8")

            # Create output file path
            output_file = Path(tmpdir) / "output.html"

            # Run the CLI
            result = subprocess.run(  # noqa: S603
                ["uv", "run", "covmapy", str(coverage_file), "--output", str(output_file)],  # noqa: S607
                capture_output=True,
                text=True,
                check=False,
            )

            # Check command success
            assert result.returncode == 0
            assert "Generating coverage visualization" in result.stdout
            assert "Coverage visualization saved" in result.stdout

            # Check output file exists and has content
            assert output_file.exists()
            html_content = output_file.read_text(encoding="utf-8")
            assert len(html_content) > 0
            assert "<html>" in html_content
            assert "plotly" in html_content.lower()

    def test_cli_with_invalid_coverage_file(self) -> None:
        """Test CLI behavior with non-existent coverage file."""
        result = subprocess.run(
            ["uv", "run", "covmapy", "nonexistent.xml"],  # noqa: S607
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode != 0
        assert "does not exist" in result.stderr or "No such file" in result.stderr

    def test_cli_with_invalid_colorscale(self) -> None:
        """Test CLI behavior with invalid colorscale."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create minimal sample coverage file
            coverage_file = Path(tmpdir) / "coverage.xml"
            coverage_file.write_text(
                """<?xml version="1.0"?>
<coverage version="7.3.2" timestamp="1701234567890" lines-valid="10" lines-covered="8" line-rate="0.8" branches-valid="5" branches-covered="4" branch-rate="0.8" complexity="0">
    <sources><source>.</source></sources>
    <packages>
        <package name="test" line-rate="0.8" branch-rate="0.8" complexity="0">
            <classes>
                <class name="test.py" filename="test.py" line-rate="0.8" branch-rate="0.8" complexity="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1"/>
                        <line number="2" hits="0"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>""",  # noqa: E501
                encoding="utf-8",
            )

            # Test with invalid colorscale
            result = subprocess.run(  # noqa: S603
                ["uv", "run", "covmapy", str(coverage_file), "--colorscale", "InvalidScale"],  # noqa: S607
                capture_output=True,
                text=True,
                check=False,
            )

            assert result.returncode != 0
            assert "InvalidScale" in result.stderr and "is not one of" in result.stderr

    def test_cli_with_various_options(self) -> None:
        """Test CLI with various valid options."""
        sample_xml = """<?xml version="1.0"?>
<coverage version="7.3.2" timestamp="1701234567890" lines-valid="50" lines-covered="40" line-rate="0.8" branches-valid="10" branches-covered="8" branch-rate="0.8" complexity="0">
    <sources><source>.</source></sources>
    <packages>
        <package name="mypackage" line-rate="0.8" branch-rate="0.8" complexity="0">
            <classes>
                <class name="mypackage/module.py" filename="mypackage/module.py" line-rate="0.8" branch-rate="0.8" complexity="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1"/>
                        <line number="2" hits="1"/>
                        <line number="3" hits="0"/>
                        <line number="4" hits="1"/>
                        <line number="5" hits="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""  # noqa: E501

        with tempfile.TemporaryDirectory() as tmpdir:
            coverage_file = Path(tmpdir) / "coverage.xml"
            coverage_file.write_text(sample_xml, encoding="utf-8")

            output_file = Path(tmpdir) / "custom_output.html"

            # Test with custom width, height, and colorscale
            result = subprocess.run(  # noqa: S603
                [  # noqa: S607
                    "uv",
                    "run",
                    "covmapy",
                    str(coverage_file),
                    "--output",
                    str(output_file),
                    "--width",
                    "1200",
                    "--height",
                    "800",
                    "--colorscale",
                    "Viridis",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            assert result.returncode == 0
            assert output_file.exists()

            # Verify the HTML contains the expected content
            html_content = output_file.read_text(encoding="utf-8")
            assert "<html>" in html_content
            assert "1200" in html_content  # Width should be in the HTML
            assert "800" in html_content  # Height should be in the HTML

    @pytest.mark.parametrize(
        "colorscale", ["RdYlGn", "Viridis", "Blues", "Reds", "YlOrRd", "YlGnBu", "RdBu", "Spectral"]
    )
    def test_cli_with_all_supported_colorscales(self, colorscale: str) -> None:
        """Test CLI with all supported colorscales."""
        sample_xml = """<?xml version="1.0"?>
<coverage version="7.3.2" timestamp="1701234567890" lines-valid="25" lines-covered="20" line-rate="0.8" branches-valid="5" branches-covered="4" branch-rate="0.8" complexity="0">
    <sources><source>.</source></sources>
    <packages>
        <package name="testpkg" line-rate="0.8" branch-rate="0.8" complexity="0">
            <classes>
                <class name="testpkg/test.py" filename="testpkg/test.py" line-rate="0.8" branch-rate="0.8" complexity="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1"/>
                        <line number="2" hits="1"/>
                        <line number="3" hits="0"/>
                        <line number="4" hits="1"/>
                        <line number="5" hits="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>"""  # noqa: E501

        with tempfile.TemporaryDirectory() as tmpdir:
            coverage_file = Path(tmpdir) / "coverage.xml"
            coverage_file.write_text(sample_xml, encoding="utf-8")

            output_file = Path(tmpdir) / f"output_{colorscale.lower()}.html"

            result = subprocess.run(  # noqa: S603
                ["uv", "run", "covmapy", str(coverage_file), "--output", str(output_file), "--colorscale", colorscale],  # noqa: S607
                capture_output=True,
                text=True,
                check=False,
            )

            assert result.returncode == 0
            assert output_file.exists()

            html_content = output_file.read_text(encoding="utf-8")
            assert len(html_content) > 0
            assert "<html>" in html_content
