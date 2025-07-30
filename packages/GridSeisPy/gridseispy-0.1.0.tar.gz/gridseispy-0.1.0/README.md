# SeisPy

A Python library for seismic data processing and visualization, designed for efficiency and ease of use.

## Features

-   Fast reading and writing of SEG-Y files.
-   Intuitive slicing and indexing of seismic data (e.g., `sgy.getInline(100)`, `sgy[..., top:bottom]`).
-   Built-in tools for coordinate and grid transformations.
-   Easy integration with Matplotlib for visualization.

## Installation

You can install SeisPy via pip:

```bash
pip install seispy
```

## Quick Start

Here is a simple example of how to load a SEG-Y file, perform some slicing, and visualize the results.

```python
import matplotlib.pyplot as plt
from seispy import SeisData, Horiz

# --- 1. Load Data ---
# Note: You need to replace the paths with your actual file paths.
sgy_path = "path/to/your/data.sgy"
top_path = "path/to/your/top_horizon.txt"
btm_path = "path/to/your/bottom_horizon.txt"

try:
    sgy = SeisData(sgy_path).load()
    top_horiz = sgy.getSeiHoriz().setTimeByTXT(top_path)
    btm_horiz = sgy.getSeiHoriz().setTimeByTXT(btm_path)
    print("Data loaded successfully.")

except Exception as e:
    print(f"Error loading files: {e}")
    # Handle error or use dummy data for demonstration
    # sgy, top_horiz, btm_horiz = create_dummy_data()

# --- 2. Slice Data ---
# Get an inline slice
inline_slice = sgy.getInline(sgy.arrInlines[sgy.shape[0] // 2])

# Slice along a horizon
slice_along_top = sgy[..., top_horiz]

# Get data between two horizons
data_between_horizons = sgy[..., top_horiz:btm_horiz]


# --- 3. Visualize Results ---
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
fig.suptitle("SeisPy Demo")

# Plot inline
axes[0].imshow(inline_slice.T, cmap='seismic', aspect='auto')
axes[0].set_title("Inline Slice")

# Plot slice along horizon
axes[1].imshow(slice_along_top, cmap='viridis', aspect='auto')
axes[1].set_title("Slice Along Top Horizon")

# Plot a trace from the data between horizons
trace = data_between_horizons[50, 50] # Example trace
axes[2].plot(trace, range(len(trace)))
axes[2].set_title("A Single Trace")
axes[2].invert_yaxis()

plt.tight_layout()
plt.show()

```

## License

This project is licensed under the MIT License. 