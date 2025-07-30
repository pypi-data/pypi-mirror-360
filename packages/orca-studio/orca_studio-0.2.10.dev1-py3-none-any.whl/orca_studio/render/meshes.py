from copy import deepcopy
from dataclasses import dataclass
from typing import Self

import numpy as np

# The sphere scales much worse than the cylinders.
# A sphere with a resolution of 64 takes 0.2MB, 128 is 0.8MB.
# A cylinder with a resolution of 64 only takes 0.007MB, 128 is 0.0014MB.
RESOLUTION: int = 96


@dataclass
class Mesh:
    x: list[float]
    y: list[float]
    z: list[float]
    i: list[int]
    j: list[int]
    k: list[int]

    def copy(self) -> "Mesh":
        """Create a deep copy of this mesh."""
        return deepcopy(self)

    @classmethod
    def unit_sphere(cls, resolution: int = RESOLUTION // 4) -> Self:
        """Create a unit sphere centered at the origin.

        Args:
            resolution: Number of segments for the sphere

        Returns:
            Unit sphere mesh
        """
        center = (0, 0, 0)
        cx, cy, cz = center
        theta_vals = np.linspace(0, np.pi, resolution + 1)
        phi_vals = np.linspace(0, 2 * np.pi, resolution, endpoint=False)
        theta_grid, phi_grid = np.meshgrid(theta_vals, phi_vals, indexing="ij")

        x_2d = cx + np.sin(theta_grid) * np.cos(phi_grid)
        y_2d = cy + np.sin(theta_grid) * np.sin(phi_grid)
        z_2d = cz + np.cos(theta_grid)

        x = x_2d.ravel().tolist()
        y = y_2d.ravel().tolist()
        z = z_2d.ravel().tolist()

        i, j, k = [], [], []

        # Generate triangle indices
        for t in range(resolution):
            for p in range(resolution):
                # Calculate vertex indices
                i0 = t * resolution + (p % resolution)
                i1 = t * resolution + ((p + 1) % resolution)
                i2 = (t + 1) * resolution + (p % resolution)
                i3 = (t + 1) * resolution + ((p + 1) % resolution)

                # First triangle
                i.append(i0)
                j.append(i1)
                k.append(i2)

                # Second triangle
                i.append(i1)
                j.append(i3)
                k.append(i2)

        return cls(x, y, z, i, j, k)

    @classmethod
    def unit_cylinder(cls, resolution: int = RESOLUTION) -> Self:
        """Create a unit cylinder along the z-axis with radius 1.

        The cylinder has its base at z=0 and top at z=1.

        Args:
            resolution: Number of segments around the cylinder

        Returns:
            Unit cylinder mesh
        """
        ADD_CAPS = True

        # Create circle points
        angles = np.linspace(0, 2 * np.pi, resolution, endpoint=False)
        circle_x = np.cos(angles)
        circle_y = np.sin(angles)

        # Create bottom and top circles
        bottom_x = circle_x
        bottom_y = circle_y
        bottom_z = np.zeros_like(circle_x)

        top_x = circle_x
        top_y = circle_y
        top_z = np.ones_like(circle_x)

        # Combine coordinates
        x = np.hstack([bottom_x, top_x]).tolist()
        y = np.hstack([bottom_y, top_y]).tolist()
        z = np.hstack([bottom_z, top_z]).tolist()

        # Create triangles for cylinder walls
        i, j, k = [], [], []
        for seg in range(resolution):
            seg_next = (seg + 1) % resolution
            b0 = seg
            b1 = seg_next
            t0 = seg + resolution
            t1 = seg_next + resolution

            # Two triangles per segment
            i.extend([b0, b1])
            j.extend([b1, t0])
            k.extend([t0, b0])
            i.extend([b1])
            j.extend([t1])
            k.extend([t0])

        if ADD_CAPS:
            # Add center points for caps
            bottom_center_idx = len(x)
            top_center_idx = len(x) + 1
            x.extend([0.0, 0.0])
            y.extend([0.0, 0.0])
            z.extend([0.0, 1.0])

            # Bottom cap
            for seg in range(resolution):
                seg_next = (seg + 1) % resolution
                i.append(bottom_center_idx)
                j.append(seg_next)
                k.append(seg)
            # Top cap
            for seg in range(resolution):
                seg_next = (seg + 1) % resolution
                i.append(top_center_idx)
                j.append(seg + resolution)
                k.append(seg_next + resolution)

        return cls(x, y, z, i, j, k)
