# SLS/pipeline.py
"""
Optional pipeline wrapper for spatial transcriptomics deconvolution.

This module provides a convenient pipeline interface for users who want
a streamlined workflow, while still maintaining the flexibility of using
individual functions directly.

The pipeline is OPTIONAL - users can use individual functions for maximum flexibility.
"""

import scanpy as sc
import numpy as np
import gc
from typing import Optional, Tuple, Union, List, Dict, Callable
from .core.data_loading import load_data
from .core.lambda_selection import (
    select_optimal_lambda,
    select_optimal_lambda_calsurrogate,
    select_optimal_lambda_mtruncation
)
from .core.deconvolution import (
    memory_efficient_svd_ridge_regression,
    memory_efficient_svd_ridge_regression_cellmap
)
from .utils.visualization import (
    add_deconvolution_to_adata,
    get_maximum_annotation,
    plot_spatial_deconvolution
)
from .config.colors import REFERENCE_COLORS


class SpatialDeconvolutionPipeline:
    """
    Optional convenience pipeline for spatial transcriptomics deconvolution.
    
    This pipeline provides a streamlined interface for common workflows,
    but users can always use individual functions for maximum flexibility.
    
    The pipeline supports both main deconvolution tasks:
    1. Cell-type mapping: spots → cell type proportions
    2. Cell mapping: spots → individual cells (temporal analysis)
    """
    
    def __init__(self, 
                 celltype_key: str = 'FinalAnnotation',
                 time_key: str = 'palantir_pseudotime',
                 n_gene: int = 5000):
        """
        Initialize the deconvolution pipeline.
        
        Parameters
        ----------
        celltype_key : str
            Key for cell type annotations in single-cell data
        time_key : str
            Key for temporal information (must already exist in single-cell data)
        n_gene : int
            Number of highly variable genes to select
            
        Examples
        --------
        >>> # Initialize with default parameters
        >>> pipeline = SpatialDeconvolutionPipeline()
        
        >>> # Initialize with custom parameters
        >>> pipeline = SpatialDeconvolutionPipeline(
        ...     celltype_key='custom_celltype',
        ...     time_key='custom_pseudotime',
        ...     n_gene=3000
        ... )
        """
        self.celltype_key = celltype_key
        self.time_key = time_key
        self.n_gene = n_gene
        
        # Store results for later use
        self.spatial_data = None
        self.sc_data = None
        self.optimal_lambda = None
        self.deconv_results = None
        self.celltypes = None
        
        print(f"Initialized SpatialDeconvolutionPipeline with:")
        print(f"  - celltype_key: {celltype_key}")
        print(f"  - time_key: {time_key}")
        print(f"  - n_gene: {n_gene}")
        print("\nNote: This pipeline assumes time_key already exists in single-cell data.")
        print("For maximum flexibility, use individual functions directly.")
    
    def run_celltype_deconvolution(self,
                                  st_dir: Optional[str] = None,
                                  sc_dir: Optional[str] = None,
                                  adata: Optional[sc.AnnData] = None,
                                  HHA: Optional[sc.AnnData] = None,
                                  lambda_range: Optional[np.ndarray] = None,
                                  lambda_selection_method: str = 'standard',
                                  output_dir: Optional[str] = None,
                                  chunk_size: Optional[int] = None) -> Tuple[np.ndarray, List[str], float]:
        """
        Run complete cell type deconvolution pipeline.
        
        This is a convenience wrapper. For maximum flexibility, use individual functions:
        load_data() → select_optimal_lambda() → memory_efficient_svd_ridge_regression()
        
        Parameters
        ----------
        st_dir : str, optional
            Path to spatial transcriptomics h5ad file
        sc_dir : str, optional
            Path to single-cell h5ad file
        adata : AnnData, optional
            Pre-loaded spatial data object
        HHA : AnnData, optional
            Pre-loaded single-cell data object
        lambda_range : np.ndarray, optional
            Range of lambda values to test
        lambda_selection_method : str
            Method for lambda selection ('standard' or 'surrogate')
        output_dir : str, optional
            Directory to save chunked results
        chunk_size : int, optional
            Size of chunks for memory-efficient processing
            
        Returns
        -------
        tuple
            (M_hat, unique_celltypes, optimal_lambda)
            
        Examples
        --------
        >>> # Basic usage
        >>> M_hat, celltypes, lambda_opt = pipeline.run_celltype_deconvolution(
        ...     st_dir='spatial.h5ad', 
        ...     sc_dir='sc.h5ad'
        ... )
        
        >>> # With custom parameters
        >>> M_hat, celltypes, lambda_opt = pipeline.run_celltype_deconvolution(
        ...     st_dir='spatial.h5ad',
        ...     sc_dir='sc.h5ad',
        ...     lambda_selection_method='surrogate',
        ...     chunk_size=1000
        ... )
        """
        print('=' * 80)
        print('CELL TYPE DECONVOLUTION PIPELINE')
        print('=' * 80)
        print('Note: You can also use individual functions for more control:')
        print('  load_data() → select_optimal_lambda() → memory_efficient_svd_ridge_regression()')
        
        # Step 1: Load data
        print('\n1. Loading data...')
        X, Y, celltype_labels = load_data(
            self.celltype_key, 
            n_gene=self.n_gene,
            st_dir=st_dir, 
            sc_dir=sc_dir,
            adata=adata, 
            HHA=HHA
        )
        
        # Store data for later use (if loaded from files)
        if adata is None and st_dir is not None:
            self.spatial_data = sc.read_h5ad(st_dir)
        else:
            self.spatial_data = adata
            
        if HHA is None and sc_dir is not None:
            self.sc_data = sc.read_h5ad(sc_dir)
        else:
            self.sc_data = HHA
        
        # Step 2: Select optimal lambda (only appropriate methods for cell-type mapping)
        print('\n2. Selecting optimal lambda for cell-type mapping...')
        if lambda_selection_method == 'standard':
            optimal_lambda, min_R, R_values = select_optimal_lambda(
                X, Y, lambda_range=lambda_range
            )
        elif lambda_selection_method == 'surrogate':
            optimal_lambda, min_R, R_values = select_optimal_lambda_calsurrogate(
                X, Y, celltype_labels, lambda_range=lambda_range
            )
        else:
            raise ValueError(f"Invalid lambda selection method for cell-type mapping: {lambda_selection_method}. "
                           f"Use 'standard' or 'surrogate'. For cell mapping, use run_cell_mapping().")
        
        self.optimal_lambda = optimal_lambda
        print(f'Selected optimal lambda: {optimal_lambda:.6e}')
        
        # Step 3: Perform cell-type deconvolution
        print('\n3. Computing cell type mapping matrix...')
        result = memory_efficient_svd_ridge_regression(
            X, Y, celltype_labels, optimal_lambda,
            output_dir=output_dir, 
            chunk_size=chunk_size
        )
        
        if result is not None:
            M_hat, unique_celltypes = result
            self.deconv_results = M_hat
            self.celltypes = unique_celltypes
            
            print('\n4. Cell-type deconvolution completed successfully!')
            print(f'Deconvolution matrix shape: {M_hat.shape}')
            print(f'Number of cell types: {len(unique_celltypes)}')
            print(f'Cell types: {unique_celltypes}')
            
            return M_hat, unique_celltypes, optimal_lambda
        else:
            print('\n4. Results saved to disk!')
            return None, None, optimal_lambda
    
    def run_cell_mapping(self,
                        type_of_interest: List[str],
                        col_thre: Optional[List[float]] = None,
                        row_thre: Optional[List[float]] = None,
                        spatial_filter_func: Optional[Callable] = None,
                        lambda_range: Optional[np.ndarray] = None,
                        output_dir: Optional[str] = None,
                        chunk_size: Optional[int] = None) -> Union[np.ndarray, None]:
        """
        Run cell mapping deconvolution for temporal analysis.
        
        This assumes the time_key already exists in the single-cell data.
        
        This is a convenience wrapper. For maximum flexibility, use individual functions:
        load_data() → select_optimal_lambda_mtruncation() → memory_efficient_svd_ridge_regression_cellmap()
        
        Parameters
        ----------
        type_of_interest : list
            List of cell types to focus on
        col_thre : list of float, optional
            Column threshold [min_fraction, max_fraction] for filtering.
            E.g., [2/3, 1] means array_col >= (max_col - min_col) * 2/3 
            and array_col <= (max_col - min_col) * 1
        row_thre : list of float, optional
            Row threshold [min_fraction, max_fraction] for filtering.
            E.g., [1/4, 1/3] means array_row >= (max_row - min_row) * (1 - 1/3)
            and array_row <= (max_row - min_row) * (1 - 1/4)
            Note: row coordinates are inverted (larger values = lower part)
        spatial_filter_func : callable, optional
            Custom function to filter spatial spots (overrides col_thre/row_thre)
        lambda_range : np.ndarray, optional
            Range of lambda values to test
        output_dir : str, optional
            Directory to save chunked results
        chunk_size : int, optional
            Size of chunks for memory-efficient processing
            
        Returns
        -------
        np.ndarray or None
            Cell mapping matrix or None if saved to disk
            
        Examples
        --------
        >>> # Basic temporal analysis (right third of tissue)
        >>> M_temporal = pipeline.run_cell_mapping(
        ...     type_of_interest=['Cortex'],
        ...     col_thre=[2/3, 1]
        ... )
        
        >>> # Lower part of tissue
        >>> M_temporal = pipeline.run_cell_mapping(
        ...     type_of_interest=['Cortex'],
        ...     row_thre=[1/4, 1/3]
        ... )
        
        >>> # Custom spatial filtering
        >>> def my_filter(adata):
        ...     # Custom logic here
        ...     return adata.obs[some_condition].index
        >>> M_temporal = pipeline.run_cell_mapping(
        ...     type_of_interest=['Cortex'],
        ...     spatial_filter_func=my_filter
        ... )
        """
        if self.spatial_data is None or self.sc_data is None:
            raise ValueError("Must run run_celltype_deconvolution() first to load data")
        
        # Check if time_key exists in single-cell data
        if self.time_key not in self.sc_data.obs.columns:
            raise ValueError(f"Time key '{self.time_key}' not found in single-cell data. "
                           f"Available columns: {list(self.sc_data.obs.columns)}")
        
        print('=' * 80)
        print('CELL MAPPING PIPELINE - Temporal Analysis')
        print('=' * 80)
        print('Note: You can also use individual functions for more control:')
        print('  load_data() → select_optimal_lambda_mtruncation() → memory_efficient_svd_ridge_regression_cellmap()')
        
        # Step 1: Filter single-cell data by cell types of interest
        print('\n1. Filtering single-cell data by cell types of interest...')
        sc_rows_of_interest = self.sc_data.obs[
            self.sc_data.obs[self.celltype_key].isin(type_of_interest)
        ].index
        HHA_sub = self.sc_data[sc_rows_of_interest, :].copy()
        
        print(f'Filtered single-cell data: {HHA_sub.shape}')
        print(f'Time values available: {HHA_sub.obs[self.time_key].notna().sum()} cells')
        
        # Step 2: Filter spatial data
        print('\n2. Filtering spatial data...')
        if spatial_filter_func is not None:
            # Use custom filter function
            print('Using custom spatial filter function...')
            st_rows_of_interest = spatial_filter_func(self.spatial_data)
        else:
            # Default filter: spots with cell types of interest
            if 'deconv_trunc' not in self.spatial_data.obs.columns:
                print("Warning: No 'deconv_trunc' column found. Please run add_results_to_spatial_data() first.")
                print("Using all spatial spots...")
                condition1 = self.spatial_data.obs.index.isin(self.spatial_data.obs.index)  # All spots
            else:
                condition1 = self.spatial_data.obs['deconv_trunc'].isin(type_of_interest)
            
            # Apply column threshold filter
            if col_thre is not None:
                if 'array_col' not in self.spatial_data.obs.columns:
                    raise ValueError("array_col not found in spatial data, cannot apply col_thre filter")
                
                min_frac, max_frac = col_thre
                max_col = self.spatial_data.obs['array_col'].max()
                min_col = self.spatial_data.obs['array_col'].min()
                col_range = max_col - min_col
                
                min_threshold = min_col + col_range * min_frac
                max_threshold = min_col + col_range * max_frac
                
                condition2 = (self.spatial_data.obs['array_col'] >= min_threshold) & \
                           (self.spatial_data.obs['array_col'] <= max_threshold)
                
                print(f'Column filter: {min_threshold:.1f} <= array_col <= {max_threshold:.1f}')
                condition1 = condition1 & condition2
            
            # Apply row threshold filter  
            if row_thre is not None:
                if 'array_row' not in self.spatial_data.obs.columns:
                    raise ValueError("array_row not found in spatial data, cannot apply row_thre filter")
                
                min_frac, max_frac = row_thre
                max_row = self.spatial_data.obs['array_row'].max()
                min_row = self.spatial_data.obs['array_row'].min()
                row_range = max_row - min_row
                
                # Note: row coordinates are inverted (larger = lower)
                min_threshold = min_row + row_range * (1 - max_frac)  # Inverted
                max_threshold = min_row + row_range * (1 - min_frac)  # Inverted
                
                condition3 = (self.spatial_data.obs['array_row'] >= min_threshold) & \
                           (self.spatial_data.obs['array_row'] <= max_threshold)
                
                print(f'Row filter: {min_threshold:.1f} <= array_row <= {max_threshold:.1f} (inverted coords)')
                condition1 = condition1 & condition3
            
            # Default column filter if no other spatial filters specified
            if col_thre is None and row_thre is None and spatial_filter_func is None:
                if 'array_col' in self.spatial_data.obs.columns:
                    print('Applying default filter: right third of tissue...')
                    max_col = self.spatial_data.obs['array_col'].max()
                    min_col = self.spatial_data.obs['array_col'].min()
                    threshold = min_col + (max_col - min_col) * 2/3  # Right third
                    condition2 = self.spatial_data.obs['array_col'] >= threshold
                    condition1 = condition1 & condition2
                    print(f'Default column filter: array_col >= {threshold:.1f}')
            
            st_rows_of_interest = self.spatial_data.obs[condition1].index
        
        adata_sub = self.spatial_data[st_rows_of_interest, :].copy()
        print(f'Filtered spatial data: {adata_sub.shape}')
        
        # Step 3: Load data for temporal analysis (time_key should already exist)
        print('\n3. Loading data for temporal analysis...')
        X2, Y2, time_labels = load_data(
            self.time_key, 
            adata=adata_sub, 
            HHA=HHA_sub, 
            n_gene=self.n_gene
        )
        
        print(f'Temporal analysis data: X2{X2.shape}, Y2{Y2.shape}')
        print(f'Time label range: [{time_labels.min():.3f}, {time_labels.max():.3f}]')
        
        # Step 4: Select optimal lambda (MUST use mtruncation for cell mapping)
        print('\n4. Selecting optimal lambda for cell mapping...')
        optimal_lambda2, min_R2, R_values2 = select_optimal_lambda_mtruncation(
            X2, Y2, lambda_range=lambda_range
        )
        print(f'Selected optimal lambda for cell mapping: {optimal_lambda2:.6e}')
        
        # Step 5: Perform cell mapping deconvolution
        print('\n5. Computing cell mapping matrix...')
        M_cell_hat = memory_efficient_svd_ridge_regression_cellmap(
            X2, Y2, optimal_lambda2,
            output_dir=output_dir, 
            chunk_size=chunk_size
        )
        
        if M_cell_hat is not None:
            print('\n6. Cell mapping completed successfully!')
            print(f'Cell mapping matrix shape: {M_cell_hat.shape}')
            
            # Add results to spatial data
            add_deconvolution_to_adata(
                adata_sub, time_labels, M_cell_hat, 'temporal_deconv'
            )
            get_maximum_annotation(
                adata_sub, 'temporal_deconv', result_key='temporal_trunc', continuous=True
            )
            
            # Store filtered data for visualization
            self.spatial_data_filtered = adata_sub
            
            return M_cell_hat
        else:
            print('\n6. Cell mapping results saved to disk!')
            return None
    
    def add_results_to_spatial_data(self, result_key: str = 'deconv') -> None:
        """
        Add deconvolution results to spatial data object.
        
        Parameters
        ----------
        result_key : str
            Key to store results in adata.obsm
            
        Examples
        --------
        >>> pipeline.add_results_to_spatial_data('cell_types')
        """
        if self.deconv_results is None or self.celltypes is None:
            raise ValueError("No deconvolution results available. Run run_celltype_deconvolution() first.")
        
        if self.spatial_data is None:
            raise ValueError("No spatial data available.")
        
        add_deconvolution_to_adata(
            self.spatial_data, self.celltypes, self.deconv_results, result_key
        )
        
        get_maximum_annotation(
            self.spatial_data, result_key, result_key + '_trunc'
        )
        
        print(f"Results added to spatial data with key '{result_key}'")
    
    def visualize_results(self, 
                         save_prefix: str = '',
                         palette: Optional[Dict[str, str]] = None) -> None:
        """
        Visualize deconvolution results.
        
        Parameters
        ----------
        save_prefix : str
            Prefix for saved plot filenames
        palette : dict, optional
            Custom color palette
            
        Examples
        --------
        >>> pipeline.visualize_results(save_prefix='my_analysis_')
        """
        if self.spatial_data is None:
            raise ValueError("No spatial data available for visualization")
        
        if palette is None:
            palette = REFERENCE_COLORS
        
        print('\nVisualizing results...')
        
        # Visualize cell type deconvolution
        if 'deconv_trunc' in self.spatial_data.obs.columns:
            print('Plotting cell type deconvolution...')
            filename = f'{save_prefix}celltype_deconv_lambda_{self.optimal_lambda:.6e}.pdf'
            plot_spatial_deconvolution(
                self.spatial_data,
                color_key='deconv_trunc',
                palette=palette,
                save=filename
            )
        
        # Visualize temporal deconvolution if available
        if hasattr(self, 'spatial_data_filtered') and 'temporal_trunc' in self.spatial_data_filtered.obs.columns:
            print('Plotting temporal deconvolution...')
            filename = f'{save_prefix}temporal_deconv.pdf'
            plot_spatial_deconvolution(
                self.spatial_data_filtered,
                color_key='temporal_trunc',
                cmap='turbo',
                save=filename
            )
    
    def get_summary(self) -> Dict[str, any]:
        """
        Get summary of pipeline results.
        
        Returns
        -------
        dict
            Summary information
            
        Examples
        --------
        >>> summary = pipeline.get_summary()
        >>> print(summary)
        """
        summary = {
            'celltype_key': self.celltype_key,
            'time_key': self.time_key,
            'n_gene': self.n_gene,
            'optimal_lambda': self.optimal_lambda,
            'celltypes': self.celltypes,
            'spatial_data_shape': self.spatial_data.shape if self.spatial_data else None,
            'sc_data_shape': self.sc_data.shape if self.sc_data else None,
            'deconv_results_shape': self.deconv_results.shape if self.deconv_results is not None else None,
            'has_temporal_results': hasattr(self, 'spatial_data_filtered'),
            'time_key_available': self.sc_data is not None and self.time_key in self.sc_data.obs.columns if self.sc_data else False
        }
        
        return summary
    
    def reset(self):
        """
        Reset the pipeline state.
        
        Clears all stored data and results, useful for running with different parameters.
        
        Examples
        --------
        >>> pipeline.reset()
        >>> # Now can run with different parameters
        """
        self.spatial_data = None
        self.sc_data = None
        self.optimal_lambda = None
        self.deconv_results = None
        self.celltypes = None
        
        if hasattr(self, 'spatial_data_filtered'):
            delattr(self, 'spatial_data_filtered')
        
        print("Pipeline state reset. Ready for new analysis.")


# Convenience function for quick cell-type deconvolution
def quick_celltype_deconvolution(st_dir: str, 
                                sc_dir: str, 
                                celltype_key: str = 'FinalAnnotation',
                                n_gene: int = 5000,
                                lambda_method: str = 'standard',
                                save_prefix: str = 'deconv') -> Tuple[sc.AnnData, np.ndarray, List[str], float]:
    """
    Quick cell-type deconvolution with visualization.
    
    This is the fastest way to get started, but for more control use individual functions
    or the SpatialDeconvolutionPipeline class.
    
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
        Prefix for saved plots
        
    Returns
    -------
    tuple
        (adata, M_hat, celltypes, optimal_lambda)
        
    Examples
    --------
    >>> # Quickest way to get started
    >>> adata, M_hat, celltypes, lambda_opt = quick_celltype_deconvolution(
    ...     'spatial.h5ad', 'sc.h5ad'
    ... )
    """
    print("Quick cell-type deconvolution")
    print("For more control, use individual functions or SpatialDeconvolutionPipeline")
    
    # Use the existing quick_deconvolution function from __init__.py
    # This avoids code duplication
    from . import quick_deconvolution
    
    return quick_deconvolution(
        st_dir=st_dir,
        sc_dir=sc_dir,
        celltype_key=celltype_key,
        n_gene=n_gene,
        lambda_method=lambda_method,
        save_prefix=save_prefix
    )