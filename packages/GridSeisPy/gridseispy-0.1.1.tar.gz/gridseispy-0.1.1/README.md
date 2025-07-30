# GridSeisPy

A Python library for seismic data processing and visualization, designed for efficiency and ease of use.

## Features

-   **Fast I/O**: Efficiently read and write SEG-Y files.
-   **Intuitive Slicing**: Slice data by inline/crossline, time/depth, or along and between horizons (e.g., `sgy.getInline(100)`, `sgy[..., top:btm]`).
-   **Advanced Indexing**: Supports `numpy`-style regional extraction using `np.ogrid`.
-   **Horizon Arithmetic**: Perform calculations directly on horizon objects (e.g., `thickness = btm_horiz - top_horiz`).
-   **Grid & Coordinate Tools**: Built-in utilities for grid and coordinate transformations.
-   **Easy Visualization**: Simple integration with Matplotlib to display results.

## Installation

You can install GridSeisPy via pip:

```bash
pip install GridSeisPy
```

## Complete Walkthrough

This example demonstrates the core workflow: creating a SEG-Y file from scratch, loading it, performing various slicing operations, and visualizing the results. This code is self-contained and runnable.

```python
import numpy as np
import matplotlib.pyplot as plt
from GridSeisPy import SeisData, Horiz, BinField, TraceField
import os

# --- 1. Create a Demo SEG-Y File ---
# First, we'll programmatically create a seismic file to work with.
output_dir = "usage_output"
os.makedirs(output_dir, exist_ok=True)
sgy_path = os.path.join(output_dir, "demo_seismic.sgy")

n_il, n_xl, n_smp = 50, 60, 120
trace_cnt = n_il * n_xl

with SeisData(sgy_path, mode='w+') as sgy_writer:
    # Create and populate trace headers
    headers = np.zeros(trace_cnt, dtype=sgy_writer.config.trace_header_dtype)
    headers[TraceField.InlineID.name] = np.repeat(np.arange(100, 100 + n_il), n_xl)
    headers[TraceField.XlineID.name] = np.tile(np.arange(500, 500 + n_xl), n_il)
    headers[TraceField.SamplePoints.name] = n_smp
    headers[TraceField.SampleRate.name] = 2000  # 2ms

    # Create trace data
    data = np.array([np.sin(np.linspace(0, 2 * np.pi, n_smp)) * (i / trace_cnt) 
                     for i in range(trace_cnt)], dtype='f4')

    # Set binary header, then write everything to the file
    bh = sgy_writer.binary_header
    bh[BinField.SamplePoints.name] = n_smp
    bh[BinField.SampleRate.name] = 2000 # In microseconds for binary header
    sgy_writer.binary_header = bh  # Re-assign to trigger update
    
    sgy_writer.SetTraceMapping(set_trace_cnt=trace_cnt)
    sgy_writer.SetTraceHeader(np.arange(trace_cnt), headers)
    sgy_writer.SetTraceData(np.arange(trace_cnt), data)

print(f"Demo SEG-Y file created at: {sgy_path}")


# --- 2. Load Data and Create Horizons ---
sgy = SeisData(sgy_path).load()

# Create virtual horizons in memory
top_horiz = sgy.getSeiHoriz()
btm_horiz = sgy.getSeiHoriz()
xx, yy = np.meshgrid(np.linspace(0, 1, sgy.shape[1]), np.linspace(0, 1, sgy.shape[0]))
top_time = 40 + (np.sin(xx * 2 * np.pi) + np.cos(yy * 2 * np.pi)) * 10
btm_time = top_time + 20
top_horiz.elems['time'] = top_time.astype('i4')
btm_horiz.elems['time'] = btm_time.astype('i4')


# --- 3. Slicing and Advanced Operations ---
# a. Get a standard inline slice
inline_slice = sgy.getInline(sgy.arrInlines[sgy.shape[0] // 2])

# b. Get a slice between two horizons
data_between_horizons = sgy[..., top_horiz:btm_horiz]

# c. Perform horizon arithmetic to get time thickness
time_thickness = btm_horiz - top_horiz


# --- 4. Visualization ---
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("GridSeisPy Feature Demonstration")

# Plot inline slice
axes[0].imshow(inline_slice.T, cmap='seismic', aspect='auto')
axes[0].set_title("Inline Slice")
axes[0].set_xlabel("Xline Index")
axes[0].set_ylabel("Time Sample")

# Plot a single trace from the data between horizons
trace = data_between_horizons[25, 30]
axes[1].plot(trace, np.arange(len(trace)))
axes[1].set_title("A Single Trace Between Horizons")
axes[1].invert_yaxis()

# Plot the time thickness map
im = axes[2].imshow(time_thickness.elems['time'], cmap='jet', aspect='auto')
axes[2].set_title("Time Thickness Map (ms)")
fig.colorbar(im, ax=axes[2])

plt.tight_layout()
plt.show()

## Future Plans

`GridSeisPy` is under active development. Here are some of the exciting features planned for the future:

*   **Easy Seismic Attribute Extraction**: We plan to add a comprehensive module for calculating various seismic attributes. The goal is to make extracting attributes like instantaneous frequency, phase, and amplitude as simple as a few lines of code.
*   **AI Integration**: A major focus will be on bridging the gap between seismic data and modern AI. We aim to provide seamless integration with popular deep learning frameworks (like PyTorch and TensorFlow) to facilitate research and application of AI in seismic interpretation.

## License

This project is licensed under the MIT License. 