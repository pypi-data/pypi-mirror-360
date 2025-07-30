"""
SVD-based ridge regression deconvolution functions.

This module contains the two main deconvolution functions:

1. memory_efficient_svd_ridge_regression(): 
   - For CELL-TYPE MAPPING (spots → cell type proportions)
   - Use with select_optimal_lambda() or select_optimal_lambda_calsurrogate()

2. memory_efficient_svd_ridge_regression_cellmap():
   - For CELL MAPPING (spots → individual cells)
   - Use with select_optimal_lambda_mtruncation()

Both functions can be used directly for maximum flexibility.
"""

import os
import numpy as np
import scipy.sparse as sp
import gc
from datetime import datetime
from typing import Optional, Tuple, Union, List
from ..utils.matrix_operations import aggregate_chunk_by_celltype

def memory_efficient_svd_ridge_regression(X: np.ndarray, 
                                        Y: np.ndarray,
                                        celltype_labels: np.ndarray, 
                                        lambda_reg: float,
                                        output_dir: Optional[str] = None, 
                                        chunk_size: Optional[int] = None) -> Union[Tuple[np.ndarray, List[str]], None]:
    """
    Perform CELL-TYPE deconvolution using SVD ridge regression.
    
    This function deconvolves spatial transcriptomics data into cell type proportions.
    Each spatial spot is mapped to a distribution over cell types.
    
    **Use with lambda from:**
    - select_optimal_lambda() (standard choice)
    - select_optimal_lambda_calsurrogate() (for efficiency)
    
    **Do NOT use with lambda from select_optimal_lambda_mtruncation()**
    
    Parameters
    ----------
    X : np.ndarray
        Single-cell expression matrix (cells × genes)
    Y : np.ndarray
        Spatial expression matrix (spots × genes)
    celltype_labels : np.ndarray
        Cell type labels for single cells
    lambda_reg : float
        Ridge regression regularization parameter (use appropriate lambda selection function)
    output_dir : str, optional
        Directory to save chunked results. If None, returns results in memory.
    chunk_size : int, optional
        Size of chunks for memory-efficient processing. If None, processes all data at once.
        
    Returns
    -------
    tuple or None
        If output_dir is None: (M_hat, unique_celltypes)
            - M_hat: Cell type proportion matrix (spots × cell_types)
            - unique_celltypes: List of cell type names
        If output_dir is provided: None (results saved to disk)
        
    Examples
    --------
    >>> # Cell-type mapping workflow
    >>> lambda_opt, _, _ = select_optimal_lambda(X, Y)  # or select_optimal_lambda_calsurrogate
    >>> M_hat, celltypes = memory_efficient_svd_ridge_regression(
    ...     X, Y, celltype_labels, lambda_opt
    ... )
    >>> print(f"Cell type proportions shape: {M_hat.shape}")
    >>> print(f"Cell types: {celltypes}")
    
    >>> # Memory-efficient processing for large datasets
    >>> memory_efficient_svd_ridge_regression(
    ...     X, Y, celltype_labels, lambda_opt,
    ...     output_dir='./celltype_results', chunk_size=1000
    ... )
    """
    import os
    from datetime import datetime
    
    print(f"[{datetime.now()}] Starting SVD ridge regression for CELL-TYPE mapping...")
    
    # Get unique cell types
    unique_celltypes = sorted(np.unique(celltype_labels))
    print(f"[{datetime.now()}] Found {len(unique_celltypes)} unique cell types: {unique_celltypes}")
    print(f"[{datetime.now()}] X shape: {X.shape}")
    print(f"[{datetime.now()}] Y shape: {Y.shape}")
    
    nc, ng = X.shape
    
    # Validate inputs
    if len(celltype_labels) != nc:
        raise ValueError(f"Number of cell type labels ({len(celltype_labels)}) "
                        f"doesn't match number of cells ({nc})")
    if Y.shape[1] != ng:
        raise ValueError(f"Number of genes in Y ({Y.shape[1]}) "
                        f"doesn't match number of genes in X ({ng})")
    
    # CRITICAL: Check SVD dimension requirements
    if nc < ng:
        print(f"⚠️  WARNING: Number of cells ({nc}) < number of genes ({ng})")
        print(f"   This can cause SVD instability. Reducing to {nc} genes for stable SVD.")
        
        # Select the first nc genes to ensure nc >= ng
        X = X[:, :nc]
        Y = Y[:, :nc]
        ng = nc  # Update gene count
        
        print(f"[{datetime.now()}] Adjusted shapes: X{X.shape}, Y{Y.shape}")
    
    # Additional check for minimum matrix size
    if nc < 2 or ng < 2:
        raise ValueError(f"Matrix too small for SVD: X{X.shape}. Need at least 2x2 matrix.")
    
    # Compute SVD: X = UΣV^T
    print(f"[{datetime.now()}] Computing SVD...")
    try:
        U, S, Vt = np.linalg.svd(X, full_matrices=False)
        print(f"[{datetime.now()}] SVD completed. U: {U.shape}, S: {S.shape}, Vt: {Vt.shape}")
    except np.linalg.LinAlgError as e:
        print(f"❌ SVD failed: {e}")
        print(f"Matrix X shape: {X.shape}, rank: {np.linalg.matrix_rank(X)}")
        raise ValueError(f"SVD decomposition failed for matrix {X.shape}. "
                        f"Try using more cells or fewer genes.") from e
    
    # Free memory
    del X
    gc.collect()
    
    print(f"[{datetime.now()}] Largest singular value: {S[0]:.4f}")
    print(f"[{datetime.now()}] Smallest singular value: {S[-1]:.4f}")
    
    # Check for numerical issues
    if S[-1] < 1e-10:
        print(f"⚠️  WARNING: Very small singular value detected ({S[-1]:.2e}). "
              f"Matrix may be near-singular.")
    
    ns = Y.shape[0]
    
    # Pre-compute regularization term
    print(f"[{datetime.now()}] Computing regularization term...")
    reg_term = S / (S * S + lambda_reg)
    
    # Pre-compute aggregated U^T by cell type
    print(f"[{datetime.now()}] Aggregating U^T by cell type...")
    U_agg = aggregate_chunk_by_celltype(U.T, celltype_labels, unique_celltypes)
    print(f"[{datetime.now()}] Aggregated U^T shape: {U_agg.shape}")
    
    if chunk_size is None:
        return _process_full_data_celltype(Y, Vt, reg_term, U_agg, unique_celltypes, output_dir, ns)
    else:
        return _process_chunked_data_celltype(Y, Vt, reg_term, U_agg, unique_celltypes, output_dir, chunk_size, ns)


def memory_efficient_svd_ridge_regression_cellmap(X: np.ndarray, 
                                                Y: np.ndarray,
                                                lambda_reg: float,
                                                output_dir: Optional[str] = None, 
                                                chunk_size: Optional[int] = None) -> Union[np.ndarray, None]:
    """
    Perform CELL MAPPING deconvolution using SVD ridge regression.
    
    This function maps spatial spots to individual cells rather than cell types.
    Each spatial spot is mapped to a distribution over individual cells.
    Useful for temporal analysis and cell trajectory mapping.
    
    **IMPORTANT: Use with lambda from select_optimal_lambda_mtruncation() ONLY**
    The matrix truncation method accounts for non-negativity constraints.
    
    Parameters
    ----------
    X : np.ndarray
        Single-cell expression matrix (cells × genes)
    Y : np.ndarray
        Spatial expression matrix (spots × genes)
    lambda_reg : float
        Ridge regression regularization parameter (use select_optimal_lambda_mtruncation)
    output_dir : str, optional
        Directory to save chunked results. If None, returns results in memory.
    chunk_size : int, optional
        Size of chunks for memory-efficient processing
        
    Returns
    -------
    np.ndarray or None
        If output_dir is None: M_hat matrix (spots × cells)
        If output_dir is provided: None (results saved to disk)
    """
    import os
    from datetime import datetime
    
    print(f"[{datetime.now()}] Starting SVD ridge regression for CELL MAPPING...")
    print(f"[{datetime.now()}] X shape: {X.shape}")
    print(f"[{datetime.now()}] Y shape: {Y.shape}")
    
    nc, ng = X.shape
    
    # Validate inputs
    if Y.shape[1] != ng:
        raise ValueError(f"Number of genes in Y ({Y.shape[1]}) "
                        f"doesn't match number of genes in X ({ng})")
    
    # CRITICAL: Check SVD dimension requirements
    if nc < ng:
        print(f"⚠️  WARNING: Number of cells ({nc}) < number of genes ({ng})")
        print(f"   This can cause SVD instability. Reducing to {nc} genes for stable SVD.")
        
        # Select the first nc genes to ensure nc >= ng
        X = X[:, :nc]
        Y = Y[:, :nc]
        ng = nc  # Update gene count
        
        print(f"[{datetime.now()}] Adjusted shapes: X{X.shape}, Y{Y.shape}")
    
    # Additional check for minimum matrix size
    if nc < 2 or ng < 2:
        raise ValueError(f"Matrix too small for SVD: X{X.shape}. Need at least 2x2 matrix.")
    
    # Compute SVD: X = UΣV^T
    print(f"[{datetime.now()}] Computing SVD...")
    try:
        U, S, Vt = np.linalg.svd(X, full_matrices=False)
        print(f"[{datetime.now()}] SVD completed. U: {U.shape}, S: {S.shape}, Vt: {Vt.shape}")
    except np.linalg.LinAlgError as e:
        print(f"❌ SVD failed: {e}")
        print(f"Matrix X shape: {X.shape}, rank: {np.linalg.matrix_rank(X)}")
        raise ValueError(f"SVD decomposition failed for matrix {X.shape}. "
                        f"Try using more cells or fewer genes.") from e
    
    # Free memory
    del X
    gc.collect()
    
    print(f"[{datetime.now()}] Largest singular value: {S[0]:.4f}")
    print(f"[{datetime.now()}] Smallest singular value: {S[-1]:.4f}")
    
    # Check for numerical issues
    if S[-1] < 1e-10:
        print(f"⚠️  WARNING: Very small singular value detected ({S[-1]:.2e}). "
              f"Matrix may be near-singular.")
    
    ns = Y.shape[0]
    
    # Pre-compute regularization term
    print(f"[{datetime.now()}] Computing regularization term...")
    reg_term = S / (S * S + lambda_reg)
    
    if chunk_size is None:
        return _process_full_data_cellmap(Y, Vt, reg_term, U, output_dir, ns, nc)
    else:
        return _process_chunked_data_cellmap(Y, Vt, reg_term, U, output_dir, chunk_size, ns, nc)


def _process_full_data_celltype(Y, Vt, reg_term, U_agg, unique_celltypes, output_dir, ns):
    """Process full data for cell type deconvolution with dimension safety."""
    import os
    from datetime import datetime
    
    print(f"[{datetime.now()}] Processing full data...")
    print(f"[{datetime.now()}] Matrix dimensions check:")
    print(f"  Y: {Y.shape}")
    print(f"  Vt: {Vt.shape}")
    print(f"  U_agg: {U_agg.shape}")
    print(f"  reg_term: {reg_term.shape}")
    
    # Verify matrix multiplication compatibility
    if Y.shape[1] != Vt.shape[1]:
        raise ValueError(f"Y columns ({Y.shape[1]}) don't match Vt columns ({Vt.shape[1]})")
    
    # Compute YV
    print(f"[{datetime.now()}] Computing YV...")
    result = np.dot(Y, Vt.T)  # (ns, ng) × (ng, rank) = (ns, rank)
    print(f"[{datetime.now()}] YV result shape: {result.shape}")
    
    # Verify intermediate result shape
    expected_result_shape = (ns, Vt.shape[0])
    if result.shape != expected_result_shape:
        raise ValueError(f"YV result shape {result.shape} incorrect. Expected {expected_result_shape}")
    
    # Apply regularization
    print(f"[{datetime.now()}] Applying regularization...")
    result = result * reg_term  # Broadcasting: (ns, rank) * (rank,) = (ns, rank)
    
    # Verify matrix multiplication compatibility for final step
    if result.shape[1] != U_agg.shape[0]:
        raise ValueError(f"Result columns ({result.shape[1]}) don't match U_agg rows ({U_agg.shape[0]})")
    
    # Compute final multiplication with aggregated U^T
    print(f"[{datetime.now()}] Computing final multiplication with aggregated U^T...")
    M_hat = np.dot(result, U_agg)  # (ns, rank) × (rank, n_celltypes) = (ns, n_celltypes)
    print(f"[{datetime.now()}] Final M_hat shape: {M_hat.shape}")
    
    # Make result non-negative and normalize
    M_hat[M_hat < 0] = 0
    M_hat = M_hat / M_hat.sum(axis=1, keepdims=True)
    M_hat[np.isnan(M_hat)] = 1 / M_hat.shape[1]
    
    # Free memory
    del result
    gc.collect()
    
    if output_dir is None:
        print(f"[{datetime.now()}] Returning M_hat with shape: {M_hat.shape}")
        return M_hat, unique_celltypes
    else:
        _save_celltype_results(output_dir, M_hat, unique_celltypes, ns)
        return None


def _process_full_data_cellmap(Y, Vt, reg_term, U, output_dir, ns, nc):
    """Process full data for cell mapping deconvolution with dimension safety."""
    import os
    from datetime import datetime
    
    print(f"[{datetime.now()}] Processing full data...")
    print(f"[{datetime.now()}] Matrix dimensions check:")
    print(f"  Y: {Y.shape}")
    print(f"  Vt: {Vt.shape}")
    print(f"  U: {U.shape}")
    print(f"  reg_term: {reg_term.shape}")
    
    # Convert Y to dense if it's sparse
    if hasattr(Y, 'toarray'):
        Y_dense = Y.toarray()
    else:
        Y_dense = Y
    
    # Verify matrix multiplication compatibility
    if Y_dense.shape[1] != Vt.shape[1]:
        raise ValueError(f"Y columns ({Y_dense.shape[1]}) don't match Vt columns ({Vt.shape[1]})")
    
    # Compute YV
    print(f"[{datetime.now()}] Computing YV...")
    result = np.dot(Y_dense, Vt.T)  # (ns, ng) × (ng, rank) = (ns, rank)
    print(f"[{datetime.now()}] YV result shape: {result.shape}")
    
    # Apply regularization
    print(f"[{datetime.now()}] Applying regularization...")
    result = result * reg_term  # Broadcasting: (ns, rank) * (rank,) = (ns, rank)
    
    # Verify matrix multiplication compatibility for final step
    if result.shape[1] != U.shape[1]:
        raise ValueError(f"Result columns ({result.shape[1]}) don't match U columns ({U.shape[1]})")
    
    # Compute final multiplication with U^T (no aggregation)
    print(f"[{datetime.now()}] Computing final multiplication with U^T...")
    M_hat = np.dot(result, U.T)  # (ns, rank) × (rank, nc) = (ns, nc)
    print(f"[{datetime.now()}] Final M_hat shape: {M_hat.shape}")
    
    # Make result non-negative and normalize
    M_hat[M_hat < 0] = 0
    M_hat = M_hat / M_hat.sum(axis=1, keepdims=True)
    M_hat[np.isnan(M_hat)] = 1 / M_hat.shape[1]
    
    # Free memory
    del result
    gc.collect()
    
    if output_dir is None:
        print(f"[{datetime.now()}] Returning M_hat with shape: {M_hat.shape}")
        return M_hat
    else:
        _save_cellmap_results(output_dir, M_hat, ns, nc)
        return None
    
def _process_chunked_data_celltype(Y, Vt, reg_term, U_agg, unique_celltypes, output_dir, chunk_size, ns):
    """Process chunked data for cell type deconvolution."""
    import os
    import scipy.sparse as sp
    from datetime import datetime
    
    if output_dir is None:
        raise ValueError("output_dir must be specified when using chunk processing")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save unique cell types
    celltype_path = os.path.join(output_dir, 'celltypes.txt')
    with open(celltype_path, 'w') as f:
        for ct in unique_celltypes:
            f.write(f"{ct}\n")
    
    # Process Y in chunks
    num_chunks = int(np.ceil(ns / chunk_size))
    print(f"[{datetime.now()}] Processing {num_chunks} chunks of size {chunk_size}...")
    
    # Save metadata
    metadata = {
        'shape': (ns, len(unique_celltypes)),
        'num_blocks': num_chunks,
        'block_size': chunk_size
    }
    np.save(os.path.join(output_dir, 'metadata.npy'), metadata)
    
    for i in range(num_chunks):
        chunk_start_time = datetime.now()
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, ns)
        print(f"[{datetime.now()}] Processing chunk {i + 1}/{num_chunks} (rows {start_idx} to {end_idx})")
        
        # Process chunk of Y
        Y_chunk = Y[start_idx:end_idx]
        print(f"[{datetime.now()}] Y chunk loaded, shape: {Y_chunk.shape}")
        
        # Compute M_hat chunk
        print(f"[{datetime.now()}] Computing YV...")
        chunk_result = np.dot(Y_chunk, Vt.T)
        print(f"[{datetime.now()}] Applying regularization...")
        chunk_result = chunk_result * reg_term
        print(f"[{datetime.now()}] Computing final multiplication with aggregated U^T...")
        chunk_result_agg = np.dot(chunk_result, U_agg)
        
        # Make result non-negative and normalize
        chunk_result_agg[chunk_result_agg < 0] = 0
        chunk_result_agg = chunk_result_agg / chunk_result_agg.sum(axis=1, keepdims=True)
        chunk_result_agg[np.isnan(chunk_result_agg)] = 1 / chunk_result_agg.shape[1]
        
        # Save aggregated block as sparse matrix
        block_path = os.path.join(output_dir, f'block_{i:05d}.npz')
        sp.save_npz(block_path, sp.csr_matrix(chunk_result_agg))
        
        # Free memory
        del chunk_result, chunk_result_agg
        gc.collect()
        
        # Log chunk completion
        chunk_end_time = datetime.now()
        chunk_duration = (chunk_end_time - chunk_start_time).total_seconds()
        print(f"[{datetime.now()}] Chunk {i + 1} saved to {block_path}")
        print(f"[{datetime.now()}] Chunk completed in {chunk_duration:.2f} seconds")
        
        # Estimate remaining time
        remaining_chunks = num_chunks - (i + 1)
        estimated_remaining_time = remaining_chunks * chunk_duration
        print(f"[{datetime.now()}] Estimated remaining time: {estimated_remaining_time:.2f} seconds")
        print("-" * 80)
    
    print(f"[{datetime.now()}] Ridge regression completed! Aggregated M_hat blocks saved to {output_dir}")
    return None


def _process_chunked_data_cellmap(Y, Vt, reg_term, U, output_dir, chunk_size, ns, nc):
    """Process chunked data for cell mapping deconvolution."""
    import os
    import scipy.sparse as sp
    from datetime import datetime
    
    if output_dir is None:
        raise ValueError("output_dir must be specified when using chunk processing")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Process Y in chunks
    num_chunks = int(np.ceil(ns / chunk_size))
    print(f"[{datetime.now()}] Processing {num_chunks} chunks of size {chunk_size}...")
    
    # Save metadata
    metadata = {
        'shape': (ns, nc),
        'num_blocks': num_chunks,
        'block_size': chunk_size
    }
    np.save(os.path.join(output_dir, 'metadata.npy'), metadata)
    
    for i in range(num_chunks):
        chunk_start_time = datetime.now()
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, ns)
        print(f"[{datetime.now()}] Processing chunk {i + 1}/{num_chunks} (rows {start_idx} to {end_idx})")
        
        # Process chunk of Y
        Y_chunk = Y[start_idx:end_idx]
        if hasattr(Y_chunk, 'toarray'):
            Y_chunk = Y_chunk.toarray()
        print(f"[{datetime.now()}] Y chunk loaded, shape: {Y_chunk.shape}")
        
        # Compute M_hat chunk
        print(f"[{datetime.now()}] Computing YV...")
        chunk_result = np.dot(Y_chunk, Vt.T)
        print(f"[{datetime.now()}] Applying regularization...")
        chunk_result = chunk_result * reg_term
        print(f"[{datetime.now()}] Computing final multiplication with U^T...")
        chunk_result_final = np.dot(chunk_result, U.T)
        
        # Make result non-negative and normalize
        chunk_result_final[chunk_result_final < 0] = 0
        chunk_result_final = chunk_result_final / chunk_result_final.sum(axis=1, keepdims=True)
        chunk_result_final[np.isnan(chunk_result_final)] = 1 / chunk_result_final.shape[1]
        
        # Save block as sparse matrix
        block_path = os.path.join(output_dir, f'block_{i:05d}.npz')
        sp.save_npz(block_path, sp.csr_matrix(chunk_result_final))
        
        # Free memory
        del chunk_result, chunk_result_final
        gc.collect()
        
        # Log chunk completion
        chunk_end_time = datetime.now()
        chunk_duration = (chunk_end_time - chunk_start_time).total_seconds()
        print(f"[{datetime.now()}] Chunk {i + 1} saved to {block_path}")
        print(f"[{datetime.now()}] Chunk completed in {chunk_duration:.2f} seconds")
        
        # Estimate remaining time
        remaining_chunks = num_chunks - (i + 1)
        estimated_remaining_time = remaining_chunks * chunk_duration
        print(f"[{datetime.now()}] Estimated remaining time: {estimated_remaining_time:.2f} seconds")
        print("-" * 80)
    
    print(f"[{datetime.now()}] Ridge regression completed! M_hat blocks saved to {output_dir}")
    return None


def _save_celltype_results(output_dir, M_hat, unique_celltypes, ns):
    """Save cell type deconvolution results."""
    import os
    import scipy.sparse as sp
    from datetime import datetime
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"[{datetime.now()}] Saving M_hat to {output_dir}")
    
    # Save unique cell types
    celltype_path = os.path.join(output_dir, 'celltypes.txt')
    with open(celltype_path, 'w') as f:
        for ct in unique_celltypes:
            f.write(f"{ct}\n")
    
    # Save metadata (single block)
    metadata = {
        'shape': (ns, len(unique_celltypes)),
        'num_blocks': 1,
        'block_size': ns
    }
    np.save(os.path.join(output_dir, 'metadata.npy'), metadata)
    
    # Save M_hat as sparse matrix
    block_path = os.path.join(output_dir, f'block_00000.npz')
    sp.save_npz(block_path, sp.csr_matrix(M_hat))
    print(f"[{datetime.now()}] M_hat and celltypes saved successfully!")


def _save_cellmap_results(output_dir, M_hat, ns, nc):
    """Save cell mapping deconvolution results."""
    import os
    import scipy.sparse as sp
    from datetime import datetime
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"[{datetime.now()}] Saving M_hat to {output_dir}")
    
    # Save metadata (single block)
    metadata = {
        'shape': (ns, nc),
        'num_blocks': 1,
        'block_size': ns
    }
    np.save(os.path.join(output_dir, 'metadata.npy'), metadata)
    
    # Save M_hat as sparse matrix
    block_path = os.path.join(output_dir, f'block_00000.npz')
    sp.save_npz(block_path, sp.csr_matrix(M_hat))
    print(f"[{datetime.now()}] M_hat saved successfully!")