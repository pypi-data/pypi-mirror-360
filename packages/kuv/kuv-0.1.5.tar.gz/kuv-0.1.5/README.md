# Project Overview
This is a Jupyter kernel implementation that provides on-demand IPython kernels with dependencies pulled from PEP723 metadata. Each kernel instance is an on-demand virtual environment managed by `uv`. This kernel is compatible with notebooks created by `juv`, EXCEPT that lockfile metadata is not respected (yet). 

# Installation and use
Either:
```bash
uv tool run --with kuv --from jupyterlab jupyter-lab 
```
or just `pip install kuv` to your existing jupyter server.

# Known limitations
- The kernel doesn't automatically install new dependencies, it must be manually restarted when the metadata changes.
- Doesn't respect juv lockfile metadata
- Unlike juv, can't install jupyter extensions

# Why use this instead of juv
This allows you to have a single jupyter server, with unique virtualenvs for each notebook. For my use, this was a better level of abstraction than running a whole jupyter server for each notebook.

# Development Commands
Install uv manually and then:
```bash
# Test package with jupyter-lab
uv tool run --with . --refresh-package kuv --from jupyterlab jupyter-lab
```
