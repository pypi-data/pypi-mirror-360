# Project Overview
This is a Jupyter kernel implementation that provides on-demand IPython kernels with dependencies pulled from PEP723 metadata. Each kernel instance is an on-demand virtual environment managed by `uv`. This is kernel compatible with notebooks created by `juv` 

# Installation and use
You must have `uv` installed.

```bash
uv tool run --with kuv --from jupyterlab jupyter-lab 
```

# Known limitations
- The kernel doesn't automatically install new dependencies, it must be manually restarted when the metadata changes.

# Architecture
1. **Kernel Launcher** (`src/kuv/kernel_launcher.py`): The main entry point that launches an IPython kernel via a subprocess that runs `uv` with PEP723 dependencies parsed from the notebook 
2. **Kernel Configuration** (`kernels/kuv/kernel.json`): Jupyter kernel specification installed to `share/jupyter/kernels/`

# Development Commands
```bash
# Test the installation with jupyter-lab, installed using uv
uv tool run --with . --from jupyterlab jupyter-lab
```