# Allen Brain Atlas Colormaps

[![PyPI version](https://badge.fury.io/py/allen-brain-colormaps.svg)](https://badge.fury.io/py/allen-brain-colormaps)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python package providing matplotlib and seaborn compatible colormaps for human brain cell types from the Allen Institute Brain Atlas.

## Features

- **Hierarchical color schemes** for brain cell types at three levels:
  - **Class level**: 3 major categories (Non-neuronal, GABAergic, Glutamatergic)
  - **Subclass level**: 24 subclasses (Astrocyte, Microglia-PVM, L6 IT, etc.)
  - **Supertype level**: 136 detailed cell clusters
- **Matplotlib integration**: Register as standard matplotlib colormaps
- **Seaborn compatibility**: Works seamlessly with seaborn plotting functions
- **Consistent colors**: Based on official Allen Institute brain atlas color scheme
- **Easy to use**: Simple API for getting colors and colormaps

## Installation

```bash
pip install allen-brain-colormaps
```

## Quick Start

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from allen_brain_colormaps import get_brain_colors, get_brain_cmap, plot_brain_palette

# Get colors for specific cell types
colors = get_brain_colors('subclass', ['Astrocyte', 'Microglia-PVM', 'L6 IT'])
print(colors)
# {'Astrocyte': '#665C47', 'Microglia-PVM': '#94AF97', 'L6 IT': '#A19922'}

# Use with matplotlib
fig, ax = plt.subplots()
cell_types = ['Astrocyte', 'Pvalb', 'Vip', 'Sst']
values = [100, 80, 60, 40]
colors = get_brain_colors('subclass', cell_types)
ax.bar(cell_types, values, color=[colors[ct] for ct in cell_types])

# Use with seaborn
df = pd.DataFrame({'cell_type': cell_types, 'expression': values})
sns.barplot(data=df, x='cell_type', y='expression', 
           palette=get_brain_colors('subclass', cell_types))

# Get matplotlib colormap
cmap = get_brain_cmap('subclass')
plt.scatter(x, y, c=labels, cmap=cmap)

# Visualize color palette
plot_brain_palette('subclass')
plt.show()
```

## Usage Examples

### Basic Color Access

```python
from allen_brain_colormaps import get_brain_colors

# Get all colors for a hierarchy level
all_subclass_colors = get_brain_colors('subclass')

# Get colors for specific cell types
my_colors = get_brain_colors('supertype', ['Astro_1', 'Pvalb_1', 'Vip_1'])

# Available levels: 'class', 'subclass', 'supertype'
class_colors = get_brain_colors('class')
```

### Matplotlib Integration

```python
import matplotlib.pyplot as plt
from allen_brain_colormaps import get_brain_cmap

# Use as standard matplotlib colormap
cmap = get_brain_cmap('subclass')
plt.imshow(data, cmap=cmap)

# For categorical data
fig, ax = plt.subplots()
scatter = ax.scatter(x, y, c=cell_type_labels, cmap=cmap)
plt.colorbar(scatter)
```

### Seaborn Integration

```python
import seaborn as sns
from allen_brain_colormaps import get_brain_colors

# Direct palette use
cell_types = df['cell_type'].unique()
palette = get_brain_colors('subclass', cell_types)
sns.boxplot(data=df, x='cell_type', y='expression', palette=palette)

# With categorical plots
sns.catplot(data=df, x='condition', y='value', hue='cell_type',
           palette=get_brain_colors('subclass'), kind='bar')
```

### Advanced Usage

```python
from allen_brain_colormaps import AllenBrainColormaps

# Create instance for advanced control
brain = AllenBrainColormaps()

# Get specific colormap
cmap = brain.get_cmap('supertype')

# Plot all available palettes
for level in ['class', 'subclass', 'supertype']:
    brain.plot_palette(level)
    plt.show()
```

## Cell Type Hierarchies

### Class Level (3 types)
- Non-neuronal and Non-neural
- Neuronal: GABAergic  
- Neuronal: Glutamatergic

### Subclass Level (24 types)
- Astrocyte, Microglia-PVM, L6 IT, VLMC, L6 CT, Pvalb, Oligodendrocyte, Vip, Endothelial, L6b, Sncg, L5 IT, L2/3 IT, L5/6 NP, Sst, L6 IT Car3, OPC, Chandelier, L4 IT, L5 ET, Lamp5, Pax6, Sst Chodl, Lamp5 Lhx6

### Supertype Level (136 types)
- Detailed cluster-level annotations (Astro_1, Astro_2, Pvalb_1, Pvalb_2, etc.)

## API Reference

### Functions

- `get_brain_colors(level, cell_types=None)`: Get color dictionary for cell types
- `get_brain_cmap(level)`: Get matplotlib colormap
- `plot_brain_palette(level, figsize=(12, 8))`: Visualize color palette

### AllenBrainColormaps Class

```python
brain = AllenBrainColormaps()
brain.get_class_colors(cell_types=None)
brain.get_subclass_colors(cell_types=None) 
brain.get_supertype_colors(cell_types=None)
brain.get_cmap(level='subclass')
brain.plot_palette(level='subclass', figsize=(12, 8))
```

## Data Source

Colors are based on the Allen Institute Brain Atlas single-cell RNA-seq datasets. The color scheme maintains consistency with the original research and provides a standardized palette for neuroscience visualizations.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this package in your research, please cite the Allen Institute for Brain Science publications.

## Acknowledgments

- Allen Institute for Brain Science for the original color scheme