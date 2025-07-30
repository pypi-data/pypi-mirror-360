"""
Core functionality for spatial deconvolution.

This module contains the main computational functions for deconvolution.
All functions can be used independently for maximum flexibility.

The core module supports two main deconvolution tasks:
1. Cell-type mapping: spots → cell type proportions
2. Cell mapping: spots → individual cells (for temporal analysis)
"""

from .data_loading import (
    load_data,
    load_data_with_time
)

from .lambda_selection import (
    select_optimal_lambda,                 # For cell-type mapping
    select_optimal_lambda_calsurrogate,   # For cell-type mapping
    select_optimal_lambda_mtruncation     # For cell mapping ONLY
)

from .deconvolution import (
    memory_efficient_svd_ridge_regression,      # Cell-type mapping
    memory_efficient_svd_ridge_regression_cellmap  # Cell mapping
)

__all__ = [
    # Data loading functions
    "load_data",
    "load_data_with_time",
    
    # Lambda selection functions (task-specific)
    "select_optimal_lambda",                 # Cell-type mapping
    "select_optimal_lambda_calsurrogate",   # Cell-type mapping  
    "select_optimal_lambda_mtruncation",    # Cell mapping
    
    # Deconvolution functions (task-specific)
    "memory_efficient_svd_ridge_regression",      # Cell-type mapping
    "memory_efficient_svd_ridge_regression_cellmap"  # Cell mapping
]
