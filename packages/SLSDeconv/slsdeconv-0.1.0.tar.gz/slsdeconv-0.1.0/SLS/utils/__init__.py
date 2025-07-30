"""
Utility functions for spatial deconvolution.

This module contains supporting functions for matrix operations,
visualization, and data processing. All functions are designed
to be used independently or in custom workflows.
"""

from .matrix_operations import (
    split_data,
    compute_reduced_svd,
    create_celltype_matrix,
    aggregate_chunk_by_celltype,
    max_to_one_others_zero,
    normalize_rows,
    apply_nonnegativity_constraint
)

from .visualization import (
    add_deconvolution_to_adata,
    get_maximum_annotation,
    plot_spatial_deconvolution,
    plot_deconvolution_heatmap,
    plot_celltype_proportions,
    plot_spatial_feature,
    compare_deconvolution_methods
)

__all__ = [
    # Matrix operation utilities
    "split_data",
    "compute_reduced_svd",
    "create_celltype_matrix", 
    "aggregate_chunk_by_celltype",
    "max_to_one_others_zero",
    "normalize_rows",
    "apply_nonnegativity_constraint",
    
    # Visualization utilities
    "add_deconvolution_to_adata",
    "get_maximum_annotation",
    "plot_spatial_deconvolution",
    "plot_deconvolution_heatmap",
    "plot_celltype_proportions", 
    "plot_spatial_feature",
    "compare_deconvolution_methods"
]
