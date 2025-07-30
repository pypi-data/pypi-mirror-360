"""
Configuration and settings for spatial deconvolution.

This module contains color palettes, default parameters,
and configuration utilities for visualization and analysis.
"""

from .colors import (
    REFERENCE_COLORS,
    VIRIDIS_COLORS,
    CATEGORICAL_COLORS,
    get_color_palette,
    create_custom_palette
)

__all__ = [
    "REFERENCE_COLORS",
    "VIRIDIS_COLORS", 
    "CATEGORICAL_COLORS",
    "get_color_palette",
    "create_custom_palette"
]