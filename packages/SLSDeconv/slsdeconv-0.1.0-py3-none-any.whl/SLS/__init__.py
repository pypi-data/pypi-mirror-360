# SLS/__init__.py
"""
Spatial Deconvolution Package

A flexible Python package for spatial transcriptomics deconvolution using SVD ridge regression.

The package supports two main deconvolution tasks:

1. CELL-TYPE MAPPING: Map spatial spots to cell type proportions
   - Functions: load_data() → select_optimal_lambda() OR select_optimal_lambda_calsurrogate() → memory_efficient_svd_ridge_regression()
   
2. CELL MAPPING: Map spatial spots to individual cells (for temporal analysis)
   - Functions: load_data() → select_optimal_lambda_mtruncation() → memory_efficient_svd_ridge_regression_cellmap()

Core Functions:
    Data Loading:
        load_data(): Load and preprocess spatial and single-cell data
        load_data_with_time(): Load temporal data and add time information
    
    Lambda Selection (choose appropriate method for your task):
        FOR CELL-TYPE MAPPING:
            select_optimal_lambda(): Standard ridge regression validation
            select_optimal_lambda_calsurrogate(): Efficient surrogate calculation
        FOR CELL MAPPING:
            select_optimal_lambda_mtruncation(): Matrix truncation approach
    
    Deconvolution:
        memory_efficient_svd_ridge_regression(): Cell-type deconvolution (spots → cell types)
        memory_efficient_svd_ridge_regression_cellmap(): Cell mapping (spots → individual cells)
    
    Visualization:
        add_deconvolution_to_adata(): Add results to spatial data
        get_maximum_annotation(): Get dominant annotations
        plot_spatial_deconvolution(): Visualize spatial results

Matrix Utilities:
    split_data(): Split data for validation
    compute_reduced_svd(): SVD decomposition
    create_celltype_matrix(): Cell type aggregation matrix
    aggregate_chunk_by_celltype(): Aggregate by cell type
    apply_nonnegativity_constraint(): Apply constraints and normalization

Additional Visualization Functions:
    plot_deconvolution_heatmap(): Heatmap of proportions
    plot_celltype_proportions(): Bar chart of average proportions
    plot_spatial_feature(): Spatial distribution of specific features
    compare_deconvolution_methods(): Compare multiple methods

Configuration:
    REFERENCE_COLORS: Default color palette
    get_color_palette(): Get color palettes by name
    create_custom_palette(): Create custom color mappings

Optional Pipeline:
    SpatialDeconvolutionPipeline: Convenient wrapper for common workflows

Examples:
    # CELL-TYPE MAPPING workflow
    >>> import SLS as sd
    >>> X, Y, labels = sd.load_data('FinalAnnotation', st_dir='spatial.h5ad', sc_dir='sc.h5ad')
    >>> lambda_opt, _, _ = sd.select_optimal_lambda(X, Y)  # or select_optimal_lambda_calsurrogate(X, Y, labels)
    >>> M_hat, celltypes = sd.memory_efficient_svd_ridge_regression(X, Y, labels, lambda_opt)
    >>> sd.add_deconvolution_to_adata(adata, celltypes, M_hat, 'celltype_deconv')
    
    # CELL MAPPING workflow (for temporal analysis)
    >>> # Filter data to cells/regions of interest first
    >>> lambda_opt, _, _ = sd.select_optimal_lambda_mtruncation(X_filtered, Y_filtered)
    >>> M_temporal = sd.memory_efficient_svd_ridge_regression_cellmap(X_filtered, Y_filtered, lambda_opt)
    >>> sd.add_deconvolution_to_adata(adata_filtered, time_labels, M_temporal, 'temporal_map')
    
    # Memory-efficient processing for large datasets
    >>> sd.memory_efficient_svd_ridge_regression(X, Y, labels, lambda_opt, 
    ...                                         output_dir='./results', chunk_size=1000)
    
    # Optional pipeline for convenience (cell-type mapping only)
    >>> pipeline = sd.SpatialDeconvolutionPipeline()
    >>> M_hat, celltypes, lambda_opt = pipeline.run_celltype_deconvolution(...)
"""

__version__ = "0.1.0"
__author__ = "Yunlu Chen"

# CORE FUNCTIONS - Primary interface for flexible usage
# Data loading functions
from .core.data_loading import (
    load_data,
    load_data_with_time          # For temporal analysis, adds time information
)

# Lambda selection functions - task-specific
from .core.lambda_selection import (
    select_optimal_lambda,                    # For cell-type mapping
    select_optimal_lambda_calsurrogate,      # For cell-type mapping  
    select_optimal_lambda_mtruncation        # For cell mapping ONLY
)

# Deconvolution functions  
from .core.deconvolution import (
    memory_efficient_svd_ridge_regression,      # Cell-type mapping
    memory_efficient_svd_ridge_regression_cellmap  # Cell mapping
)

# UTILITY FUNCTIONS - Supporting functionality
# Matrix operations
from .utils.matrix_operations import (
    split_data,
    compute_reduced_svd,
    create_celltype_matrix,
    aggregate_chunk_by_celltype,
    max_to_one_others_zero,
    normalize_rows,
    apply_nonnegativity_constraint
)

# Visualization functions
from .utils.visualization import (
    add_deconvolution_to_adata,
    get_maximum_annotation,
    plot_spatial_deconvolution,
    plot_deconvolution_heatmap,
    plot_celltype_proportions,
    plot_spatial_feature,
    compare_deconvolution_methods
)

# CONFIGURATION
from .config.colors import (
    REFERENCE_COLORS,
    get_color_palette,
    create_custom_palette
)

# PIPELINE
from .pipeline import (
    SpatialDeconvolutionPipeline,
    quick_celltype_deconvolution
)

# PRIMARY EXPORTS - Functions users will most commonly need
__all__ = [
    # Core deconvolution workflow functions
    "load_data",
    "load_data_with_time", 
    
    # Lambda selection - clearly grouped by task
    "select_optimal_lambda",                  # Cell-type mapping
    "select_optimal_lambda_calsurrogate",    # Cell-type mapping
    "select_optimal_lambda_mtruncation",     # Cell mapping
    
    # Deconvolution functions
    "memory_efficient_svd_ridge_regression",      # Cell-type mapping
    "memory_efficient_svd_ridge_regression_cellmap",  # Cell mapping
    
    # Essential visualization functions
    "add_deconvolution_to_adata",
    "get_maximum_annotation",
    "plot_spatial_deconvolution",
    
    # Matrix utility functions
    "split_data",
    "compute_reduced_svd", 
    "create_celltype_matrix",
    "aggregate_chunk_by_celltype",
    "apply_nonnegativity_constraint",
    
    # Additional visualization functions
    "plot_deconvolution_heatmap",
    "plot_celltype_proportions", 
    "plot_spatial_feature",
    "compare_deconvolution_methods",
    
    # Matrix utilities
    "max_to_one_others_zero",
    "normalize_rows",
    
    # Configuration
    "REFERENCE_COLORS",
    "get_color_palette", 
    "create_custom_palette",
    
    # Convenience function (cell-type mapping only)
    "quick_deconvolution"
]

# Convenience function for cell-type mapping only
def quick_deconvolution(st_dir, sc_dir, celltype_key='FinalAnnotation', n_gene=5000, 
                       lambda_method='standard', save_prefix='deconv'):
    """
    Quick CELL-TYPE deconvolution workflow for rapid prototyping.
    
    This is a convenience function for cell-type mapping only.
    For cell mapping, use individual functions with select_optimal_lambda_mtruncation.
    
    Parameters
    ----------
    st_dir : str
        Path to spatial transcriptomics h5ad file
    sc_dir : str  
        Path to single-cell h5ad file
    celltype_key : str
        Key for cell type annotations
    n_gene : int
        Number of genes to use
    lambda_method : str
        Lambda selection method ('standard' or 'surrogate')
    save_prefix : str
        Prefix for saved plots (just the prefix, not full path)
        
    Returns
    -------
    tuple
        (adata, M_hat, celltypes, optimal_lambda)
        
    Examples
    --------
    >>> # Quick cell-type mapping with standard method
    >>> adata, M_hat, celltypes, lambda_opt = quick_deconvolution(
    ...     'spatial.h5ad', 'sc.h5ad', lambda_method='standard'
    ... )
    
    >>> # Quick cell-type mapping with surrogate method (faster)
    >>> adata, M_hat, celltypes, lambda_opt = quick_deconvolution(
    ...     'spatial.h5ad', 'sc.h5ad', lambda_method='surrogate'
    ... )
    """
    import scanpy as sc
    import os
    
    # Load data
    X, Y, celltype_labels = load_data(celltype_key, n_gene=n_gene, 
                                     st_dir=st_dir, sc_dir=sc_dir)
    
    # Select lambda (only methods appropriate for cell-type mapping)
    if lambda_method == 'standard':
        optimal_lambda, _, _ = select_optimal_lambda(X, Y)
    elif lambda_method == 'surrogate':
        optimal_lambda, _, _ = select_optimal_lambda_calsurrogate(X, Y, celltype_labels)
    else:
        raise ValueError(f"Invalid lambda method for cell-type mapping: {lambda_method}. "
                        f"Use 'standard' or 'surrogate'. For cell mapping, use individual functions.")
    
    # Deconvolve (cell-type mapping)
    M_hat, celltypes = memory_efficient_svd_ridge_regression(X, Y, celltype_labels, optimal_lambda)
    
    # Add to spatial data and visualize
    adata = sc.read_h5ad(st_dir)
    add_deconvolution_to_adata(adata, celltypes, M_hat, 'deconv')
    get_maximum_annotation(adata, 'deconv', 'deconv_max')
    
    # Create output directory for saving plots if it doesn't exist
    save_dir = os.path.dirname(save_prefix) if os.path.dirname(save_prefix) else '.'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
    
    # Plot with proper error handling
    try:
        plot_spatial_deconvolution(adata, 'deconv_max', palette=REFERENCE_COLORS,
                                 save=f'{save_prefix}_spatial.pdf', show=False)
    except Exception as e:
        print(f"Warning: Spatial plot failed: {e}")
    
    # try:
    #     plot_celltype_proportions(adata, 'deconv', save=f'{save_prefix}_proportions.pdf')
    # except Exception as e:
    #     print(f"Warning: Proportions plot failed: {e}")
    
    return adata, M_hat, celltypes, optimal_lambda