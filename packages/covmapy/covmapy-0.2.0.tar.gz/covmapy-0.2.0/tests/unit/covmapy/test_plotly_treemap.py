"""Unit tests for Plotly treemap layout module."""

from unittest.mock import Mock

import plotly.graph_objects as go  # type: ignore[import-untyped]
import pytest

from covmapy.models import DirectoryNode, FileCoverage, FileNode, HierarchicalCoverageReport
from covmapy.plotly_treemap import PlotlyTreemapLayout, TreemapData


class TestTreemapData:
    """Test TreemapData class."""

    def test_init(self) -> None:
        """Test TreemapData initialization."""
        data = TreemapData()

        assert data.ids == []
        assert data.labels == []
        assert data.values == []
        assert data.parents == []
        assert data.colors == []
        assert data.text_info == []

    def test_data_modification(self) -> None:
        """Test TreemapData data modification."""
        data = TreemapData()

        # Add test data
        data.ids.append("test_id")
        data.labels.append("test_label")
        data.values.append(10.0)
        data.parents.append("parent_id")
        data.colors.append(75.0)
        data.text_info.append("test info")

        assert len(data.ids) == 1
        assert data.ids[0] == "test_id"
        assert data.labels[0] == "test_label"
        assert data.values[0] == 10.0
        assert data.parents[0] == "parent_id"
        assert data.colors[0] == 75.0
        assert data.text_info[0] == "test info"


class TestPlotlyTreemapLayout:
    """Test PlotlyTreemapLayout class."""

    @pytest.fixture
    def layout(self) -> PlotlyTreemapLayout:
        """Create PlotlyTreemapLayout instance."""
        return PlotlyTreemapLayout()

    @pytest.fixture
    def custom_layout(self) -> PlotlyTreemapLayout:
        """Create PlotlyTreemapLayout with custom colorscale."""
        return PlotlyTreemapLayout(colorscale="Viridis")

    @pytest.fixture
    def simple_hierarchical_report(self) -> HierarchicalCoverageReport:
        """Create simple hierarchical coverage report."""
        root = DirectoryNode(name="root", path="", children=[])
        file_coverage = FileCoverage(filename="test.py", total_lines=10, covered_lines=8)
        file_node = FileNode(name="test.py", path="test.py", file_coverage=file_coverage)
        root.add_child(file_node)
        return HierarchicalCoverageReport(root=root)

    @pytest.fixture
    def complex_hierarchical_report(self) -> HierarchicalCoverageReport:
        """Create complex hierarchical coverage report."""
        # Root directory
        root = DirectoryNode(name="src", path="src", children=[])

        # Add files to root
        file1_coverage = FileCoverage(filename="src/main.py", total_lines=20, covered_lines=15)
        file1_node = FileNode(name="main.py", path="src/main.py", file_coverage=file1_coverage)
        root.add_child(file1_node)

        # Add subdirectory
        subdir = DirectoryNode(name="utils", path="src/utils", children=[])
        file2_coverage = FileCoverage(filename="src/utils/helper.py", total_lines=30, covered_lines=24)
        file2_node = FileNode(name="helper.py", path="src/utils/helper.py", file_coverage=file2_coverage)
        subdir.add_child(file2_node)

        file3_coverage = FileCoverage(filename="src/utils/config.py", total_lines=15, covered_lines=10)
        file3_node = FileNode(name="config.py", path="src/utils/config.py", file_coverage=file3_coverage)
        subdir.add_child(file3_node)

        root.add_child(subdir)

        return HierarchicalCoverageReport(root=root)

    @pytest.fixture
    def empty_hierarchical_report(self) -> HierarchicalCoverageReport:
        """Create empty hierarchical coverage report."""
        root = DirectoryNode(name="empty", path="", children=[])
        return HierarchicalCoverageReport(root=root)

    def test_init_default(self) -> None:
        """Test initialization with default colorscale."""
        layout = PlotlyTreemapLayout()
        assert layout.colorscale == "Spectral"

    def test_init_custom_colorscale(self) -> None:
        """Test initialization with custom colorscale."""
        layout = PlotlyTreemapLayout(colorscale="Viridis")
        assert layout.colorscale == "Viridis"

    def test_generate_figure_returns_plotly_figure(
        self, layout: PlotlyTreemapLayout, simple_hierarchical_report: HierarchicalCoverageReport
    ) -> None:
        """Test that generate_figure returns a Plotly Figure."""
        figure = layout.generate_figure(simple_hierarchical_report)

        assert isinstance(figure, go.Figure)

    def test_generate_figure_with_custom_dimensions(
        self, layout: PlotlyTreemapLayout, simple_hierarchical_report: HierarchicalCoverageReport
    ) -> None:
        """Test generate_figure with custom dimensions."""
        width = 1200
        height = 800

        figure = layout.generate_figure(simple_hierarchical_report, width=width, height=height)

        assert figure.layout.width == width
        assert figure.layout.height == height

    def test_generate_figure_with_custom_colorscale(
        self, custom_layout: PlotlyTreemapLayout, simple_hierarchical_report: HierarchicalCoverageReport
    ) -> None:
        """Test generate_figure with custom colorscale."""
        figure = custom_layout.generate_figure(simple_hierarchical_report)

        # Check that the custom colorscale was used by verifying layout colorscale property
        assert custom_layout.colorscale == "Viridis"

        # The treemap should have a colorscale applied (Plotly converts named colorscales to arrays)
        treemap_data = figure.data[0]
        assert treemap_data.marker.colorscale is not None
        assert len(treemap_data.marker.colorscale) > 0

    def test_generate_figure_simple_structure(
        self, layout: PlotlyTreemapLayout, simple_hierarchical_report: HierarchicalCoverageReport
    ) -> None:
        """Test generate_figure with simple structure."""
        figure = layout.generate_figure(simple_hierarchical_report)

        treemap_data = figure.data[0]

        # Check that we have root and file nodes
        assert len(treemap_data.ids) == 2
        assert "root" in treemap_data.ids
        assert "test.py" in treemap_data.ids

        # Check labels
        assert "root" in treemap_data.labels
        assert "test.py" in treemap_data.labels

        # Check parent relationships
        assert "" in treemap_data.parents  # root has empty parent
        assert "root" in treemap_data.parents  # file has root as parent

    def test_generate_figure_complex_structure(
        self, layout: PlotlyTreemapLayout, complex_hierarchical_report: HierarchicalCoverageReport
    ) -> None:
        """Test generate_figure with complex structure."""
        figure = layout.generate_figure(complex_hierarchical_report)

        treemap_data = figure.data[0]

        # Should have root, subdir, and 3 files
        assert len(treemap_data.ids) == 5

        # Check specific IDs - note the full path structure
        expected_ids = ["src", "src/main.py", "src/utils", "src/utils/helper.py", "src/utils/config.py"]
        for expected_id in expected_ids:
            assert expected_id in treemap_data.ids

        # Check parent relationships
        root_idx = treemap_data.ids.index("src")
        assert treemap_data.parents[root_idx] == ""

        main_idx = treemap_data.ids.index("src/main.py")
        assert treemap_data.parents[main_idx] == "src"

        utils_idx = treemap_data.ids.index("src/utils")
        assert treemap_data.parents[utils_idx] == "src"

        helper_idx = treemap_data.ids.index("src/utils/helper.py")
        assert treemap_data.parents[helper_idx] == "src/utils"

    def test_generate_figure_empty_structure(
        self, layout: PlotlyTreemapLayout, empty_hierarchical_report: HierarchicalCoverageReport
    ) -> None:
        """Test generate_figure with empty structure."""
        figure = layout.generate_figure(empty_hierarchical_report)

        treemap_data = figure.data[0]

        # Should have only root
        assert len(treemap_data.ids) == 1
        assert treemap_data.ids[0] == "empty"
        assert treemap_data.parents[0] == ""

    def test_prepare_treemap_data(
        self, layout: PlotlyTreemapLayout, simple_hierarchical_report: HierarchicalCoverageReport
    ) -> None:
        """Test _prepare_treemap_data method."""
        data = layout._prepare_treemap_data(simple_hierarchical_report)

        assert isinstance(data, TreemapData)
        assert len(data.ids) == 2
        assert len(data.labels) == 2
        assert len(data.values) == 2
        assert len(data.parents) == 2
        assert len(data.colors) == 2
        assert len(data.text_info) == 2

    def test_add_node_file_node(self, layout: PlotlyTreemapLayout) -> None:
        """Test _add_node with FileNode."""
        data = TreemapData()
        file_coverage = FileCoverage(filename="test.py", total_lines=10, covered_lines=8)
        file_node = FileNode(name="test.py", path="test.py", file_coverage=file_coverage)

        layout._add_node(file_node, data)

        assert len(data.ids) == 1
        assert data.ids[0] == "test.py"
        assert data.labels[0] == "test.py"
        assert data.parents[0] == ""
        assert data.values[0] == 10
        assert data.colors[0] == 80.0  # 8/10 * 100
        assert "Coverage: 80.0%" in data.text_info[0]
        assert "Lines: 8/10" in data.text_info[0]

    def test_add_node_directory_node_with_files(self, layout: PlotlyTreemapLayout) -> None:
        """Test _add_node with DirectoryNode containing files."""
        data = TreemapData()

        # Create directory with file
        directory = DirectoryNode(name="src", path="src", children=[])
        file_coverage = FileCoverage(filename="src/test.py", total_lines=20, covered_lines=15)
        file_node = FileNode(name="test.py", path="src/test.py", file_coverage=file_coverage)
        directory.add_child(file_node)

        layout._add_node(directory, data)

        assert len(data.ids) == 2  # directory and file

        # Check directory data
        dir_idx = data.ids.index("src")
        assert data.labels[dir_idx] == "src"
        assert data.values[dir_idx] == 20
        assert data.colors[dir_idx] == 75.0  # 15/20 * 100
        assert "Directory" in data.text_info[dir_idx]
        assert "Coverage: 75.0%" in data.text_info[dir_idx]

    def test_add_node_directory_node_empty(self, layout: PlotlyTreemapLayout) -> None:
        """Test _add_node with empty DirectoryNode."""
        data = TreemapData()
        directory = DirectoryNode(name="empty", path="empty", children=[])

        layout._add_node(directory, data)

        assert len(data.ids) == 1
        assert data.ids[0] == "empty"
        assert data.values[0] == 1  # Default value for empty directory
        assert data.colors[0] == 0  # Default color for empty directory
        assert data.text_info[0] == "empty<br>Directory"

    def test_add_node_directory_node_empty_coverage_check(self, layout: PlotlyTreemapLayout) -> None:
        """Test _add_node with empty DirectoryNode to ensure coverage of empty directory branch."""
        data = TreemapData()
        # Create explicitly empty directory with no children
        directory = DirectoryNode(name="empty_dir", path="empty_dir", children=[])

        # Verify the directory has no total lines
        assert directory.total_lines == 0

        layout._add_node(directory, data)

        # Verify the empty directory branch is taken
        assert len(data.ids) == 1
        assert data.ids[0] == "empty_dir"
        assert data.values[0] == 1  # PlotlyConfig.EMPTY_DIRECTORY_VALUE
        assert data.colors[0] == 0  # PlotlyConfig.EMPTY_DIRECTORY_COLOR
        assert data.text_info[0] == "empty_dir<br>Directory"

    def test_add_node_directory_node_zero_lines_explicit(self, layout: PlotlyTreemapLayout) -> None:
        """Test _add_node with DirectoryNode that explicitly has zero total_lines."""
        data = TreemapData()
        # Create an empty directory that should have total_lines = 0
        directory = DirectoryNode(name="zero_lines", path="zero_lines", children=[])

        # Ensure this directory has no children and therefore total_lines = 0
        assert len(directory.children) == 0
        assert directory.total_lines == 0

        layout._add_node(directory, data)

        # Check that the else branch (node.total_lines == 0) was taken
        assert len(data.ids) == 1
        assert data.ids[0] == "zero_lines"
        assert data.values[0] == 1  # PlotlyConfig.EMPTY_DIRECTORY_VALUE
        assert data.colors[0] == 0  # PlotlyConfig.EMPTY_DIRECTORY_COLOR
        assert data.text_info[0] == "zero_lines<br>Directory"

    def test_add_node_with_invalid_node_type(self, layout: PlotlyTreemapLayout) -> None:
        """Test _add_node with node that is neither FileNode nor DirectoryNode."""

        data = TreemapData()
        # Create a mock object that is neither FileNode nor DirectoryNode
        invalid_node = Mock()
        invalid_node.name = "invalid"

        # This should test the case where neither isinstance condition is true
        # and the function should exit without doing anything
        layout._add_node(invalid_node, data)

        # Basic data should be added but no type-specific values/colors/text_info
        assert len(data.ids) == 1
        assert data.ids[0] == "invalid"
        assert len(data.labels) == 1
        assert data.labels[0] == "invalid"
        assert len(data.parents) == 1
        assert data.parents[0] == ""

        # Type-specific data should not be added
        assert len(data.values) == 0
        assert len(data.colors) == 0
        assert len(data.text_info) == 0

    def test_add_node_with_parent_id(self, layout: PlotlyTreemapLayout) -> None:
        """Test _add_node with parent ID."""
        data = TreemapData()
        file_coverage = FileCoverage(filename="test.py", total_lines=10, covered_lines=8)
        file_node = FileNode(name="test.py", path="test.py", file_coverage=file_coverage)

        layout._add_node(file_node, data, parent_id="parent")

        assert data.parents[0] == "parent"

    def test_add_node_with_path_parts(self, layout: PlotlyTreemapLayout) -> None:
        """Test _add_node with path parts."""
        data = TreemapData()
        file_coverage = FileCoverage(filename="test.py", total_lines=10, covered_lines=8)
        file_node = FileNode(name="test.py", path="test.py", file_coverage=file_coverage)

        layout._add_node(file_node, data, path_parts=["src", "subdir"])

        # ID should include path parts
        assert data.ids[0] == "src/subdir/test.py"

    def test_add_node_root_special_case(self, layout: PlotlyTreemapLayout) -> None:
        """Test _add_node with root special case."""
        data = TreemapData()
        file_coverage = FileCoverage(filename="test.py", total_lines=10, covered_lines=8)
        file_node = FileNode(name="test.py", path="test.py", file_coverage=file_coverage)

        layout._add_node(file_node, data, path_parts=["root"])

        # ID should be just the filename when path starts with "root"
        assert data.ids[0] == "test.py"

    @pytest.mark.parametrize(
        "width,height",
        [
            (800, 600),
            (1024, 768),
            (1200, 800),
            (400, 300),
        ],
    )
    def test_generate_figure_dimensions(
        self,
        layout: PlotlyTreemapLayout,
        simple_hierarchical_report: HierarchicalCoverageReport,
        width: int,
        height: int,
    ) -> None:
        """Test generate_figure with various dimensions."""
        figure = layout.generate_figure(simple_hierarchical_report, width=width, height=height)

        assert figure.layout.width == width
        assert figure.layout.height == height

    def test_figure_layout_properties(
        self, layout: PlotlyTreemapLayout, simple_hierarchical_report: HierarchicalCoverageReport
    ) -> None:
        """Test that figure has expected layout properties."""
        figure = layout.generate_figure(simple_hierarchical_report)

        # Check layout properties
        assert figure.layout.title.text == "Hierarchical Test Coverage Treemap"
        assert figure.layout.title.x == 0.5
        assert figure.layout.title.xanchor == "center"
        assert figure.layout.margin.t == 60
        assert figure.layout.margin.b == 20
        assert figure.layout.margin.l == 20
        assert figure.layout.margin.r == 20
        assert figure.layout.font.size == 12

    def test_treemap_properties(
        self, layout: PlotlyTreemapLayout, simple_hierarchical_report: HierarchicalCoverageReport
    ) -> None:
        """Test that treemap has expected properties."""
        figure = layout.generate_figure(simple_hierarchical_report)

        treemap = figure.data[0]

        # Check treemap properties
        assert treemap.branchvalues == "total"
        assert treemap.textinfo == "label"
        assert treemap.hovertemplate == "%{text}<extra></extra>"

        # Check tiling properties
        assert treemap.tiling.packing == "squarify"
        assert treemap.tiling.squarifyratio == 1.618
        assert treemap.tiling.pad == 2

        # Check marker properties
        assert treemap.marker.colorbar.title.text == "Coverage %"
        assert treemap.marker.cmid == 50
        assert treemap.marker.cmin == 0
        assert treemap.marker.cmax == 100
        assert treemap.marker.line.width == 1
        assert treemap.marker.line.color == "white"

    def test_coverage_calculation_in_text_info(
        self, layout: PlotlyTreemapLayout, simple_hierarchical_report: HierarchicalCoverageReport
    ) -> None:
        """Test that coverage percentages are calculated correctly in text info."""
        figure = layout.generate_figure(simple_hierarchical_report)

        treemap = figure.data[0]

        # Find the file node text info
        file_text_idx = None
        for i, text in enumerate(treemap.text):
            if "Coverage:" in text and "test.py" in text:
                file_text_idx = i
                break

        assert file_text_idx is not None
        file_text = treemap.text[file_text_idx]
        assert "Coverage: 80.0%" in file_text  # 8/10 * 100
        assert "Lines: 8/10" in file_text

    def test_directory_aggregation(
        self, layout: PlotlyTreemapLayout, complex_hierarchical_report: HierarchicalCoverageReport
    ) -> None:
        """Test that directory values and colors are properly aggregated."""
        figure = layout.generate_figure(complex_hierarchical_report)

        treemap = figure.data[0]

        # Find the src directory
        src_idx = treemap.ids.index("src")
        src_value = treemap.values[src_idx]
        src_color = treemap.marker.colors[src_idx]

        # Should aggregate from all files: 20 + 30 + 15 = 65 total lines
        # Covered: 15 + 24 + 10 = 49 covered lines
        # Coverage: 49/65 ≈ 75.38%
        assert src_value == 65
        assert abs(src_color - 75.38461538461539) < 0.001

    def test_unique_id_generation(self, layout: PlotlyTreemapLayout) -> None:
        """Test that unique IDs are generated correctly."""
        data = TreemapData()

        # Test with nested structure
        file_coverage = FileCoverage(filename="test.py", total_lines=10, covered_lines=8)
        file_node = FileNode(name="test.py", path="test.py", file_coverage=file_coverage)

        # Add with different path parts
        layout._add_node(file_node, data, path_parts=["a", "b", "c"])

        assert data.ids[0] == "a/b/c/test.py"

    def test_root_name_handling(self, layout: PlotlyTreemapLayout) -> None:
        """Test proper handling of 'root' in path parts."""
        data = TreemapData()

        file_coverage = FileCoverage(filename="test.py", total_lines=10, covered_lines=8)
        file_node = FileNode(name="test.py", path="test.py", file_coverage=file_coverage)

        # Test root handling
        layout._add_node(file_node, data, path_parts=["root", "src"])

        # When path starts with "root", it should be stripped
        assert data.ids[0] == "src/test.py"

        # Test edge case: only root
        data2 = TreemapData()
        layout._add_node(file_node, data2, path_parts=["root"])
        # When only root, it still creates the filename
        assert data2.ids[0] == "test.py"
