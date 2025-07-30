# SLS - Spatial Deconvolution Package

A Python package for spatial transcriptomics deconvolution using SVD ridge regression.

## Two Core Functions

SLS provides **two main deconvolution functions**:

### 1. Cell-Type Mapping
```python
sd.memory_efficient_svd_ridge_regression(X, Y, celltype_labels, lambda_reg)
```
Maps spatial spots → cell type proportions

### 2. Cell Mapping  
```python
sd.memory_efficient_svd_ridge_regression_cellmap(X, Y, lambda_reg)
```
Maps spatial spots → individual cells (for temporal analysis)

## Quick Example

```python
import SLS as sd
import scanpy as sc
import numpy as np

# Load data
X, Y, celltype_labels = sd.load_data('FinalAnnotation', st_dir='spatial.h5ad', sc_dir='sc.h5ad')

# Cell-type mapping
lambda_opt, _, _ = sd.select_optimal_lambda(X, Y)
M_hat, celltypes = sd.memory_efficient_svd_ridge_regression(X, Y, celltype_labels, lambda_opt)

# Visualize
adata = sc.read_h5ad('spatial.h5ad')
sd.add_deconvolution_to_adata(adata, celltypes, M_hat, 'deconv')
sd.get_maximum_annotation(adata, 'deconv', 'dominant_celltype')
sd.plot_spatial_deconvolution(adata, 'dominant_celltype', palette=sd.REFERENCE_COLORS)
```

## Complete Workflows

### Cell-Type Mapping Workflow
```python
# 1. Load data
X, Y, labels = sd.load_data('FinalAnnotation', st_dir='...', sc_dir='...')

# 2. Select optimal lambda
lambda_opt, _, _ = sd.select_optimal_lambda(X, Y)  # or sd.select_optimal_lambda_calsurrogate

# 3. Deconvolve
M_hat, celltypes = sd.memory_efficient_svd_ridge_regression(X, Y, labels, lambda_opt)

# 4. Visualize
sd.add_deconvolution_to_adata(adata, celltypes, M_hat, 'deconv')
sd.get_maximum_annotation(adata, 'deconv', 'celltype_result')
```

### Cell Mapping Workflow (Temporal Analysis)
```python
# 1. Filter to cell types of interest
X_filtered, Y_filtered, time_labels = sd.load_data('palantir_pseudotime', adata=adata_sub, HHA=temporal_data)

# 2. Select lambda (use mtruncation method for cell mapping)
lambda_opt, _, _ = sd.select_optimal_lambda_mtruncation(X_filtered, Y_filtered)

# 3. Cell mapping
M_temporal = sd.memory_efficient_svd_ridge_regression_cellmap(X_filtered, Y_filtered, lambda_opt)

# 4. Visualize temporal mapping
sd.add_deconvolution_to_adata(adata_sub, time_labels, M_temporal, 'temporal')
sd.get_maximum_annotation(adata_sub, 'temporal', 'pseudotime', continuous=True, feature_values=time_labels)
```

## Key Functions

| Function | Purpose |
|----------|---------|
| `load_data()` | Load spatial and single-cell data |
| `select_optimal_lambda()` | Lambda selection for cell-type mapping |
| `select_optimal_lambda_mtruncation()` | Lambda selection for cell mapping |
| `memory_efficient_svd_ridge_regression()` | **Core Function 1**: Cell-type mapping |
| `memory_efficient_svd_ridge_regression_cellmap()` | **Core Function 2**: Cell mapping |
| `add_deconvolution_to_adata()` | Add results to spatial data |
| `get_maximum_annotation()` | Get dominant cell types/values |

## Installation

```bash
pip install SLS
```

## Requirements

- Python ≥ 3.8
- scanpy, numpy, pandas, scipy, matplotlib

## Usage Notes

- **Cell-type mapping**: Use `select_optimal_lambda()` or `select_optimal_lambda_calsurrogate()`
- **Cell mapping**: Use `select_optimal_lambda_mtruncation()` only
- **Large datasets**: Add `output_dir` and `chunk_size` parameters for memory efficiency
- **Visualization**: Built-in functions with `sd.REFERENCE_COLORS` palette

## Example Files

See `example.py` for a complete reproduction of published analysis workflows.