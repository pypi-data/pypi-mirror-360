"""
Lambda parameter selection functions for ridge regression.

These functions find the optimal regularization parameter for SVD ridge regression.
Different methods are designed for different deconvolution tasks:

FOR CELL-TYPE MAPPING:
    - select_optimal_lambda(): Standard approach, good general choice
    - select_optimal_lambda_calsurrogate(): Efficient surrogate calculation

FOR CELL MAPPING:
    - select_optimal_lambda_mtruncation(): Matrix truncation with non-negativity constraints

Note: select_optimal_lambda_mtruncation is specifically designed for cell mapping
and should not be used for cell-type mapping tasks.
"""

import numpy as np
import time
from typing import Tuple, Optional, List
from ..utils.matrix_operations import split_data, compute_reduced_svd, create_celltype_matrix, aggregate_chunk_by_celltype


def select_optimal_lambda(X: np.ndarray, 
                         Y: np.ndarray, 
                         lambda_range: Optional[np.ndarray] = None,
                         train_ratio: float = 0.8, 
                         random_state: int = 42) -> Tuple[float, float, List[float]]:
    """
    Select optimal lambda using standard ridge regression validation.
    
    **Designed for: CELL-TYPE MAPPING**
    
    Optimized version with minimal dimension checks.
    """
    if lambda_range is None:
        lambda_range = np.logspace(-6, 6, 13)
    
    # Quick dimension check - only adjust if necessary
    nc, ng = X.shape
    if nc < ng:
        print(f"⚠️  Adjusting from {ng} to {nc} genes for stability")
        X = X[:, :nc]
        Y = Y[:, :nc]
    
    # Single split operation
    X_tr, X_te, Y_tr, Y_te = split_data(X, Y, train_ratio, random_state)
    
    # Compute SVD once
    U_tr, Sigma_tr, V_tr = compute_reduced_svd(X_tr, "training")
    U_te, Sigma_te, V_te = compute_reduced_svd(X_te, "test")
    
    # Precompute matrices that don't depend on lambda
    U_tr_U_te = U_tr.T @ U_te
    Y_tr_Y_te = Y_tr.T @ Y_te
    Y_tr_Y_tr = Y_tr.T @ Y_tr
    
    # Fast lambda search
    print(f"\nTesting {len(lambda_range)} lambda values...")
    R_values = []
    for lambda_val in lambda_range:
        R_lambda = _compute_R_lambda_batch(
            lambda_val, U_tr_U_te, Y_tr_Y_te, Y_tr_Y_tr, 
            Sigma_tr, Sigma_te, V_tr, V_te
        )
        R_values.append(R_lambda)
        
    optimal_idx = np.argmin(R_values)
    optimal_lambda = lambda_range[optimal_idx]
    min_R_lambda = R_values[optimal_idx]
    
    print(f"Optimal λ: {optimal_lambda:.6e}, R: {min_R_lambda:.6f}")
    return optimal_lambda, min_R_lambda, R_values


def select_optimal_lambda_mtruncation(X: np.ndarray, 
                                    Y: np.ndarray,
                                    lambda_range: Optional[np.ndarray] = None,
                                    train_ratio: float = 0.8, 
                                    random_state: int = 42) -> Tuple[float, float, List[float]]:
    """
    Select optimal lambda using matrix truncation approach.
    
    **Designed for: CELL MAPPING**
    
    Optimized version with minimal overhead.
    """
    if lambda_range is None:
        lambda_range = np.logspace(-6, 6, 13)
    
    # Quick dimension check
    nc, ng = X.shape
    if nc < ng:
        print(f"⚠️  Adjusting from {ng} to {nc} genes for stability")
        X = X[:, :nc]
        Y = Y[:, :nc]
        
    # Single split and SVD
    X_tr, X_te, Y_tr, Y_te = split_data(X, Y, train_ratio, random_state)
    U_tr, Sigma_tr, V_tr = compute_reduced_svd(X_tr, "training")
    U_te, Sigma_te, V_te = compute_reduced_svd(X_te, "test")
    
    # Fast lambda search
    print(f"\nTesting {len(lambda_range)} lambda values...")
    R_values = []
    for lambda_val in lambda_range:
        R_lambda = _compute_R_lambda_batch2(
            lambda_val, U_tr, U_te, Sigma_tr, Sigma_te, V_tr, V_te, Y_tr, Y_te
        )
        R_values.append(R_lambda)
        
    optimal_idx = np.argmin(R_values)
    optimal_lambda = lambda_range[optimal_idx]
    min_R_lambda = R_values[optimal_idx]
    
    print(f"Optimal λ: {optimal_lambda:.6e}, R: {min_R_lambda:.6f}")
    return optimal_lambda, min_R_lambda, R_values


def select_optimal_lambda_calsurrogate(X: np.ndarray, 
                                     Y: np.ndarray,
                                     celltype_labels: np.ndarray,
                                     lambda_range: Optional[np.ndarray] = None,
                                     train_ratio: float = 0.8, 
                                     random_state: int = 42) -> Tuple[float, float, List[float]]:
    """
    Select optimal lambda using surrogate calculation with cell type aggregation.
    
    **Designed for: CELL-TYPE MAPPING**
    
    Optimized version with cached computations.
    """
    if lambda_range is None:
        lambda_range = np.logspace(-6, 6, 13)
    
    # Quick dimension and validation checks
    nc, ng = X.shape
    if nc < ng:
        X = X[:, :nc]
        Y = Y[:, :nc]
        if len(celltype_labels) > nc:
            celltype_labels = celltype_labels[:nc]
    
    # Validate once
    if len(celltype_labels) != X.shape[0]:
        raise ValueError(f"Celltype labels ({len(celltype_labels)}) != cells ({X.shape[0]})")
    
    # Single split operation
    X_tr, X_te, Y_tr, Y_te = split_data(X, Y, train_ratio, random_state)
    
    # Precompute all matrices that don't depend on lambda
    unique_celltypes = sorted(np.unique(celltype_labels))
    C = create_celltype_matrix(celltype_labels, unique_celltypes)
    Xprime_te = C @ X_te
    
    # Single SVD
    U, S, Vt = compute_reduced_svd(X_tr, "training")
    chunk_result_agg = aggregate_chunk_by_celltype(U.T, celltype_labels, unique_celltypes)
    chunk_result = Y_tr @ Vt.T  # Faster than np.dot
    
    # Fast lambda search - minimal operations in loop
    print(f"\nTesting {len(lambda_range)} lambda values...")
    R_values = []
    
    # Precompute what we can
    S_squared = S * S
    
    for lambda_val in lambda_range:
        # Minimal operations per lambda
        reg_term = S / (S_squared + lambda_val)
        chunk_result2 = chunk_result * reg_term
        chunk_result3 = chunk_result2 @ chunk_result_agg
        
        # Fast non-negativity constraint
        np.maximum(chunk_result3, 0, out=chunk_result3)
        
        # Fast norm calculation
        prediction = chunk_result3 @ Xprime_te
        diff = Y_te - prediction
        R_lambda = np.sum(diff * diff)  # Faster than np.linalg.norm(..., 'fro')**2
        R_values.append(R_lambda)
        
    optimal_idx = np.argmin(R_values)
    optimal_lambda = lambda_range[optimal_idx]
    min_R_lambda = R_values[optimal_idx]
    
    print(f"Optimal λ: {optimal_lambda:.6e}, R: {min_R_lambda:.6f}")
    return optimal_lambda, min_R_lambda, R_values


def _compute_R_lambda_batch(lambda_val, U_tr_U_te, Y_tr_Y_te, Y_tr_Y_tr, 
                           Sigma_tr, Sigma_te, V_tr, V_te):
    """Optimized R(lambda) computation for standard approach."""
    inv_term = Sigma_tr / (Sigma_tr * Sigma_tr + lambda_val)  # Faster than **2
    prep = V_te * Sigma_te
    mat1 = prep @ U_tr_U_te.T
    mat1 *= inv_term  # In-place operation
    mat1 = mat1 @ V_tr.T
    ret = np.trace(mat1 @ Y_tr_Y_te)
    mat1 = mat1 @ Y_tr_Y_tr @ V_tr
    mat1 *= inv_term
    mat1 = mat1 @ U_tr_U_te @ prep.T
    ret -= 2 * np.trace(mat1)
    return ret


def _compute_R_lambda_batch2(lambda_val, U_tr, U_te, Sigma_tr, Sigma_te, 
                            V_tr, V_te, Y_tr, Y_te):
    """Optimized R(lambda) computation for matrix truncation approach."""
    inv_term = Sigma_tr / (Sigma_tr * Sigma_tr + lambda_val)
    nonneg = U_tr * inv_term @ V_tr.T @ Y_tr.T
    np.maximum(nonneg, 0, out=nonneg)  # In-place clipping
    term1 = nonneg @ nonneg.T
    term2 = nonneg @ Y_te
    del nonneg  # Free memory immediately
    prep = V_te * Sigma_te @ U_te.T
    ret = np.trace(prep @ term1 @ prep.T)
    ret -= 2 * np.trace(prep @ term2)
    return ret