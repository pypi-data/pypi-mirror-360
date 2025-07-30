"""Visualization module for analysis results.

This module provides comprehensive tools for visualization of analysis results.
"""

from isospec_data_tools.visualization.analysis.cluster_plots import (
    ClusteringPlotter,
)
from isospec_data_tools.visualization.analysis.confounder_plots import ConfounderPlotter
from isospec_data_tools.visualization.analysis.differential_plots import (
    DifferentialExpressionPlotter,
    ModelPlotter,
)
from isospec_data_tools.visualization.analysis.method_plot import (
    CVAnalyzer,
    MethodPlotter,
    PlotStyler,
    SignificanceMarker,
    add_significance_markers,
    compute_cv_by_sample_type,
    # Backward compatibility functions
    plot_cv,
    plot_distribution_by_groups,
)

__all__ = [
    "ConfounderPlotter",
    "DataValidator",
    "PlotHelper",
    "CVAnalyzer",
    "MethodPlotter",
    "SignificanceMarker",
    "PlotStyler",
    "plot_cv",
    "plot_distribution_by_groups",
    "compute_cv_by_sample_type",
    "add_significance_markers",
    "ClusteringPlotter",
    "DifferentialExpressionPlotter",
    "ModelPlotter",
]
