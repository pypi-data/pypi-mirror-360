"""
Color palettes and configurations for visualization.
"""

import numpy as np
from typing import List, Dict, Union

# Reference color palette for cell types (from your original script)
REFERENCE_COLORS = {
    'APM': '#1f77b4',              # Blue
    'B': '#ff7f0e',                # Orange
    'Bulge': '#2ca02c',            # Green
    'Cortex': '#d62728',           # Red
    'Cuticle': '#9467bd',          # Purple
    'DP': '#8c564b',               # Brown
    'Eccrine_Acrosyringium': '#e377c2',     # Pink
    'Eccrine_Epithelial': '#7f7f7f',        # Gray
    'Eccrine_Myoepithelial': '#17becf',     # Cyan
    'Endothelial': '#bcbd22',      # Olive
    'Fibroblasts I': '#ff1493',    # Deep pink
    'Fibroblasts II': '#00ced1',   # Dark turquoise
    'Fibroblasts III': '#32cd32',  # Lime green
    'Fibroblasts IV': '#ff4500',   # Orange red
    'IFE_Basal': '#4b0082',        # Indigo
    'IFE_Suprabasal': '#dc143c',   # Crimson
    'IRS': '#00ff7f',              # Spring green
    'Inf_Basal': '#ff69b4',        # Hot pink
    'Inf_Suprabasal': '#4682b4',   # Steel blue
    'LCs': '#daa520',              # Goldenrod
    'Lymphatics': '#8b008b',       # Dark magenta
    'Mast': '#ff6347',             # Tomato
    'Proximal ORS': '#40e0d0',     # Turquoise
    'Melanocytes I': '#9932cc',    # Dark orchid
    'Melanocytes II': '#228b22',   # Forest green
    'Merkel': '#cd5c5c',           # Indian red
    'Myeloid I': '#ffd700',        # Gold
    'Myeloid II': '#8fbc8f',       # Dark sea green
    'Myeloid III': '#4169e1',      # Royal blue
    'NKT': '#ba55d3',              # Medium orchid
    'ORS_Basal': '#20b2aa',        # Light sea green
    'ORS_Suprabasal': '#f0e68c',   # Khaki
    'Isthmus_Suprabasal': '#ff8c00', # Dark orange
    'Pericytes': '#9370db',        # Medium purple
    'Proximal CL': '#3cb371',      # Medium sea green
    'SG': '#f4a460',               # Sandy brown
    'SM I': '#2e8b57',             # Sea green
    'SM II': '#d2691e',            # Chocolate
    'Schwann': '#6495ed',          # Cornflower blue
    'T_Helper': '#dc143c',         # Crimson
    'T_Reg': '#708090',            # Slate gray
    'Other': '#000000'             # Black for 'Other' category
}

# Alternative color palettes (needed for __init__.py imports)
VIRIDIS_COLORS = {
    'continuous': 'viridis',
    'plasma': 'plasma',
    'inferno': 'inferno',
    'magma': 'magma'
}

CATEGORICAL_COLORS = {
    'tab10': 'tab10',
    'tab20': 'tab20',
    'Set1': 'Set1',
    'Set2': 'Set2',
    'Set3': 'Set3'
}

# Continuous colormaps for temporal/pseudotime data
CONTINUOUS_COLORMAPS = [
    'viridis', 'plasma', 'inferno', 'magma', 'cividis',
    'turbo', 'hot', 'cool', 'spring', 'summer', 'autumn', 'winter'
]

# Categorical colormaps for discrete cell types
CATEGORICAL_COLORMAPS = [
    'tab10', 'tab20', 'tab20b', 'tab20c',
    'Set1', 'Set2', 'Set3', 'Paired', 'Dark2', 'Accent'
]

# All available colormaps
ALL_COLORMAPS = CONTINUOUS_COLORMAPS + CATEGORICAL_COLORMAPS


def get_color_palette(palette_name: str = 'reference') -> Union[Dict[str, str], str]:
    """
    Get a color palette by name.
    
    Parameters
    ----------
    palette_name : str
        Name of the palette to retrieve
        Options: 
        - 'reference': Default reference colors for known cell types
        - Any matplotlib colormap name (e.g., 'viridis', 'tab10', 'Set1')
        
    Returns
    -------
    dict or str
        If 'reference': dictionary mapping cell types to hex colors
        Otherwise: matplotlib colormap name as string
        
    Examples
    --------
    >>> # Get reference colors for known cell types
    >>> ref_colors = get_color_palette('reference')
    >>> print(ref_colors['Cortex'])  # '#d62728'
    
    >>> # Get matplotlib colormap name
    >>> cmap = get_color_palette('viridis')
    >>> print(cmap)  # 'viridis'
    """
    if palette_name == 'reference':
        return REFERENCE_COLORS.copy()
    elif palette_name in ALL_COLORMAPS:
        return palette_name
    else:
        available = ['reference'] + ALL_COLORMAPS
        raise ValueError(f"Unknown palette: '{palette_name}'. "
                        f"Available options: {available}")


def create_custom_palette(cell_types: List[str], 
                         base_palette: str = 'tab20') -> Dict[str, str]:
    """
    Create a custom color palette for given cell types.
    
    Parameters
    ----------
    cell_types : list
        List of cell type names
    base_palette : str
        Base matplotlib colormap to use
        
    Returns
    -------
    dict
        Custom color mapping from cell types to hex colors
        
    Examples
    --------
    >>> celltypes = ['Neuron', 'Astrocyte', 'Oligodendrocyte']
    >>> colors = create_custom_palette(celltypes, 'Set3')
    >>> print(colors)
    # {'Neuron': '#8dd3c7', 'Astrocyte': '#ffffb3', 'Oligodendrocyte': '#bebada'}
    """
    try:
        import matplotlib.pyplot as plt
        import matplotlib.colors as mcolors
    except ImportError:
        raise ImportError("matplotlib is required for create_custom_palette()")
    
    if base_palette not in ALL_COLORMAPS:
        raise ValueError(f"Unknown base palette: '{base_palette}'. "
                        f"Available: {ALL_COLORMAPS}")
    
    # Get colors from matplotlib colormap
    try:
        if base_palette.startswith('tab'):
            # tab palettes have discrete colors
            cmap = plt.cm.get_cmap(base_palette)
            if hasattr(cmap, 'colors'):
                colors = cmap.colors
            else:
                # Fallback for newer matplotlib versions
                colors = [cmap(i) for i in np.linspace(0, 1, min(len(cell_types), 20))]
        else:
            # Other palettes - sample evenly
            cmap = plt.cm.get_cmap(base_palette)
            colors = [cmap(i) for i in np.linspace(0, 1, len(cell_types))]
    except Exception as e:
        raise ValueError(f"Error accessing colormap '{base_palette}': {e}")
    
    # Create mapping from cell types to hex colors
    color_dict = {}
    for i, cell_type in enumerate(cell_types):
        color_idx = i % len(colors)
        hex_color = mcolors.to_hex(colors[color_idx])
        color_dict[cell_type] = hex_color
    
    return color_dict


def extend_reference_palette(new_cell_types: List[str], 
                           base_palette: str = 'tab20') -> Dict[str, str]:
    """
    Extend the reference palette with new cell types.
    
    Keeps existing reference colors and adds new ones for unknown cell types.
    
    Parameters
    ----------
    new_cell_types : list
        List of all cell types (including known and unknown)
    base_palette : str
        Base palette for unknown cell types
        
    Returns
    -------
    dict
        Extended color mapping
        
    Examples
    --------
    >>> all_types = ['Cortex', 'Neuron', 'MyNewCellType', 'AnotherNewType']
    >>> colors = extend_reference_palette(all_types)
    >>> print(colors['Cortex'])        # '#d62728' (from reference)
    >>> print(colors['MyNewCellType']) # '#1f77b4' (newly assigned)
    """
    # Start with reference colors
    extended_colors = REFERENCE_COLORS.copy()
    
    # Find cell types not in reference
    unknown_types = [ct for ct in new_cell_types if ct not in REFERENCE_COLORS]
    
    if unknown_types:
        # Create colors for unknown types
        new_colors = create_custom_palette(unknown_types, base_palette)
        extended_colors.update(new_colors)
    
    # Return only colors for requested cell types
    return {ct: extended_colors[ct] for ct in new_cell_types if ct in extended_colors}


def get_colormap_for_data_type(data_type: str) -> str:
    """
    Get recommended colormap for different data types.
    
    Parameters
    ----------
    data_type : str
        Type of data: 'categorical', 'temporal', 'proportion', 'continuous'
        
    Returns
    -------
    str
        Recommended matplotlib colormap name
        
    Examples
    --------
    >>> get_colormap_for_data_type('categorical')  # 'tab20'
    >>> get_colormap_for_data_type('temporal')     # 'viridis'
    """
    recommendations = {
        'categorical': 'tab20',      # Discrete cell types
        'temporal': 'viridis',       # Time/pseudotime data
        'proportion': 'plasma',      # Proportion values 0-1
        'continuous': 'viridis',     # General continuous data
        'diverging': 'RdBu_r',      # Data centered around zero
        'sequential': 'Blues'        # Sequential data (low to high)
    }
    
    if data_type in recommendations:
        return recommendations[data_type]
    else:
        available = list(recommendations.keys())
        raise ValueError(f"Unknown data type: '{data_type}'. "
                        f"Available: {available}")


def validate_colors(color_dict: Dict[str, str]) -> bool:
    """
    Validate that all colors in dictionary are valid hex colors.
    
    Parameters
    ----------
    color_dict : dict
        Dictionary mapping names to color strings
        
    Returns
    -------
    bool
        True if all colors are valid
        
    Raises
    ------
    ValueError
        If any color is invalid
    """
    try:
        import matplotlib.colors as mcolors
    except ImportError:
        # Basic hex validation without matplotlib
        import re
        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
        
        for name, color in color_dict.items():
            if not hex_pattern.match(color):
                raise ValueError(f"Invalid hex color for '{name}': '{color}'")
        return True
    
    # Use matplotlib for validation
    for name, color in color_dict.items():
        try:
            mcolors.to_rgb(color)
        except ValueError as e:
            raise ValueError(f"Invalid color for '{name}': '{color}' - {e}")
    
    return True


# Validate reference colors on import
try:
    validate_colors(REFERENCE_COLORS)
except Exception as e:
    print(f"Warning: Reference colors validation failed: {e}")