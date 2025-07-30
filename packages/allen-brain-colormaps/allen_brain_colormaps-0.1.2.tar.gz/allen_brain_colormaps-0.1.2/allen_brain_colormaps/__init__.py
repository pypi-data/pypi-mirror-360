"""
Allen Brain Atlas Cell Type Colormaps
A Python package providing matplotlib and seaborn compatible colormaps for human brain cell types.
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap
import seaborn as sns
import numpy as np

# Class-level color mapping
class_to_color = {
    "Non-neuronal and Non-neural": "#808080",
    "Neuronal: GABAergic": "#F05A28", 
    "Neuronal: Glutamatergic": "#00ADF8"
}

# Subclass-level color mapping
subclass_to_color = {
    "Astrocyte": "#665C47",
    "Microglia-PVM": "#94AF97",
    "L6 IT": "#A19922",
    "VLMC": "#697255",
    "L6 CT": "#2D8CB8",
    "Pvalb": "#D93137",
    "Oligodendrocyte": "#53776C",
    "Vip": "#A45FBF",
    "Endothelial": "#8D6C62",
    "L6b": "#7044AA",
    "Sncg": "#DF70FF",
    "L5 IT": "#50B2AD",
    "L2/3 IT": "#B1EC30",
    "L5/6 NP": "#3E9E64",
    "Sst": "#FF9900",
    "L6 IT Car3": "#5100FF",
    "OPC": "#374A45",
    "Chandelier": "#F641A8",
    "L4 IT": "#00E5E5",
    "L5 ET": "#0D5B78",
    "Lamp5": "#DA808C",
    "Pax6": "#71238C",
    "Sst Chodl": "#B1B10C",
    "Lamp5 Lhx6": "#935F50"
}

# Supertype/cluster-level color mapping
supertype_to_color = {
    "Astro_1": "#D1C9BA",
    "Astro_2": "#AAA395",
    "Astro_3": "#847D71",
    "Astro_4": "#5E574C",
    "Astro_5": "#383228",
    "Chandelier_1": "#F87CC3",
    "Chandelier_2": "#AD2D76",
    "Endo_1": "#D8BFB8",
    "Endo_2": "#B09A93",
    "Endo_3": "#6D615E",
    "L2/3 IT_1": "#EEF987",
    "L2/3 IT_10": "#798C46",
    "L2/3 IT_12": "#5F7438",
    "L2/3 IT_13": "#536831",
    "L2/3 IT_2": "#E1EC7F",
    "L2/3 IT_3": "#D4E078",
    "L2/3 IT_5": "#BAC86A",
    "L2/3 IT_6": "#ADBC63",
    "L2/3 IT_7": "#A0B05C",
    "L2/3 IT_8": "#93A454",
    "L4 IT_1": "#8DF2F7",
    "L4 IT_2": "#72C3C7",
    "L4 IT_3": "#579697",
    "L4 IT_4": "#3C6868",
    "L5 ET_1": "#67A8B2",
    "L5 ET_2": "#0D5B78",
    "L5 IT_1": "#B0DFE2",
    "L5 IT_2": "#99C6C7",
    "L5 IT_3": "#82ADAD",
    "L5 IT_5": "#547B79",
    "L5 IT_6": "#3D625F",
    "L5 IT_7": "#264945",
    "L5/6 NP_1": "#9FD4AE",
    "L5/6 NP_2": "#86BA96",
    "L5/6 NP_3": "#6DA17E",
    "L5/6 NP_4": "#538866",
    "L5/6 NP_6": "#225637",
    "L6 CT_1": "#81CDE7",
    "L6 CT_2": "#5FA3BC",
    "L6 CT_3": "#3D7A91",
    "L6 CT_4": "#1B5166",
    "L6 IT Car3_1": "#874FFF",
    "L6 IT Car3_2": "#631AFF",
    "L6 IT Car3_3": "#23068C",
    "L6 IT_1": "#BEB867",
    "L6 IT_2": "#716C18",
    "L6b_1": "#C7AFD4",
    "L6b_2": "#AA93BB",
    "L6b_3": "#8E77A3",
    "L6b_4": "#715B8B",
    "L6b_5": "#553F73",
    "L6b_6": "#39245B",
    "Lamp5_1": "#F9B7C3",
    "Lamp5_2": "#DA9EA8",
    "Lamp5_3": "#BB848E",
    "Lamp5_4": "#9D6B74",
    "Lamp5_5": "#7E525A",
    "Lamp5_6": "#603A40",
    "Lamp5_Lhx6_1": "#B49186",
    "Micro-PVM_1": "#CFE2D0",
    "Micro-PVM_2": "#94AF97",
    "Oligo_1": "#B2CEC5",
    "Oligo_2": "#799B8E",
    "Oligo_3": "#4A6B61",
    "Oligo_4": "#32443D",
    "OPC_1": "#75827F",
    "OPC_2": "#263430",
    "Pax6_1": "#D38FEF",
    "Pax6_2": "#9E65B5",
    "Pax6_3": "#693B7B",
    "Pax6_4": "#341142",
    "Pvalb_1": "#F97D86",
    "Pvalb_10": "#8E3C43",
    "Pvalb_12": "#772D34",
    "Pvalb_13": "#6B262C",
    "Pvalb_14": "#5F1F25",
    "Pvalb_15": "#54181E",
    "Pvalb_2": "#ED757E",
    "Pvalb_3": "#E16E77",
    "Pvalb_5": "#C96068",
    "Pvalb_6": "#BE5860",
    "Pvalb_7": "#B25159",
    "Pvalb_8": "#A64A52",
    "Pvalb_9": "#9A434A",
    "Sncg_1": "#E99CFF",
    "Sncg_2": "#D58DEA",
    "Sncg_3": "#C17ED6",
    "Sncg_4": "#AD70C2",
    "Sncg_5": "#9A61AE",
    "Sncg_6": "#86539A",
    "Sncg_8": "#5F3672",
    "Sst Chodl_1": "#C9C958",
    "Sst Chodl_2": "#7D7D08",
    "Sst_1": "#FFB84F",
    "Sst_10": "#C68934",
    "Sst_11": "#C08430",
    "Sst_12": "#BA7F2E",
    "Sst_13": "#B47A2B",
    "Sst_19": "#8E5B19",
    "Sst_2": "#F8B24C",
    "Sst_20": "#885616",
    "Sst_22": "#7B4C10",
    "Sst_23": "#75470C",
    "Sst_25": "#693D07",
    "Sst_3": "#F2AD49",
    "Sst_4": "#ECA846",
    "Sst_5": "#E6A343",
    "Sst_7": "#D9993D",
    "Sst_9": "#CD8F37",
    "Vip_1": "#E1B0F7",
    "Vip_11": "#9B74AD",
    "Vip_12": "#946EA6",
    "Vip_13": "#8E689F",
    "Vip_14": "#876297",
    "Vip_15": "#805C90",
    "Vip_16": "#795689",
    "Vip_18": "#6B4A7A",
    "Vip_19": "#644473",
    "Vip_2": "#DAAAEF",
    "Vip_21": "#563864",
    "Vip_23": "#492C56",
    "Vip_4": "#CC9EE1",
    "Vip_5": "#C598D9",
    "Vip_6": "#BE92D2",
    "Vip_9": "#A980BC",
    "VLMC_1": "#979E8A",
    "VLMC_2": "#4A503C",
    "Supertype": "#2C2C2C",
    "SMC-SEAAD": "#8B4513",
    "Monocyte": "#DAA520",
    "Pericyte_1": "#9932CC",
    "Micro-PVM_2_1-SEAAD": "#7FA87C",
    "Lymphocyte": "#4169E1",
    "OPC_2_2-SEAAD": "#4F5F5A",
    "Micro-PVM_3-SEAAD": "#B8D6BB",
    "Astro_6-SEAAD": "#1C1611"
}


class AllenBrainColormaps:
    """
    Allen Brain Atlas cell type colormaps for neuroscience visualization.
    
    Provides consistent colors for cell type hierarchies: class, subclass, and supertype levels.
    Compatible with matplotlib and seaborn plotting functions.
    """
    
    def __init__(self):
        """Initialize Allen Brain colormaps."""
        self._colormaps_registered = False
        self._register_colormaps()
    
    def _register_colormaps(self):
        """Register all colormaps with matplotlib."""
        if self._colormaps_registered:
            return
            
        try:
            # Register discrete colormaps
            self.register_discrete_cmap('allen_brain_class', list(class_to_color.values()))
            self.register_discrete_cmap('allen_brain_subclass', list(subclass_to_color.values()))
            self.register_discrete_cmap('allen_brain_supertype', list(supertype_to_color.values()))
            self._colormaps_registered = True
        except Exception as e:
            # If registration fails, continue without registered colormaps
            print(f"Warning: Could not register colormaps with matplotlib: {e}")
    
    @staticmethod
    def register_discrete_cmap(name, colors):
        """Register a discrete colormap with matplotlib."""
        cmap = ListedColormap(colors, name=name)
        
        # Handle different matplotlib versions more robustly
        import matplotlib as mpl
        
        # Try different registration methods based on matplotlib version
        registered = False
        
        # Method 1: matplotlib >= 3.6.0 (preferred)
        if not registered:
            try:
                if hasattr(mpl, 'colormaps') and hasattr(mpl.colormaps, 'register'):
                    mpl.colormaps.register(cmap, name=name)
                    registered = True
            except Exception:
                pass
        
        # Method 2: matplotlib 3.5.x and some 3.6.x
        if not registered:
            try:
                if hasattr(mpl.cm, 'register_cmap'):
                    mpl.cm.register_cmap(name=name, cmap=cmap)
                    registered = True
            except Exception:
                pass
        
        # Method 3: Older matplotlib versions
        if not registered:
            try:
                if hasattr(plt, 'register_cmap'):
                    plt.register_cmap(name=name, cmap=cmap)
                    registered = True
            except Exception:
                pass
        
        # Method 4: Very old matplotlib versions  
        if not registered:
            try:
                mpl.cm._cmap_registry[name] = cmap
                registered = True
            except Exception:
                pass
        
        if not registered:
            raise RuntimeError(f"Could not register colormap '{name}' with any known matplotlib method")
        
        return cmap
    
    def get_class_colors(self, cell_types=None):
        """
        Get colors for class-level cell types.
        
        Parameters
        ----------
        cell_types : list, optional
            List of cell type names. If None, returns all available colors.
            
        Returns
        -------
        dict
            Dictionary mapping cell types to colors.
        """
        if cell_types is None:
            return class_to_color.copy()
        return {ct: class_to_color.get(ct, '#000000') for ct in cell_types}
    
    def get_subclass_colors(self, cell_types=None):
        """
        Get colors for subclass-level cell types.
        
        Parameters
        ----------
        cell_types : list, optional
            List of cell type names. If None, returns all available colors.
            
        Returns
        -------
        dict
            Dictionary mapping cell types to colors.
        """
        if cell_types is None:
            return subclass_to_color.copy()
        return {ct: subclass_to_color.get(ct, '#000000') for ct in cell_types}
    
    def get_supertype_colors(self, cell_types=None):
        """
        Get colors for supertype/cluster-level cell types.
        
        Parameters
        ----------
        cell_types : list, optional
            List of cell type names. If None, returns all available colors.
            
        Returns
        -------
        dict
            Dictionary mapping cell types to colors.
        """
        if cell_types is None:
            return supertype_to_color.copy()
        return {ct: supertype_to_color.get(ct, '#000000') for ct in cell_types}
    
    def get_cmap(self, level='subclass'):
        """
        Get matplotlib colormap for specified hierarchy level.
        
        Parameters
        ----------
        level : str
            Hierarchy level: 'class', 'subclass', or 'supertype'
            
        Returns
        -------
        matplotlib.colors.ListedColormap
            Colormap object for use with matplotlib/seaborn
        """
        color_maps = {
            'class': class_to_color,
            'subclass': subclass_to_color,
            'supertype': supertype_to_color
        }
        
        if level not in color_maps:
            raise ValueError(f"Level must be one of {list(color_maps.keys())}")
        
        # Return a fresh colormap instead of relying on registration
        colors = list(color_maps[level].values())
        return ListedColormap(colors, name=f'allen_brain_{level}')
    
    def plot_palette(self, level='subclass', figsize=(12, 8)):
        """
        Plot color palette for visual inspection.
        
        Parameters
        ----------
        level : str
            Hierarchy level: 'class', 'subclass', or 'supertype'
        figsize : tuple
            Figure size (width, height)
        """
        color_maps = {
            'class': class_to_color,
            'subclass': subclass_to_color,
            'supertype': supertype_to_color
        }
        
        if level not in color_maps:
            raise ValueError(f"Level must be one of {list(color_maps.keys())}")
        
        colors_dict = color_maps[level]
        
        fig, ax = plt.subplots(figsize=figsize)
        
        y_pos = np.arange(len(colors_dict))
        colors = list(colors_dict.values())
        labels = list(colors_dict.keys())
        
        bars = ax.barh(y_pos, [1] * len(colors), color=colors)
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(labels)
        ax.set_xlabel('Color')
        ax.set_title(f'Allen Brain {level.title()} Color Palette')
        ax.set_xlim(0, 1)
        
        # Add hex color codes
        for i, (bar, color) in enumerate(zip(bars, colors)):
            ax.text(0.5, i, color, ha='center', va='center', 
                   color='white' if self._is_dark_color(color) else 'black',
                   fontweight='bold')
        
        plt.tight_layout()
        return fig, ax
    
    @staticmethod
    def _is_dark_color(hex_color):
        """Check if a hex color is dark (for text contrast)."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        return luminance < 0.5


# Convenience functions for direct access
def get_brain_colors(level='subclass', cell_types=None):
    """
    Get brain cell type colors.
    
    Parameters
    ----------
    level : str
        Hierarchy level: 'class', 'subclass', or 'supertype'
    cell_types : list, optional
        Specific cell types to get colors for
        
    Returns
    -------
    dict
        Mapping of cell types to hex colors
    """
    if level == 'class':
        if cell_types is None:
            return class_to_color.copy()
        return {ct: class_to_color.get(ct, '#000000') for ct in cell_types}
    elif level == 'subclass':
        if cell_types is None:
            return subclass_to_color.copy()
        return {ct: subclass_to_color.get(ct, '#000000') for ct in cell_types}
    elif level == 'supertype':
        if cell_types is None:
            return supertype_to_color.copy()
        return {ct: supertype_to_color.get(ct, '#000000') for ct in cell_types}
    else:
        raise ValueError("Level must be 'class', 'subclass', or 'supertype'")


def get_brain_cmap(level='subclass'):
    """
    Get brain colormap for matplotlib/seaborn.
    
    Parameters
    ----------
    level : str
        Hierarchy level: 'class', 'subclass', or 'supertype'
        
    Returns
    -------
    matplotlib.colors.ListedColormap
        Colormap for plotting
    """
    color_maps = {
        'class': class_to_color,
        'subclass': subclass_to_color,
        'supertype': supertype_to_color
    }
    
    if level not in color_maps:
        raise ValueError(f"Level must be one of {list(color_maps.keys())}")
    
    colors = list(color_maps[level].values())
    return ListedColormap(colors, name=f'allen_brain_{level}')


def plot_brain_palette(level='subclass', figsize=(12, 8)):
    """
    Plot brain color palette.
    
    Parameters
    ----------
    level : str
        Hierarchy level: 'class', 'subclass', or 'supertype'
    figsize : tuple
        Figure size
        
    Returns
    -------
    tuple
        (figure, axis) objects
    """
    brain = AllenBrainColormaps()    
    return brain.plot_palette(level, figsize)


# Entry point functions for matplotlib colormap registration
def get_brain_cmap_class():
    """Entry point for matplotlib class colormap."""
    return ListedColormap(list(class_to_color.values()), name='allen_brain_class')

def get_brain_cmap_subclass():
    """Entry point for matplotlib subclass colormap."""
    return ListedColormap(list(subclass_to_color.values()), name='allen_brain_subclass')

def get_brain_cmap_supertype():
    """Entry point for matplotlib supertype colormap."""
    return ListedColormap(list(supertype_to_color.values()), name='allen_brain_supertype')


# Delayed initialization to avoid import errors
def _initialize_colormaps():
    """Initialize colormaps safely."""
    try:
        _brain_instance = AllenBrainColormaps()
        return _brain_instance
    except Exception:
        # If initialization fails, continue without instance
        return None

# Try to initialize, but don't fail if it doesn't work
_brain_instance = _initialize_colormaps()

# Make color dictionaries available at module level
__all__ = [
    'AllenBrainColormaps',
    'get_brain_colors', 
    'get_brain_cmap',
    'plot_brain_palette',
    'class_to_color',
    'subclass_to_color', 
    'supertype_to_color',
    'get_brain_cmap_class',
    'get_brain_cmap_subclass', 
    'get_brain_cmap_supertype'
]