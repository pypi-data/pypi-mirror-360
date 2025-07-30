"""
Data loading functions for spatial transcriptomics deconvolution.

These functions handle loading and preprocessing of spatial and single-cell data.
They can be used independently or as part of a pipeline.
"""

import scanpy as sc
import pandas as pd
import numpy as np
import gc
from typing import Optional, Tuple, Union


def load_data(celltype_key: str,
              n_gene: Optional[int] = None, 
              st_dir: Optional[str] = None, 
              sc_dir: Optional[str] = None,
              adata: Optional[sc.AnnData] = None, 
              HHA: Optional[sc.AnnData] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Load spatial transcriptomics and single-cell data.
    
    Parameters
    ----------
    celltype_key : str
        Key for cell type annotations in single-cell data
    n_gene : int, optional
        Number of highly variable genes to select. If None, uses intersection of all genes.
    st_dir : str, optional
        Path to spatial transcriptomics h5ad file
    sc_dir : str, optional
        Path to single-cell h5ad file
    adata : AnnData, optional
        Pre-loaded spatial data object
    HHA : AnnData, optional
        Pre-loaded single-cell data object
        
    Returns
    -------
    tuple
        (HHA_X, adata_X, celltype_labels) - Expression matrices and cell type labels
        
    Examples
    --------
    >>> # Load from files
    >>> X, Y, labels = load_data('FinalAnnotation', 
    ...                          st_dir='spatial.h5ad', 
    ...                          sc_dir='reference.h5ad',
    ...                          n_gene=5000)
    
    >>> # Use pre-loaded data
    >>> X, Y, labels = load_data('FinalAnnotation', 
    ...                          adata=spatial_data, 
    ...                          HHA=sc_data)
    """
    # Validate input parameters
    if adata is None and st_dir is None:
        raise ValueError("Either 'adata' or 'st_dir' must be provided")
    if HHA is None and sc_dir is None:
        raise ValueError("Either 'HHA' or 'sc_dir' must be provided")
        
    # Load spatial transcriptomics data
    if adata is not None:
        print("Using provided adata object")
        spatial_data = adata
    else:
        print(f"Loading spatial data from: {st_dir}")
        spatial_data = sc.read_h5ad(st_dir)
        
    # Load single-cell data
    if HHA is not None:
        print("Using provided HHA object")
        sc_data = HHA
    else:
        print(f"Loading single-cell data from: {sc_dir}")
        sc_data = sc.read_h5ad(sc_dir)
        
    # Gene selection
    genes = _select_genes(spatial_data, sc_data, n_gene)
    
    # Extract expression matrices
    HHA_X = sc_data[:, genes].copy().X
    adata_X = spatial_data[:, genes].copy().X
    
    print(f'Single-cell data shape: {HHA_X.shape}')
    print(f'Spatial data shape: {adata_X.shape}')
    
    return HHA_X.toarray(), adata_X.toarray(), sc_data.obs[celltype_key].values


def load_data_with_time(HHA: sc.AnnData,  # temporary purpose
                       add_key: str, 
                       mat_dir: Optional[str] = None,
                       Matrix: Optional[sc.AnnData] = None) -> sc.AnnData:
    """
    Load temporal data and add time information to single-cell data.
    
    Parameters
    ----------
    HHA : AnnData
        Single-cell data object
    add_key : str
        Key to add from HHA to Matrix
    mat_dir : str, optional
        Path to matrix h5ad file
    Matrix : AnnData, optional
        Pre-loaded matrix object
        
    Returns
    -------
    AnnData
        Filtered matrix with added temporal information
        
    Examples
    --------
    >>> Matrix_with_time = load_data_with_time(sc_data, 
    ...                                        'palantir_pseudotime',
    ...                                        mat_dir='temporal.h5ad')
    """
    if Matrix is None:
        if mat_dir is not None:
            Matrix = sc.read_h5ad(mat_dir)
        else:
            raise ValueError("Either Matrix or mat_dir must be provided")
            
    # Process matrix
    symbol_to_ensembl = dict(zip(HHA.var["names"], HHA.var["ensembl"]))
    
    def map_to_ensembl(name):
        if name.startswith("ENSG"):
            return name
        return symbol_to_ensembl.get(name, "Unknown")
        
    Matrix.var["ensembl"] = Matrix.var["names"].apply(map_to_ensembl)
    Matrix = Matrix[:, Matrix.var["ensembl"] != "Unknown"].copy()
    new_index = Matrix.var["ensembl"]
    Matrix.var.index = new_index
    Matrix.var_names = new_index
    
    HHA.obs.index = HHA.obs.index.astype(str)
    Matrix.obs.index = Matrix.obs.index.astype(str)
    
    # Filter Matrix and add temporal information
    Matrix_filtered = Matrix[Matrix.obs.index.isin(HHA.obs.index)].copy()
    if add_key not in HHA.obs.columns:
        raise ValueError(f"Key '{add_key}' not found in HHA.obs")
        
    Matrix_filtered.obs[add_key] = HHA.obs[add_key][Matrix_filtered.obs.index].values
    return Matrix_filtered


def _select_genes(spatial_data: sc.AnnData, 
                 sc_data: sc.AnnData, 
                 n_gene: Optional[int]) -> list:
    """
    Select genes based on highly variable gene analysis or intersection.
    
    Parameters
    ----------
    spatial_data : AnnData
        Spatial transcriptomics data
    sc_data : AnnData
        Single-cell reference data
    n_gene : int, optional
        Number of highly variable genes to select
        
    Returns
    -------
    list
        Selected gene names
    """
    if n_gene is None:
        print('No gene selection specified (n_gene=None)')
        genes = sorted(list(set(spatial_data.var_names.values)
                         .intersection(set(sc_data.var_names.values))))
        print(f'Final number of genes selected: {len(genes)}')
    else:
        print(f'Selecting top {n_gene} highly variable genes')
        HHA_copy = sc_data.copy()
        sc.pp.highly_variable_genes(HHA_copy, flavor='seurat_v3', n_top_genes=n_gene)
        genes_sc = HHA_copy.var_names[HHA_copy.var['highly_variable']].tolist()
        del HHA_copy
        gc.collect()
        
        genes = sorted(list(set(genes_sc)
                         .intersection(set(spatial_data.var_names.values))))
        print(f'Final number of genes selected: {len(genes)}')
        
    return genes