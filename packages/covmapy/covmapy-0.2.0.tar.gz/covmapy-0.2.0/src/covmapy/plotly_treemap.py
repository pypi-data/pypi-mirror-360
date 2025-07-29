"""Plotly-based treemap layout implementation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

import plotly.graph_objects as go  # type: ignore[import-untyped]

from covmapy.constants import DefaultValues, PlotlyConfig
from covmapy.models import DirectoryNode, FileNode, HierarchicalCoverageReport


class PlotlyTreemapLayout:
    """Hierarchical treemap layout using Plotly."""

    def __init__(self, colorscale: str = DefaultValues.COLORSCALE) -> None:
        """Initialize Plotly hierarchical treemap layout.

        Args:
            colorscale: Plotly colorscale name (default: Spectral for rainbow gradient)
        """
        self.colorscale = colorscale

    def generate_figure(
        self,
        hierarchical_report: HierarchicalCoverageReport,
        width: int = PlotlyConfig.DEFAULT_WIDTH,
        height: int = PlotlyConfig.DEFAULT_HEIGHT,
    ) -> go.Figure:
        """Generate hierarchical Plotly treemap figure.

        Args:
            hierarchical_report: Hierarchical coverage report
            width: Figure width in pixels
            height: Figure height in pixels

        Returns:
            Plotly Figure object
        """
        # Prepare hierarchical data for Plotly treemap
        treemap_data = self._prepare_treemap_data(hierarchical_report)

        # Use squarify algorithm with golden ratio for optimal space utilization

        # Create hierarchical treemap
        fig = go.Figure(
            go.Treemap(
                ids=treemap_data.ids,
                labels=treemap_data.labels,
                values=treemap_data.values,
                parents=treemap_data.parents,
                branchvalues="total",
                textinfo="label",
                hovertemplate="%{text}<extra></extra>",
                text=treemap_data.text_info,
                tiling={
                    "packing": PlotlyConfig.TILING_PACKING,
                    "squarifyratio": PlotlyConfig.GOLDEN_RATIO,
                    "pad": PlotlyConfig.TILING_PADDING,
                },
                marker={
                    "colorscale": self.colorscale,
                    "colorbar": {"title": "Coverage %"},
                    "cmid": PlotlyConfig.COVERAGE_MID,
                    "cmin": PlotlyConfig.COVERAGE_MIN,
                    "cmax": PlotlyConfig.COVERAGE_MAX,
                    "line": {"width": PlotlyConfig.BORDER_WIDTH, "color": PlotlyConfig.BORDER_COLOR},
                    "colors": treemap_data.colors,
                },
            )
        )

        # Update layout
        fig.update_layout(
            title={
                "text": PlotlyConfig.DEFAULT_TITLE,
                "x": PlotlyConfig.TITLE_X_POSITION,
                "xanchor": PlotlyConfig.TITLE_X_ANCHOR,
            },
            width=width,
            height=height,
            margin={
                "t": PlotlyConfig.MARGIN_TOP,
                "b": PlotlyConfig.MARGIN_BOTTOM,
                "l": PlotlyConfig.MARGIN_LEFT,
                "r": PlotlyConfig.MARGIN_RIGHT,
            },
            font={"size": PlotlyConfig.FONT_SIZE},
        )

        return fig

    def _prepare_treemap_data(self, hierarchical_report: HierarchicalCoverageReport) -> TreemapData:
        """Prepare data for treemap visualization.

        Args:
            hierarchical_report: Hierarchical coverage report

        Returns:
            TreemapData containing prepared data for visualization
        """
        data = TreemapData()
        self._add_node(hierarchical_report.root, data)
        return data

    def _add_node(
        self,
        node: Union[DirectoryNode, FileNode],
        data: TreemapData,
        parent_id: str = "",
        path_parts: Union[list[str], None] = None,
    ) -> None:
        """Recursively add nodes to the treemap data.

        Args:
            node: Node to add (DirectoryNode or FileNode)
            data: TreemapData to populate
            parent_id: Parent node ID
            path_parts: Current path parts for building unique IDs
        """
        if path_parts is None:
            path_parts = []

        node_name = node.name

        # Create unique ID using full path
        current_path = [*path_parts, node_name]
        unique_id = "/".join(current_path) if current_path[0] != "root" else "/".join(current_path[1:]) or "root"

        data.ids.append(unique_id)
        data.labels.append(node_name)
        data.parents.append(parent_id)

        if isinstance(node, FileNode):
            data.values.append(node.total_lines)
            coverage_percentage = node.coverage_rate * 100
            data.colors.append(coverage_percentage)
            data.text_info.append(
                f"{node_name}<br>Coverage: {coverage_percentage:.1f}%<br>Lines: {node.covered_lines}/{node.total_lines}"
            )
        elif isinstance(node, DirectoryNode):
            if node.total_lines > 0:
                data.values.append(node.total_lines)
                coverage_percentage = node.coverage_rate * 100
                data.colors.append(coverage_percentage)
                data.text_info.append(
                    f"{node_name}<br>"
                    f"Directory<br>"
                    f"Coverage: {coverage_percentage:.1f}%<br>"
                    f"Lines: {node.covered_lines}/{node.total_lines}"
                )
            else:
                data.values.append(PlotlyConfig.EMPTY_DIRECTORY_VALUE)
                data.colors.append(PlotlyConfig.EMPTY_DIRECTORY_COLOR)
                data.text_info.append(f"{node_name}<br>Directory")

            # Add children
            for child in node.children:
                self._add_node(child, data, unique_id, current_path)


@dataclass
class TreemapData:
    """Container for treemap visualization data."""

    ids: list[str]
    labels: list[str]
    values: list[float]
    parents: list[str]
    colors: list[float]
    text_info: list[str]

    def __init__(self) -> None:
        """Initialize empty treemap data."""
        self.ids = []
        self.labels = []
        self.values = []
        self.parents = []
        self.colors = []
        self.text_info = []
