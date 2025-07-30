# ORCA Studio

## Installation

For the command-line interface:

```bash
uv tool install orca-studio
```

Access the modules in your own Python code:

```bash
uv add orca-studio
```

Or if you're not using `uv`:

```bash
pip install orca-studio
```

## Modules

### ORCA Parse

reading and interpreting data from ORCA output files

Data is made available either directly as values (int, float, bool, ..),
custom dataclasses for structured, non-tabular data (e.g. AILFT data etc.),
and polars DataFrames for tabular data such as absorption spectra.

Each parsing task is handeled in a separate file in `src/orca_parse`.
The module exposes a central `OrcaOutput` class that bundles all parseable attributes
and provides introspective access via properties.


### ORCA Render

creating and rendering 3D visualizations of molecular structures and density isosurfaces

The molecule and isosurfaces are added as meshes to a plotly Figure object.
The module exposes a single user-facing `Renderer` class.

Creating densities (i.e. cube files) requires `orca_plot` to be available in the `$PATH`.


### ORCA Studio

high-level data analysis and visualization with Marimo GUI applications and CLI interface

This central module utilizes the lower-level `orca_parse` and `orca_render` modules to
craft powerful tools for analyzing ORCA calculations.
Raw data from `orca_parse` is refined to provide insight-oriented summaries.
