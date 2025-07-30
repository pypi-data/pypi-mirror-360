"""
Central renderer class for molecular visualization with isosurfaces.
"""

from pathlib import Path
from typing import Dict, List

import plotly.graph_objects as go

from orca_studio.molecule import Molecule
from orca_studio.render.isosurface_renderer import IsosurfaceRenderer
from orca_studio.render.molecular_render import MolecularRenderer

# Default layout for plotly figures
DEFAULT_LAYOUT = dict(
    scene=dict(
        aspectmode="data",
        xaxis_visible=False,
        yaxis_visible=False,
        zaxis_visible=False,
        bgcolor="whitesmoke",
        dragmode="orbit",
    ),
    scene_camera=dict(
        up=dict(x=0, y=0, z=2),
        eye=dict(x=0, y=2.5, z=0),
        center=dict(x=0, y=0, z=0),
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    legend=dict(dict(yanchor="top", y=0.99, xanchor="left", x=0.01)),
)


class Renderer:
    """
    Central class for rendering molecules with isosurfaces.

    This class provides a high-level interface for visualizing molecular structures
    and quantum chemical properties like orbitals, densities, and spin densities.

    Example:
    --------
    >>> renderer = Renderer("path/to/molecule.out")
    >>> renderer.show()  # Show molecule
    >>> renderer.add_isosurface("path/to/orbital.cube")  # Add orbital isosurface
    >>> renderer.show()  # Show molecule with isosurface
    """

    def __init__(self, file_path: str | Path):
        """
        Initialize a renderer with an ORCA output file.

        Parameters:
        -----------
        file_path : str | Path
            Path to the ORCA output file (.out or .xyz)
        """
        self.file_path = Path(file_path)
        self.molecule = Molecule.from_output(file_path)
        self.mol_renderer = MolecularRenderer(self.molecule)

        # Create figure with molecule
        self.fig = go.Figure()
        self._add_molecule_to_figure()
        self.fig.update_layout(DEFAULT_LAYOUT)

        # Keep track of isosurface traces
        self._isosurface_traces: Dict[str, List[int]] = {}

    def _add_molecule_to_figure(self) -> None:
        """Add molecular geometry to the figure."""
        molecule_meshes = self.mol_renderer.create_meshes()
        for mesh in molecule_meshes:
            self.fig.add_trace(mesh)

    def add_isosurface(
        self,
        cube_file: str | Path,
        isovalue: float = 0.05,
        colors: tuple[str, str] = ("1E88E5", "004D40"),
        smoothness_factor: float = 1.0,
        opacity: float = 1.0,
        name: str = "default",
        replace: bool = True,
    ) -> None:
        """
        Add an isosurface to the current figure.

        Parameters:
        -----------
        cube_file : str | Path
            Path to the cube file containing the volumetric data
        isovalue : float
            Value at which to render the isosurface
        colors : tuple[str, str]
            Tuple of colors for positive and negative isosurfaces
        smoothness_factor : float
            Factor to control the smoothness of the isosurface
        opacity : float
            Opacity of the isosurface (0.0-1.0)
        name : str
            Name to identify this isosurface
        replace : bool
            Whether to replace existing isosurfaces with the same name
        """
        # Remove existing isosurface with the same name if replace is True
        if replace and name in self._isosurface_traces:
            self.remove_isosurface(name)

        # Create isosurface renderer
        iso_renderer = IsosurfaceRenderer(cube_file)

        # Get isosurface meshes
        positive_mesh, negative_mesh = iso_renderer.render_isosurface(
            isovalue=isovalue,
            colors=colors,
            smoothness_factor=smoothness_factor,
            opacity=opacity,
        )

        # Add meshes to figure and track their indices
        trace_indices = []
        trace_indices.append(len(self.fig.data))  # type: ignore
        self.fig.add_trace(positive_mesh)
        trace_indices.append(len(self.fig.data))  # type: ignore
        self.fig.add_trace(negative_mesh)

        # Store trace indices for later removal if needed
        self._isosurface_traces[name] = trace_indices

    def remove_isosurface(self, name: str) -> bool:
        """
        Remove an isosurface from the figure.

        Parameters:
        -----------
        name : str
            Name of the isosurface to remove

        Returns:
        --------
        bool
            True if the isosurface was successfully removed, False otherwise
        """
        if name not in self._isosurface_traces:
            return False

        # Get the trace indices to remove
        indices = sorted(self._isosurface_traces[name], reverse=True)

        # Create a new data list excluding the traces to be removed
        new_data = [trace for i, trace in enumerate(self.fig.data) if i not in indices]
        self.fig.data = new_data

        # Remove from tracking dict
        del self._isosurface_traces[name]
        return True

    def show(self) -> None:
        """Display the current figure."""
        self.fig.show()
