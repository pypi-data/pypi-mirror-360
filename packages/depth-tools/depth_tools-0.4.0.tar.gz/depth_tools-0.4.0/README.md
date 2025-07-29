![Unit tests badge](https://github.com/mntusr/depth_tools/actions/workflows/unit-tests.yml/badge.svg)


[Documentation](./doc)

# Depth Tools

A simple pure Python implementation for common depth-map-related operations.

Minimal installation:

```
pip install depth_tools
```

Features:

- Loss calculation
- Dataset handling (requires extra `Datasets`)
- Prediction alignment
- Depth clip implementation
- Limited Pytorch support (requires package Pytorch)
- Point cloud diagram creation (requires extra `Plots`)
- Depth/disparity/distance normalization
- Conversion between depth maps and distance maps

The contents of the extras:

- `Datasets`: `scipy`, `h5py`, `Pillow`, `pandas`
- `Plots`: `matplotlib`, `plotly`

All Pytorch-related functions are contained by the `depth_tools.pt` package. Contrary to its root package, you need to install Pytorch to import this package.

Documentation:

- [Introduction](doc/Introduction.md)
- [Array formats](doc/Array-formats.md)

# Comparison to Open3D

These two packages have somewhat different goals.

Open3D has a wider scope, like GUI handling. In exchange, it has more dependencies and it is partially written in C++.

Depth Tools has a narrower scope. In exchange, it is written in pure Python and tries to minimize the number of dependencies. Depth tools also uses a simpler camera model (with all of its pros and cons).
