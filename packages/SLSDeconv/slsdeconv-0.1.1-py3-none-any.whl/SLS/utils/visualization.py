"""
Visualization functions for spatial deconvolution results.

These functions handle adding results to AnnData objects and creating plots.
They can be used independently for custom visualization workflows.
"""

import scanpy as sc
import pandas as pd
import numpy as np
import scipy.sparse as sp
import matplotlib.pyplot as plt
from typing import Optional, Union, Dict, Any, List, Tuple
import os

def add_deconvolution_to_adata(adata: sc.AnnData, 
                              celltypes: list, 
                              deconv_matrix: Union[np.ndarray, sp.spmatrix],
                              result_key: str = 'deconv') -> None:
    """
    Add deconvolution results to AnnData object.
    
    Parameters
    ----------
    adata : AnnData
        Spatial data object to modify
    celltypes : list
        List of cell type names (column names)
    deconv_matrix : array-like
        Deconvolution result matrix (spots × cell_types)
    result_key : str
        Key to store results in adata.obsm
        
    Examples
    --------
    >>> # Add cell type deconvolution results
    >>> add_deconvolution_to_adata(adata, celltypes, M_hat, 'cell_types')
    >>> print(adata.obsm['cell_types'].head())
    
    >>> # Add temporal mapping results
    >>> add_deconvolution_to_adata(adata, time_labels, M_temporal, 'temporal')
    """
    # Convert sparse matrix to dense if needed
    if sp.issparse(deconv_matrix):
        matrix_dense = deconv_matrix.toarray()
    else:
        matrix_dense = deconv_matrix
        
    # Validate dimensions
    n_obs, n_features = matrix_dense.shape
    if n_obs != adata.n_obs:
        raise ValueError(f"Number of rows in matrix ({n_obs}) doesn't match "
                       f"number of observations in adata ({adata.n_obs})")
    if len(celltypes) != n_features:
        raise ValueError(f"Number of celltypes ({len(celltypes)}) doesn't match "
                       f"number of columns in matrix ({n_features})")
    
    # Create DataFrame with proper index and columns
    deconv_df = pd.DataFrame(
        data=matrix_dense,
        index=adata.obs.index,
        columns=celltypes
    )
    
    # Set column name for clarity
    deconv_df.columns.name = 'feature'
    
    # Add to adata.obsm
    adata.obsm[result_key] = deconv_df
    
    print(f"Successfully added deconvolution results to adata.obsm['{result_key}']")
    print(f"Shape: {deconv_df.shape}")
    print(f"Features: {celltypes[:5]}..." if len(celltypes) > 5 else f"Features: {celltypes}")

def get_maximum_annotation(adata, obsm_key, result_key=None, continuous=False, feature_values=None):
    if obsm_key not in adata.obsm:
        raise KeyError(f"Key '{obsm_key}' not found in adata.obsm")
        
    obsm = adata.obsm[obsm_key]
    
    # Convert to numpy array if DataFrame
    if hasattr(obsm, 'values'):
        deconv_values = obsm.values
        column_names = getattr(obsm, 'columns', None)
    else:
        deconv_values = obsm
        column_names = None
    
    # Get indices of maximum contributing features for each spot
    max_indices = deconv_values.argmax(axis=1)
    
    if continuous and feature_values is not None:
        # CORRECTED: Map to actual feature values (e.g., pseudotime of contributing cells)
        result_values = feature_values[max_indices]
        result = pd.Series(result_values, index=adata.obs.index, dtype=float)
        
    elif continuous:
        # For continuous data without feature values: use maximum proportion values
        max_values = deconv_values.max(axis=1)
        result = pd.Series(max_values, index=adata.obs.index, dtype=float)
        
    else:
        # For categorical data: use column names (cell types)
        if column_names is not None:
            result_values = column_names[max_indices]
            result = pd.Series(result_values, index=adata.obs.index)
            # Convert to categorical
            result = result.astype(pd.CategoricalDtype(column_names))
        else:
            result = pd.Series(max_indices, index=adata.obs.index)
    
    # Either add to adata.obs or return the Series
    if result_key is not None:
        adata.obs[result_key] = result
        return adata
    else:
        return result

def plot_spatial_deconvolution(adata: sc.AnnData,
                              color_key: str,
                              palette: Optional[Dict[str, str]] = None,
                              img_key: str = "hires",
                              figsize: tuple = (12, 12),
                              save: Optional[str] = None,
                              cmap: Optional[str] = None,
                              show: bool = False,
                              **kwargs) -> plt.Figure:
    """
    Plot spatial deconvolution results.
    
    Parameters
    ----------
    adata : AnnData
        Spatial data object
    color_key : str
        Key in adata.obs to color by
    palette : dict, optional
        Color palette for categorical data
    img_key : str
        Key for background image
    figsize : tuple
        Figure size
    save : str, optional
        Filename to save plot (will be saved in ./figures/ directory)
    cmap : str, optional
        Colormap for continuous data
    show : bool
        Whether to show the plot
    **kwargs
        Additional arguments for sc.pl.spatial
        
    Returns
    -------
    plt.Figure
        Matplotlib figure object
        
    Examples
    --------
    >>> # Plot cell type deconvolution
    >>> plot_spatial_deconvolution(adata, 'dominant_celltype', 
    ...                           palette=REFERENCE_COLORS,
    ...                           save='celltype_spatial.pdf')
    
    >>> # Plot continuous values
    >>> plot_spatial_deconvolution(adata, 'max_pseudotime',
    ...                           cmap='viridis',
    ...                           save='pseudotime_spatial.pdf')
    """
    if color_key not in adata.obs.columns:
        available_keys = list(adata.obs.columns)
        raise KeyError(f"Key '{color_key}' not found in adata.obs. "
                      f"Available keys: {available_keys[:10]}...")
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    
    # Prepare arguments for sc.pl.spatial
    plot_kwargs = {
        'color': color_key,  # Don't wrap in list - scanpy expects string
        'img_key': img_key,
        'ax': ax,
        'show': False,  # Important: don't show automatically
        **kwargs
    }
    
    # Add optional parameters
    if palette is not None:
        plot_kwargs['palette'] = palette
    if cmap is not None:
        plot_kwargs['cmap'] = cmap
    
    # Plot using scanpy
    sc.pl.spatial(adata, **plot_kwargs)
    
    # Handle saving manually if needed
    if save is not None:
        # Create figures directory if it doesn't exist
        figures_dir = 'figures'
        os.makedirs(figures_dir, exist_ok=True)
        
        # Construct full path
        save_path = os.path.join(figures_dir, save)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to: {save_path}")
    
    # Show plot if requested
    if show:
        plt.show()
    
    return fig

def plot_deconvolution_heatmap(adata: sc.AnnData,
                              obsm_key: str,
                              figsize: tuple = (12, 8),
                              cmap: str = 'viridis',
                              save: Optional[str] = None,
                              top_n: Optional[int] = None) -> plt.Figure:
    """
    Plot heatmap of deconvolution proportions.
    
    Parameters
    ----------
    adata : AnnData
        Spatial data object
    obsm_key : str
        Key in adata.obsm containing deconvolution results
    figsize : tuple
        Figure size
    cmap : str
        Colormap
    save : str, optional
        Filename to save plot (will be saved in ./figures/ directory)
    top_n : int, optional
        Show only top N features by mean proportion
        
    Returns
    -------
    plt.Figure
        Matplotlib figure object
        
    Examples
    --------
    >>> # Plot all cell types
    >>> plot_deconvolution_heatmap(adata, 'cell_types')
    
    >>> # Plot top 10 most abundant cell types
    >>> plot_deconvolution_heatmap(adata, 'cell_types', top_n=10, save='heatmap.pdf')
    """
    if obsm_key not in adata.obsm:
        raise KeyError(f"Key '{obsm_key}' not found in adata.obsm")
        
    deconv_data = adata.obsm[obsm_key]
    
    # Select top features if requested
    if top_n is not None:
        mean_props = deconv_data.mean(axis=0).sort_values(ascending=False)
        top_features = mean_props.head(top_n).index
        deconv_data = deconv_data[top_features]
    
    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(deconv_data.T, cmap=cmap, aspect='auto')
    
    ax.set_xlabel('Spots')
    ax.set_ylabel('Features')
    ax.set_yticks(range(len(deconv_data.columns)))
    ax.set_yticklabels(deconv_data.columns)
    
    plt.colorbar(im, ax=ax, label='Proportion')
    plt.tight_layout()
    
    if save is not None:
        # Create figures directory if it doesn't exist
        figures_dir = 'figures'
        os.makedirs(figures_dir, exist_ok=True)
        
        # Construct full path
        save_path = os.path.join(figures_dir, save)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Heatmap saved to: {save_path}")
        
    return fig

def plot_celltype_proportions(adata: sc.AnnData,
                             obsm_key: str,
                             figsize: tuple = (10, 6),
                             save: Optional[str] = None,
                             top_n: Optional[int] = None) -> plt.Figure:
    """
    Plot bar chart of average cell type proportions.
    
    Parameters
    ----------
    adata : AnnData
        Spatial data object
    obsm_key : str
        Key in adata.obsm containing deconvolution results
    figsize : tuple
        Figure size
    save : str, optional
        Filename to save plot (will be saved in ./figures/ directory)
    top_n : int, optional
        Show only top N cell types
        
    Returns
    -------
    plt.Figure
        Matplotlib figure object
        
    Examples
    --------
    >>> # Plot average proportions of all cell types
    >>> plot_celltype_proportions(adata, 'cell_types')
    
    >>> # Focus on most abundant cell types
    >>> plot_celltype_proportions(adata, 'cell_types', top_n=15, save='proportions.pdf')
    """
    if obsm_key not in adata.obsm:
        raise KeyError(f"Key '{obsm_key}' not found in adata.obsm")
        
    deconv_data = adata.obsm[obsm_key]
    mean_proportions = deconv_data.mean(axis=0).sort_values(ascending=False)
    
    if top_n is not None:
        mean_proportions = mean_proportions.head(top_n)
    
    fig, ax = plt.subplots(figsize=figsize)
    bars = ax.bar(range(len(mean_proportions)), mean_proportions.values)
    
    ax.set_xlabel('Features')
    ax.set_ylabel('Average Proportion')
    ax.set_title('Average Feature Proportions')
    ax.set_xticks(range(len(mean_proportions)))
    ax.set_xticklabels(mean_proportions.index, rotation=45, ha='right')
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, mean_proportions.values)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.001,
               f'{value:.3f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    
    if save is not None:
        # Create figures directory if it doesn't exist
        figures_dir = 'figures'
        os.makedirs(figures_dir, exist_ok=True)
        
        # Construct full path
        save_path = os.path.join(figures_dir, save)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Bar chart saved to: {save_path}")
        
    return fig

def plot_spatial_feature(adata: sc.AnnData,
                        obsm_key: str,
                        feature: str,
                        img_key: str = "hires",
                        figsize: tuple = (10, 10),
                        cmap: str = 'viridis',
                        save: Optional[str] = None,
                        show: bool = False,
                        **kwargs) -> plt.Figure:
    """
    Plot spatial distribution of a specific feature.
    
    Parameters
    ----------
    adata : AnnData
        Spatial data object
    obsm_key : str
        Key in adata.obsm containing deconvolution results
    feature : str
        Specific feature to plot
    img_key : str
        Key for background image
    figsize : tuple
        Figure size
    cmap : str
        Colormap
    save : str, optional
        Filename to save plot (will be saved in ./figures/ directory)
    show : bool
        Whether to show the plot
    **kwargs
        Additional arguments for sc.pl.spatial
        
    Returns
    -------
    plt.Figure
        Matplotlib figure object
        
    Examples
    --------
    >>> # Plot spatial distribution of a specific cell type
    >>> plot_spatial_feature(adata, 'cell_types', 'Neuron', save='neuron_spatial.pdf')
    
    >>> # Plot with custom colormap
    >>> plot_spatial_feature(adata, 'cell_types', 'Astrocyte', 
    ...                      cmap='plasma', save='astrocyte_spatial.pdf')
    """
    if obsm_key not in adata.obsm:
        available_keys = list(adata.obsm.keys())
        raise KeyError(f"Key '{obsm_key}' not found in adata.obsm. "
                      f"Available keys: {available_keys}")
    
    deconv_data = adata.obsm[obsm_key]
    if feature not in deconv_data.columns:
        available_features = list(deconv_data.columns)
        raise ValueError(f"Feature '{feature}' not found in deconvolution results. "
                        f"Available features: {available_features}")
    
    # Create a safe temporary key
    temp_key = f'_temp_feature_{feature.replace(" ", "_").replace("/", "_")}'
    
    # Add feature values to obs temporarily
    adata.obs[temp_key] = deconv_data[feature].values
    
    try:
        # Create figure and axis
        fig, ax = plt.subplots(figsize=figsize)
        
        # Prepare arguments for sc.pl.spatial
        plot_kwargs = {
            'color': temp_key,  # Use the temporary key
            'img_key': img_key,
            'ax': ax,
            'cmap': cmap,
            'show': False,  # Important: don't show automatically
            **kwargs
        }
        
        # Plot using scanpy
        sc.pl.spatial(adata, **plot_kwargs)
        
        # Add title to make it clear what feature is plotted
        ax.set_title(f'{feature} (from {obsm_key})', fontsize=14)
        
        # Handle saving manually if needed
        if save is not None:
            # Create figures directory if it doesn't exist
            figures_dir = 'figures'
            os.makedirs(figures_dir, exist_ok=True)
            
            # Construct full path
            save_path = os.path.join(figures_dir, save)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Feature plot saved to: {save_path}")
        
        # Show plot if requested
        if show:
            plt.show()
        
    finally:
        # Clean up temporary column
        if temp_key in adata.obs.columns:
            del adata.obs[temp_key]
    
    return fig

def compare_deconvolution_methods(adata: sc.AnnData,
                                 obsm_keys: List[str],
                                 method_names: Optional[List[str]] = None,
                                 figsize: tuple = (15, 5),
                                 save: Optional[str] = None,
                                 show: bool = False) -> plt.Figure:
    """
    Compare results from multiple deconvolution methods.
    
    Parameters
    ----------
    adata : AnnData
        Spatial data object
    obsm_keys : list
        List of keys in adata.obsm to compare
    method_names : list, optional
        Names for the methods (for plot titles)
    figsize : tuple
        Figure size
    save : str, optional
        Filename to save plot (will be saved in ./figures/ directory)
    show : bool
        Whether to show the plot
        
    Returns
    -------
    plt.Figure
        Matplotlib figure object
        
    Examples
    --------
    >>> # Compare different lambda values
    >>> compare_deconvolution_methods(
    ...     adata, 
    ...     ['deconv_lambda_001', 'deconv_lambda_01', 'deconv_lambda_1'],
    ...     ['λ=0.001', 'λ=0.01', 'λ=0.1'],
    ...     save='lambda_comparison.pdf'
    ... )
    """
    n_methods = len(obsm_keys)
    if method_names is None:
        method_names = obsm_keys
    
    if len(method_names) != n_methods:
        raise ValueError(f"Number of method names ({len(method_names)}) must match "
                        f"number of obsm keys ({n_methods})")
    
    # Create subplots
    fig, axes = plt.subplots(1, n_methods, figsize=figsize)
    if n_methods == 1:
        axes = [axes]
    
    temp_keys = []  # Track temporary keys for cleanup
    
    try:
        for i, (obsm_key, method_name) in enumerate(zip(obsm_keys, method_names)):
            if obsm_key not in adata.obsm:
                print(f"Warning: Key '{obsm_key}' not found in adata.obsm, skipping...")
                axes[i].text(0.5, 0.5, f"Data not found:\n{obsm_key}", 
                           ha='center', va='center', transform=axes[i].transAxes)
                axes[i].set_title(method_name)
                continue
            
            # Get dominant annotation for this method
            max_annotation = get_maximum_annotation(adata, obsm_key)
            
            # Create temporary key
            temp_key = f'_temp_comparison_{i}'
            temp_keys.append(temp_key)
            adata.obs[temp_key] = max_annotation
            
            # Plot on the specific axis
            try:
                sc.pl.spatial(adata, color=temp_key, ax=axes[i], 
                             img_key="hires", show=False)
                axes[i].set_title(method_name)
            except Exception as e:
                print(f"Warning: Failed to plot method {i} ({method_name}): {e}")
                axes[i].text(0.5, 0.5, f"Plot failed:\n{str(e)[:50]}...", 
                           ha='center', va='center', transform=axes[i].transAxes)
                axes[i].set_title(f"{method_name} (failed)")
        
        plt.tight_layout()
        
        # Handle saving
        if save is not None:
            # Create figures directory if it doesn't exist
            figures_dir = 'figures'
            os.makedirs(figures_dir, exist_ok=True)
            
            # Construct full path
            save_path = os.path.join(figures_dir, save)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Comparison plot saved to: {save_path}")
        
        # Show plot if requested
        if show:
            plt.show()
    
    finally:
        # Clean up all temporary columns
        for temp_key in temp_keys:
            if temp_key in adata.obs.columns:
                del adata.obs[temp_key]
    
    return fig

def plot_gene_expression_spatial(adata: sc.AnnData,
                                gene: str,
                                img_key: str = "hires",
                                figsize: tuple = (10, 10),
                                cmap: str = 'viridis',
                                save: Optional[str] = None,
                                **kwargs) -> plt.Figure:
    """
    Plot spatial distribution of gene expression.
    
    Parameters
    ----------
    adata : AnnData
        Spatial data object
    gene : str
        Gene name to plot
    img_key : str
        Key for background image
    figsize : tuple
        Figure size
    cmap : str
        Colormap
    save : str, optional
        Filename to save plot (will be saved in ./figures/ directory)
    **kwargs
        Additional arguments for sc.pl.spatial
        
    Returns
    -------
    plt.Figure
        Matplotlib figure object
    """
    if gene not in adata.var_names:
        available_genes = adata.var_names[:10].tolist()
        raise ValueError(f"Gene '{gene}' not found. "
                        f"Available genes (first 10): {available_genes}")
    
    fig, ax = plt.subplots(figsize=figsize)
    
    plot_kwargs = {
        'color': [gene],
        'img_key': img_key,
        'ax': ax,
        'cmap': cmap,
        'show': False,  # Don't show automatically
        **kwargs
    }
    
    # Plot using scanpy
    sc.pl.spatial(adata, **plot_kwargs)
    
    # Handle saving manually if needed
    if save is not None:
        # Create figures directory if it doesn't exist
        figures_dir = 'figures'
        os.makedirs(figures_dir, exist_ok=True)
        
        # Construct full path
        save_path = os.path.join(figures_dir, save)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Gene expression plot saved to: {save_path}")
    
    return fig


def create_deconvolution_summary_plot(adata: sc.AnnData,
                                    obsm_key: str,
                                    top_n: int = 6,
                                    figsize: tuple = (20, 12),
                                    save: Optional[str] = None) -> plt.Figure:
    """
    Create a comprehensive summary plot of deconvolution results.
    
    Parameters
    ----------
    adata : AnnData
        Spatial data object
    obsm_key : str
        Key in adata.obsm containing deconvolution results
    top_n : int
        Number of top cell types to show individual plots for
    figsize : tuple
        Figure size
    save : str, optional
        Filename to save plot (will be saved in ./figures/ directory)
        
    Returns
    -------
    plt.Figure
        Matplotlib figure object with multiple subplots
    """
    if obsm_key not in adata.obsm:
        raise KeyError(f"Key '{obsm_key}' not found in adata.obsm")
        
    deconv_data = adata.obsm[obsm_key]
    
    # Get top cell types by mean proportion
    mean_props = deconv_data.mean(axis=0).sort_values(ascending=False)
    top_celltypes = mean_props.head(top_n).index.tolist()
    
    # Create subplots: dominant map + top N individual + proportions bar chart
    n_plots = 2 + top_n
    cols = min(4, n_plots)
    rows = int(np.ceil(n_plots / cols))
    
    fig, axes = plt.subplots(rows, cols, figsize=figsize)
    if rows == 1:
        axes = axes.reshape(1, -1)
    axes = axes.flatten()
    
    # Plot 1: Dominant cell type map
    get_maximum_annotation(adata, obsm_key, '_temp_dominant')
    try:
        sc.pl.spatial(adata, color=['_temp_dominant'], ax=axes[0], 
                     img_key="hires", show=False)
        axes[0].set_title('Dominant Cell Types')
    finally:
        if '_temp_dominant' in adata.obs.columns:
            del adata.obs['_temp_dominant']
    
    # Plot 2: Proportions bar chart
    bars = axes[1].bar(range(len(mean_props)), mean_props.values)
    axes[1].set_xlabel('Cell Types')
    axes[1].set_ylabel('Average Proportion')
    axes[1].set_title('Average Cell Type Proportions')
    axes[1].set_xticks(range(len(mean_props)))
    axes[1].set_xticklabels(mean_props.index, rotation=45, ha='right')
    
    # Highlight top cell types in bar chart
    for i, celltype in enumerate(mean_props.index):
        if celltype in top_celltypes:
            bars[i].set_color('red')
        else:
            bars[i].set_color('lightblue')
    
    # Plots 3+: Individual cell type maps
    for i, celltype in enumerate(top_celltypes):
        plot_idx = i + 2
        if plot_idx < len(axes):
            # Add text indicating the cell type (simplified for summary plot)
            axes[plot_idx].text(0.5, 0.5, f'{celltype}\n(See individual plot)', 
                               ha='center', va='center', transform=axes[plot_idx].transAxes)
            axes[plot_idx].set_title(f'{celltype} Distribution')
    
    # Hide unused subplots
    for i in range(n_plots, len(axes)):
        axes[i].set_visible(False)
    
    plt.tight_layout()
    
    # Handle saving
    if save is not None:
        # Create figures directory if it doesn't exist
        figures_dir = 'figures'
        os.makedirs(figures_dir, exist_ok=True)
        
        # Construct full path
        save_path = os.path.join(figures_dir, save)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Summary plot saved to: {save_path}")
        
    return fig

def validate_deconvolution_results(adata: sc.AnnData,
                                 obsm_key: str,
                                 check_proportions: bool = True,
                                 check_non_negative: bool = True,
                                 tolerance: float = 1e-6) -> Dict[str, Any]:
    """
    Validate deconvolution results for common issues.
    
    Parameters
    ----------
    adata : AnnData
        Spatial data object
    obsm_key : str
        Key in adata.obsm containing deconvolution results
    check_proportions : bool
        Whether to check if rows sum to 1
    check_non_negative : bool
        Whether to check for negative values
    tolerance : float
        Tolerance for proportion sum checks
        
    Returns
    -------
    dict
        Validation results with issues found
    """
    if obsm_key not in adata.obsm:
        raise KeyError(f"Key '{obsm_key}' not found in adata.obsm")
        
    deconv_data = adata.obsm[obsm_key]
    results = {
        'valid': True,
        'issues': [],
        'summary': {}
    }
    
    # Check for negative values
    if check_non_negative:
        negative_mask = deconv_data < 0
        if negative_mask.any().any():
            n_negative = negative_mask.sum().sum()
            results['valid'] = False
            results['issues'].append(f"Found {n_negative} negative values")
            results['summary']['negative_values'] = n_negative
    
    # Check proportion sums
    if check_proportions:
        row_sums = deconv_data.sum(axis=1)
        bad_sums = np.abs(row_sums - 1.0) > tolerance
        if bad_sums.any():
            n_bad = bad_sums.sum()
            results['valid'] = False
            results['issues'].append(f"Found {n_bad} rows with sums != 1.0")
            results['summary']['bad_proportion_sums'] = n_bad
            results['summary']['sum_range'] = (row_sums.min(), row_sums.max())
    
    # Check for all-zero rows
    zero_rows = (deconv_data == 0).all(axis=1)
    if zero_rows.any():
        n_zero = zero_rows.sum()
        results['issues'].append(f"Found {n_zero} all-zero rows")
        results['summary']['zero_rows'] = n_zero
    
    # Summary statistics
    results['summary']['shape'] = deconv_data.shape
    results['summary']['mean_values'] = deconv_data.mean().to_dict()
    results['summary']['max_values'] = deconv_data.max().to_dict()
    
    return results

def load_chunked_deconvolution_results(results_dir: str,
                                     chunk_range: Optional[Tuple[int, int]] = None) -> Tuple[np.ndarray, Optional[List[str]]]:
    """
    Load deconvolution results that were saved in chunks.
    
    Parameters
    ----------
    results_dir : str
        Directory containing the chunked results
    chunk_range : tuple, optional
        (start_chunk, end_chunk) to load only specific chunks
        
    Returns
    -------
    tuple
        (combined_matrix, celltypes) - Combined results and cell type names (if available)
    """
    import os
    import glob
    
    if not os.path.exists(results_dir):
        raise FileNotFoundError(f"Results directory not found: {results_dir}")
    
    # Load metadata
    metadata_path = os.path.join(results_dir, 'metadata.npy')
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
    
    metadata = np.load(metadata_path, allow_pickle=True).item()
    total_shape = metadata['shape']
    num_blocks = metadata['num_blocks']
    
    # Determine which chunks to load
    if chunk_range is None:
        start_chunk, end_chunk = 0, num_blocks
    else:
        start_chunk, end_chunk = chunk_range
        end_chunk = min(end_chunk, num_blocks)
    
    # Load and combine chunks
    chunks = []
    for i in range(start_chunk, end_chunk):
        chunk_path = os.path.join(results_dir, f'block_{i:05d}.npz')
        if os.path.exists(chunk_path):
            chunk = sp.load_npz(chunk_path).toarray()
            chunks.append(chunk)
        else:
            print(f"Warning: Chunk {i} not found at {chunk_path}")
    
    if not chunks:
        raise ValueError(f"No valid chunks found in range {start_chunk}-{end_chunk}")
    
    combined = np.vstack(chunks)
    
    # Load cell types if available
    celltypes = None
    celltype_path = os.path.join(results_dir, 'celltypes.txt')
    if os.path.exists(celltype_path):
        with open(celltype_path, 'r') as f:
            celltypes = [line.strip() for line in f.readlines()]
    
    print(f"Loaded {len(chunks)} chunks, combined shape: {combined.shape}")
    
    return combined, celltypes