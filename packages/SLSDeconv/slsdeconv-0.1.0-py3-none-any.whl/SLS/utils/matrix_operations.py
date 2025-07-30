"""
Matrix manipulation utility functions.

These functions handle various matrix operations needed for deconvolution.
They can be used independently for custom analyses.
"""

import numpy as np
from typing import Tuple, Optional, List


def split_data(X: np.ndarray, Y: np.ndarray, train_ratio: float = 0.8, 
               random_state: int = 42) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Split data into training and test sets by genes.
    
    Parameters
    ----------
    X : np.ndarray
        Single-cell expression matrix (cells × genes)
    Y : np.ndarray
        Spatial expression matrix (spots × genes)
    train_ratio : float
        Ratio of genes to use for training
    random_state : int
        Random seed for reproducibility
        
    Returns
    -------
    tuple
        (X_tr, X_te, Y_tr, Y_te) - Training and test splits
        
    Examples
    --------
    >>> X_tr, X_te, Y_tr, Y_te = split_data(X, Y, train_ratio=0.8)
    >>> print(f"Training genes: {X_tr.shape[1]}, Test genes: {X_te.shape[1]}")
    """
    n_g = X.shape[1]
    n_g_tr = int(n_g * train_ratio)
    rng = np.random.RandomState(random_state)
    perm = rng.permutation(n_g)
    tr_idx = perm[:n_g_tr]
    te_idx = perm[n_g_tr:]
    
    X_tr = X[:, tr_idx]
    X_te = X[:, te_idx]
    Y_tr = Y[:, tr_idx]
    Y_te = Y[:, te_idx]
    
    return X_tr, X_te, Y_tr, Y_te


def compute_reduced_svd(X: np.ndarray, name: str = "") -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute reduced SVD decomposition.
    
    Parameters
    ----------
    X : np.ndarray
        Input matrix
    name : str
        Name for logging purposes
        
    Returns
    -------
    tuple
        (U, Sigma, V) - SVD components where X = U @ diag(Sigma) @ V.T
        
    Examples
    --------
    >>> U, S, V = compute_reduced_svd(X, "my_matrix")
    >>> # Verify: X ≈ U @ np.diag(S) @ V.T
    """
    U, Sigma, Vt = np.linalg.svd(X, full_matrices=False)
    V = Vt.T
    
    print(f"\nSVD dimensions for {name}:")
    print(f"U shape: {U.shape}")
    print(f"Sigma length: {Sigma.shape}")
    print(f"V shape: {V.shape}")
    
    return U, Sigma, V


def create_celltype_matrix(celltype_labels: np.ndarray, 
                          unique_celltypes: Optional[List[str]] = None) -> np.ndarray:
    """
    Create cell type aggregation matrix.
    
    This matrix allows aggregation of single-cell data by cell type,
    where each cell contributes equally within its type.
    
    Parameters
    ----------
    celltype_labels : np.ndarray
        Cell type labels for each cell
    unique_celltypes : list, optional
        List of unique cell types. If None, inferred from labels.
        
    Returns
    -------
    np.ndarray
        Cell type aggregation matrix (n_celltypes × n_cells)
        
    Examples
    --------
    >>> labels = np.array(['TypeA', 'TypeA', 'TypeB', 'TypeB', 'TypeC'])
    >>> C = create_celltype_matrix(labels)
    >>> print(C.shape)  # (3, 5) - 3 cell types, 5 cells
    >>> # Use: aggregated = C @ single_cell_data
    """
    if unique_celltypes is None:
        unique_celltypes = sorted(np.unique(celltype_labels))
        
    n_cells = len(celltype_labels)
    n_celltypes = len(unique_celltypes)
    C = np.zeros((n_cells, n_celltypes))
    
    for j, celltype in enumerate(unique_celltypes):
        mask = celltype_labels == celltype
        celltype_count = np.sum(mask)
        if celltype_count > 0:
            C[mask, j] = 1.0 / celltype_count
            
    return C.T


def aggregate_chunk_by_celltype(chunk_result: np.ndarray, 
                               celltype_labels: np.ndarray,
                               unique_celltypes: Optional[List[str]] = None) -> np.ndarray:
    """
    Aggregate chunk results by cell type.
    
    Sums the contributions of cells belonging to the same cell type.
    
    Parameters
    ----------
    chunk_result : np.ndarray
        Result matrix to aggregate (any_dim × n_cells)
    celltype_labels : np.ndarray
        Cell type labels (length n_cells)
    unique_celltypes : list, optional
        List of unique cell types
        
    Returns
    -------
    np.ndarray
        Aggregated matrix (any_dim × n_celltypes)
        
    Examples
    --------
    >>> # Aggregate SVD results by cell type
    >>> U_agg = aggregate_chunk_by_celltype(U.T, celltype_labels)
    >>> print(f"Original: {U.T.shape}, Aggregated: {U_agg.shape}")
    """
    if unique_celltypes is None:
        unique_celltypes = sorted(np.unique(celltype_labels))
        
    n_features = chunk_result.shape[0]  # Could be spots, components, etc.
    n_celltypes = len(unique_celltypes)
    aggregated = np.zeros((n_features, n_celltypes))
    
    for i, celltype in enumerate(unique_celltypes):
        mask = celltype_labels == celltype
        aggregated[:, i] = chunk_result[:, mask].sum(axis=1)
        
    return aggregated


def max_to_one_others_zero(arr: np.ndarray) -> np.ndarray:
    """
    Convert each row to binary with maximum value set to 1, others to 0.
    
    Useful for creating hard assignments from soft deconvolution results.
    
    Parameters
    ----------
    arr : np.ndarray
        Input array (spots × cell_types)
        
    Returns
    -------
    np.ndarray
        Binary array with max values set to 1
        
    Examples
    --------
    >>> proportions = np.array([[0.1, 0.7, 0.2], [0.3, 0.3, 0.4]])
    >>> binary = max_to_one_others_zero(proportions)
    >>> # Result: [[0, 1, 0], [0, 0, 1]]
    """
    result = np.zeros_like(arr)
    
    for i in range(arr.shape[0]):
        max_indices = np.where(arr[i] == np.max(arr[i]))[0]
        if len(max_indices) > 1:
            # If ties, choose randomly
            chosen_index = np.random.choice(max_indices)
            result[i, chosen_index] = 1
        else:
            result[i, max_indices[0]] = 1
            
    return result


def normalize_rows(arr: np.ndarray, method: str = 'sum') -> np.ndarray:
    """
    Normalize rows of a matrix.
    
    Parameters
    ----------
    arr : np.ndarray
        Input matrix
    method : str
        Normalization method ('sum', 'max', 'l2')
        
    Returns
    -------
    np.ndarray
        Row-normalized matrix
        
    Examples
    --------
    >>> # Ensure proportions sum to 1
    >>> normalized = normalize_rows(deconv_results, method='sum')
    """
    if method == 'sum':
        row_sums = arr.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1  # Avoid division by zero
        return arr / row_sums
    elif method == 'max':
        row_maxs = arr.max(axis=1, keepdims=True)
        row_maxs[row_maxs == 0] = 1
        return arr / row_maxs
    elif method == 'l2':
        row_norms = np.linalg.norm(arr, axis=1, keepdims=True)
        row_norms[row_norms == 0] = 1
        return arr / row_norms
    else:
        raise ValueError(f"Unknown normalization method: {method}")


def apply_nonnegativity_constraint(arr: np.ndarray, 
                                  normalize: bool = True) -> np.ndarray:
    """
    Apply non-negativity constraint and optionally normalize.
    
    Parameters
    ----------
    arr : np.ndarray
        Input array
    normalize : bool
        Whether to normalize rows to sum to 1 after clipping
        
    Returns
    -------
    np.ndarray
        Non-negative (and optionally normalized) array
        
    Examples
    --------
    >>> clean_result = apply_nonnegativity_constraint(raw_deconv_result)
    """
    # Clip negative values
    result = np.clip(arr, 0, None)
    
    if normalize:
        result = normalize_rows(result, method='sum')
        # Handle all-zero rows
        zero_rows = np.all(result == 0, axis=1)
        if np.any(zero_rows):
            result[zero_rows, :] = 1.0 / result.shape[1]
    
    return result