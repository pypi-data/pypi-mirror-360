from collections import namedtuple
from pathlib import Path
from typing import Any

import numpy as np
import plotly.graph_objects as go
from scipy.ndimage import zoom
from skimage import measure


class IsosurfaceRenderer:
    """Renders molecular orbitals, densities, and other volumetric data as isosurfaces."""

    def __init__(self, cube_file: str | Path):
        """Initialize the renderer with a cube file.

        Args:
            cube_file: Path to the cube file containing volumetric data
        """
        self.cube_file = Path(cube_file)
        self.cube_data = self._read_cube()

    def render_isosurface(
        self,
        isovalue: float = 0.05,
        colors: tuple[str, str] = ("1E88E5", "004D40"),
        smoothness_factor: float = 1.0,
        opacity: float = 1.0,
    ) -> tuple[go.Mesh3d, go.Mesh3d]:
        """Render isosurfaces from the volumetric data.

        Args:
            isovalue: Value at which to create the isosurface
            colors: tuple of hex colors for (positive, negative) isosurfaces
            smoothness_factor: Factor to smooth the volumetric data
            opacity: Opacity of the isosurfaces

        Returns:
            tuple of (positive_isosurface, negative_isosurface) Mesh3d objects
        """
        # Smooth the density data for better visualization
        if smoothness_factor != 1.0:
            density = self._smooth_density(self.cube_data, smoothness_factor)
        else:
            density = self.cube_data

        # Mesh properties for both surfaces
        mesh_props = dict(
            opacity=opacity,
            showlegend=True,
            hoverinfo="skip",
            lighting=dict(
                ambient=0.5,
                diffuse=0.7,
                specular=0.2,
                roughness=0.2,
                fresnel=0.1,
            ),
        )

        # Create the isosurfaces
        isosurfaces = (
            self._create_surface(density, isovalue),
            self._create_surface(density, -isovalue),
        )

        # Create the positive isosurface mesh
        positive_mesh = go.Mesh3d(
            name="Positive",
            color=f"#{colors[0]}",
            x=isosurfaces[0][0][:, 0],
            y=isosurfaces[0][0][:, 1],
            z=isosurfaces[0][0][:, 2],
            i=isosurfaces[0][1][:, 0],
            j=isosurfaces[0][1][:, 1],
            k=isosurfaces[0][1][:, 2],
            **mesh_props,
        )

        # Create the negative isosurface mesh
        negative_mesh = go.Mesh3d(
            name="Negative",
            color=f"#{colors[1]}",
            x=isosurfaces[1][0][:, 0],
            y=isosurfaces[1][0][:, 1],
            z=isosurfaces[1][0][:, 2],
            i=isosurfaces[1][1][:, 0],
            j=isosurfaces[1][1][:, 1],
            k=isosurfaces[1][1][:, 2],
            **mesh_props,
        )

        return (positive_mesh, negative_mesh)

    def _create_surface(
        self, density: dict[str, Any], isovalue: float
    ) -> tuple[np.ndarray, np.ndarray]:
        """Create an isosurface at the given isovalue from the density data.

        Args:
            density: Volumetric data dictionary
            isovalue: Level at which to create the isosurface

        Returns:
            tuple of (vertices, faces) arrays
        """
        try:
            vertices, faces, normals, values = measure.marching_cubes(
                density["values"], level=isovalue, spacing=density["spacing"]
            )
        except ValueError as e:
            raise ValueError(
                "Isovalue is too extreme, the isosurface would protrude the grid volume."
            ) from e

        # Center vertices to the origin
        vertices += density["origin"]
        return (vertices, faces)

    def _smooth_density(
        self, density: dict[str, Any], smoothness_factor: float = 1.0
    ) -> dict[str, Any]:
        """Smooth the volumetric data for better visualization.

        Args:
            density: Original density data dictionary
            smoothness_factor: Factor to increase resolution for smoother surfaces

        Returns:
            New density dictionary with smoothed values
        """
        smoothed_density = density.copy()
        smoothed_density["values"] = zoom(
            input=density["values"], zoom=smoothness_factor, order=3
        )
        smoothed_density["spacing"] = [
            basis_vec / smoothness_factor for basis_vec in density["spacing"]
        ]
        return smoothed_density

    def _read_cube(self) -> dict[str, Any]:
        """Parse a .cube density file into a dictionary.

        Returns:
            dictionary containing parsed cube file data:
            {
                "origin": origin coordinates,
                "basis_vectors": basis vectors,
                "grid": grid dimensions,
                "values": volumetric data values,
                "spacing": grid spacing
            }
        """
        lines = self.cube_file.read_text().splitlines()

        _comments = lines[:2]
        n_atoms, *origin = lines[2].strip().split()
        n_atoms = int(n_atoms)

        # Cube files encode the unit (Bohrs or Angstroms) in the sign
        # of the number of atoms
        unit = "bohr"
        if n_atoms < 0:
            n_atoms = -n_atoms
            # unit = "angstrom"  # Commented as per original logic
        scale = 0.529177 if unit == "bohr" else 1.0

        origin = np.array([float(coord) * scale for coord in origin])

        BasisVector = namedtuple("BasisVector", ["n_voxels", "x", "y", "z"])
        basis_vectors = {
            "x": BasisVector(
                int(lines[3].split()[0]),
                *[float(coord) * scale for coord in lines[3].split()[1:]],
            ),
            "y": BasisVector(
                int(lines[4].split()[0]),
                *[float(coord) * scale for coord in lines[4].split()[1:]],
            ),
            "z": BasisVector(
                int(lines[5].split()[0]),
                *[float(coord) * scale for coord in lines[5].split()[1:]],
            ),
        }

        if (
            not basis_vectors["x"].n_voxels
            == basis_vectors["y"].n_voxels
            == basis_vectors["z"].n_voxels
        ):
            raise ValueError("Number of voxels in each direction must be equal")

        grid_resolution = basis_vectors["x"].n_voxels

        # Skip atom section
        grid_values = []
        for line in lines[6 + n_atoms :]:
            grid_values.extend(map(float, line.split()))

        try:
            grid_values = np.array(grid_values).reshape(
                basis_vectors["x"].n_voxels,
                basis_vectors["y"].n_voxels,
                basis_vectors["z"].n_voxels,
            )
        except ValueError:
            # Sometimes ORCA writes an additional charge/multiplicity line after the coordinates
            # which goes against the cube file format
            grid_values = grid_values[2:]
            grid_values = np.array(grid_values).reshape(
                basis_vectors["x"].n_voxels,
                basis_vectors["y"].n_voxels,
                basis_vectors["z"].n_voxels,
            )

        spacing = (
            basis_vectors["x"].x,
            basis_vectors["y"].y,
            basis_vectors["z"].z,
        )

        return {
            "origin": origin,
            "basis_vectors": basis_vectors,
            "grid": grid_resolution,
            "values": grid_values,
            "spacing": spacing,
        }
