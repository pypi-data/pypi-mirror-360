from typing import Optional

import numpy as np
import plotly.graph_objects as go

from orca_studio.molecule import Atom, Bond, BondType, Molecule
from orca_studio.render.meshes import Mesh

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


class MolecularRenderer:
    """Renders molecular structures using plotly."""

    # Cache mesh templates for performance
    _SPHERE_TEMPLATE = Mesh.unit_sphere()
    _CYLINDER_TEMPLATE = Mesh.unit_cylinder()

    def __init__(self, molecule: Molecule):
        self.molecule = molecule
        self._fig: Optional[go.Figure] = None

    @property
    def fig(self) -> go.Figure:
        if not self._fig:
            self._fig = go.Figure()
            self._fig.update_layout(DEFAULT_LAYOUT)
            molecule_meshes = self.create_meshes()
            for mesh in molecule_meshes:
                self._fig.add_trace(mesh)
        return self._fig

    def create_meshes(
        self,
        atom_scale: float = 0.25,
        bond_radius: float = 0.2,
        show_bonds: bool = True,
        custom_colors: Optional[dict] = None,
    ) -> list[go.Mesh3d]:
        """Render a complete molecule with atoms and bonds.

        Args:
            atom_scale: Scaling factor for atom radii
            bond_radius: Radius for bond cylinders
            show_bonds: Whether to show bonds
            custom_colors: Custom colors for atoms or bonds {element_symbol: hex_color}

        Returns:
            list of plotly Mesh3d objects representing the molecule
        """
        meshes = []

        # Add all atoms
        for atom in self.molecule.geometry.atoms:
            mesh = self._atom_to_mesh(
                atom, scale=atom_scale, custom_colors=custom_colors
            )
            meshes.append(mesh)

        # Add bonds if requested
        if show_bonds:
            bonds = self.molecule.get_bonds_by_radius_overlap()
            for bond in bonds:
                mesh = self._bond_to_mesh(
                    bond, radius=bond_radius, custom_colors=custom_colors
                )
                meshes.append(mesh)

        return meshes

    def _atom_to_mesh(
        self, atom: Atom, scale: float = 0.25, custom_colors: Optional[dict] = None
    ) -> go.Mesh3d:
        """Convert an orca_studio Atom to a plotly Mesh3d.

        Args:
            atom: Atom instance to render
            scale: Scaling factor for atom radius
            custom_colors: Custom colors for atoms {element_symbol: hex_color}

        Returns:
            Plotly Mesh3d object representing the atom
        """
        mesh = self._SPHERE_TEMPLATE.copy()

        # Scale and translate
        radius = atom.element.atomic_radius_pm / 100 * scale
        mesh.x = [x * radius + atom.coords[0] for x in mesh.x]
        mesh.y = [y * radius + atom.coords[1] for y in mesh.y]
        mesh.z = [z * radius + atom.coords[2] for z in mesh.z]

        # Get color from custom colors or element's default
        color = None
        if custom_colors and atom.element.symbol in custom_colors:
            color = custom_colors[atom.element.symbol]
        else:
            color = f"#{atom.element.hex_color}"

        return go.Mesh3d(
            x=mesh.x,
            y=mesh.y,
            z=mesh.z,
            i=mesh.i,
            j=mesh.j,
            k=mesh.k,
            color=color,
            lighting=dict(
                ambient=0.85,
                diffuse=0.2,
                specular=0.6,
                roughness=0.5,
                fresnel=0.5,
            ),
            hoverinfo="skip",
        )

    def _bond_to_mesh(
        self, bond: Bond, radius: float = 0.2, custom_colors: Optional[dict] = None
    ) -> go.Mesh3d:
        """Convert an orca_studio Bond to a plotly Mesh3d.

        Args:
            bond: Bond instance to render
            radius: Radius for bond cylinder
            custom_colors: Custom colors for bonds {bond_type: hex_color}

        Returns:
            Plotly Mesh3d object representing the bond
        """
        mesh = self._CYLINDER_TEMPLATE.copy()

        # Get coordinate vectors from atoms
        atom1, atom2 = bond.atoms
        p0 = atom1.coords
        p1 = atom2.coords

        # Calculate bond direction and length
        direction = p1 - p0
        length = np.linalg.norm(direction)
        if length < 1e-12:
            raise ValueError("Degenerate case, both atoms are at the same position")

        # Normalize direction
        direction_normalized = direction / length

        # The cylinder initially points along the z-axis [0, 0, 1]
        z_axis = np.array([0, 0, 1])

        # Calculate rotation axis and angle using the cross product
        rotation_axis = np.cross(z_axis, direction_normalized)
        rotation_axis_norm = np.linalg.norm(rotation_axis)

        # If rotation_axis is very small, the bond is already aligned with z-axis
        # (or pointing in the opposite direction)
        if rotation_axis_norm < 1e-6:
            # If bond points along -z, we need to rotate 180 degrees around any
            # perpendicular axis (like x)
            if direction_normalized[2] < 0:
                rotation_matrix = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])
            else:  # Bond already points along +z
                rotation_matrix = np.eye(3)
        else:
            # Normalize rotation axis
            rotation_axis = rotation_axis / rotation_axis_norm

            # Calculate rotation angle
            cos_angle = np.dot(z_axis, direction_normalized)
            sin_angle = rotation_axis_norm

            # Build rotation matrix using Rodrigues' rotation formula
            K = np.array(
                [
                    [0, -rotation_axis[2], rotation_axis[1]],
                    [rotation_axis[2], 0, -rotation_axis[0]],
                    [-rotation_axis[1], rotation_axis[0], 0],
                ]
            )
            rotation_matrix = np.eye(3) + sin_angle * K + (1 - cos_angle) * (K @ K)

        # Prepare coordinates as NumPy arrays for vectorized operations
        coords = np.vstack([mesh.x, mesh.y, mesh.z]).T

        # Scale radius based on bond type
        bond_scale = 1.0
        if bond.type == BondType.COORDINATION:
            bond_scale = bond.type.value.radius

        # Apply scaling
        coords[:, 0] *= radius * bond_scale
        coords[:, 1] *= radius * bond_scale
        coords[:, 2] *= length

        # Apply rotation (vectorized)
        rotated_coords = np.dot(coords, rotation_matrix.T)

        # Get color from custom colors or bond type's default
        color = None
        if custom_colors and bond.type in custom_colors:
            color = custom_colors[bond.type]
        else:
            color = f"#{bond.type.value.hex_color}"

        # Create and return mesh
        return go.Mesh3d(
            x=rotated_coords[:, 0] + p0[0],
            y=rotated_coords[:, 1] + p0[1],
            z=rotated_coords[:, 2] + p0[2],
            i=mesh.i,
            j=mesh.j,
            k=mesh.k,
            color=color,
            lighting=dict(
                ambient=0.85,
                diffuse=0.3,
                specular=0.4,
                roughness=0.5,
                fresnel=0.5,
            ),
            hoverinfo="skip",
        )
