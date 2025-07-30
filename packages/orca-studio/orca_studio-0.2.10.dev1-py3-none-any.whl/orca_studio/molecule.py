import json
from dataclasses import dataclass
from enum import Enum
from itertools import combinations
from pathlib import Path
from typing import Optional, Self

import numpy as np
import polars as pl
from numpy.typing import NDArray
from plotly.graph_objects import Figure

from orca_studio.orca_output import OrcaOutput
from orca_studio.parse.common import OrcaParsingError

PERIODIC_TABLE: pl.DataFrame = pl.read_json(
    Path(__file__).parent / "periodic_table.json"
)


@dataclass
class Element:
    symbol: str
    atomic_number: int
    name: str
    hex_color: str
    electron_configuration: str
    electronegativity: float
    atomic_radius_pm: int
    group_block: str

    @classmethod
    def from_symbol(cls, symbol: str) -> Self:
        element_df = PERIODIC_TABLE.filter(
            pl.col("symbol").str.to_lowercase() == symbol.lower()
        )
        if element_df.is_empty():
            raise ValueError(f"No element with symbol '{symbol}' found!")
        element: dict = element_df.to_dicts()[0]
        return cls(**element)

    @classmethod
    def from_atomic_number(cls, atomic_number: int) -> Self:
        element_df = PERIODIC_TABLE.filter(pl.col("atomic_number") == atomic_number)
        if element_df.is_empty():
            raise ValueError(f"No element with atomic number '{atomic_number}' found!")
        element: dict = element_df.to_dicts()[0]
        return cls(**element)

    @property
    def is_metal(self) -> bool:
        metal_blocks = [
            "Alkali metal",
            "Alkaline earth metal",
            "Transition metal",
            "Post-transition metal",
        ]
        return True if self.group_block in metal_blocks else False


@dataclass
class Atom:
    element: Element
    coords: NDArray

    def __repr__(self) -> str:
        return f"{self.element.symbol} {self.coords[0]:.4f} {self.coords[1]:.4f} {self.coords[2]:.4f}"

    @classmethod
    def from_str(cls, string: str) -> Self:
        symbol_or_atomic_number, x, y, z = string.split()
        if symbol_or_atomic_number.isdigit():
            atomic_number = int(symbol_or_atomic_number)
            element = Element.from_atomic_number(atomic_number)
        else:
            symbol = str(symbol_or_atomic_number)
            element = Element.from_symbol(symbol)
        coords = np.array([x, y, z], dtype=float)
        return cls(element, coords)


@dataclass
class Geometry:
    """Molecular geometry composed of Atoms and an optional comment"""

    atoms: list[Atom]
    comment: str = ""

    def __repr__(self) -> str:
        return (
            f"{len(self.atoms)}\n{self.comment}\n"
            + "\n".join([str(a) for a in self.atoms])
            + "\n"
        )

    @classmethod
    def from_xyz_file(cls, xyz_file: Path | str) -> Self:
        xyz = Path(xyz_file).read_text()
        return cls.from_xyz(xyz)

    @classmethod
    def from_hess_file(cls, hess_file: Path | str) -> Self:
        lines = Path(hess_file).read_text().splitlines()

        idx = None
        for i, line in enumerate(lines):
            if "$atoms" in line.strip():
                idx = i
                break

        if not idx:
            raise OrcaParsingError("Atoms not found in .hess file")

        bohr_to_angstrom = 0.529177249

        atoms = []
        for line in lines[idx + 2 :]:
            if not line.strip():
                break
            symbol, weight, x, y, z = line.split()
            # Convert the coordinates from Bohrs to Angstrom..
            x, y, z = map(lambda i: float(i) * bohr_to_angstrom, [x, y, z])
            atoms.append(f"{symbol} {x} {y} {z}")

        xyz = f"{len(atoms)}\n\n" + "\n".join(atoms)
        return cls.from_xyz(xyz)

    @classmethod
    def from_xyz(cls, xyz: str) -> Self:
        lines = xyz.splitlines()
        n_atoms = int(lines[0])
        comment = str(lines[1])
        atoms = [Atom.from_str(line) for line in lines[2:]]
        if n_atoms != len(atoms):
            raise ValueError(
                f"Invalid XYZ file: expected {n_atoms} atoms, found {len(atoms)}"
            )
        return cls(atoms, comment)

    def write_xyz_file(self, xyz_file: Path | str, overwrite: bool = False) -> Path:
        xyz_file = Path(xyz_file)
        if xyz_file.exists():
            if overwrite:
                xyz_file.unlink()
            else:
                raise FileExistsError(
                    f"{xyz_file} already exists. Use `overwrite=True`"
                )
        xyz_file.write_text(str(self))
        return xyz_file

    def displace_along_normal_mode(
        self, hess_file: Path | str, mode: int, amplitude: float = 1.0
    ) -> "Geometry":
        normal_modes = OrcaOutput.get_normal_modes(hess_file)

        bohr_to_angstrom = 0.529177249

        mode_idx = str(mode - 1)

        selected_mode = normal_modes.select(pl.col(mode_idx)).to_numpy().flatten()
        selected_mode *= bohr_to_angstrom
        mode_displacement = selected_mode * amplitude

        original_coords = np.array([a.coords for a in self.atoms])
        flattened_coords = original_coords.reshape(-1)

        displaced_flattened_coords = flattened_coords + mode_displacement
        displaced_coords = displaced_flattened_coords.reshape(len(self.atoms), 3)

        # Create new atoms with displaced coordinates
        displaced_atoms = [
            Atom(element=atom.element, coords=new_coord)
            for atom, new_coord in zip(self.atoms, displaced_coords)
        ]

        # Return a new Geometry object with the displaced atoms
        return Geometry(atoms=displaced_atoms, comment=self.comment)

    def create_normal_mode_frames(
        self,
        hess_file: Path | str,
        mode: int,
        amplitude: float = 1.0,
        n_frames: int = 9,
    ) -> list["Geometry"]:
        frames = []

        # Create evenly spaced amplitude values from -amplitude to +amplitude
        amplitude_values = np.linspace(-amplitude, amplitude, n_frames)

        # Generate a frame for each amplitude value
        for amp in amplitude_values:
            displaced_geometry = self.displace_along_normal_mode(hess_file, mode, amp)
            frames.append(displaced_geometry)

        return frames


@dataclass
class BondTypeSettings:
    """Dataclass for storing BondType settings"""

    range: float
    radius: float
    hex_color: str


class BondType(Enum):
    """BondType with respective technical settings"""

    SINGLE = BondTypeSettings(range=1.0, radius=1.0, hex_color="D3D3D3")
    COORDINATION = BondTypeSettings(range=1.3, radius=0.6, hex_color="C20CBE")


@dataclass
class Bond:
    """A Bond between two atoms"""

    atoms: tuple[Atom, Atom]
    type: BondType = BondType.SINGLE


class Molecule:
    """A Molecule composed of a Geometry, a charge, and a multiplicity"""

    def __init__(self, charge: int, mult: int, geometry: Geometry) -> None:
        self.charge = int(charge)
        self.mult = int(mult)
        self.geometry = geometry
        self.output_file: Optional[Path] = None

    def __repr__(self) -> str:
        json_metadata = (
            '{"charge": ' + str(self.charge) + ', "mult": ' + str(self.mult) + "}"
        )
        return f"{len(self.geometry.atoms)}\n{json_metadata}\n" + "\n".join(
            [str(a) for a in self.geometry.atoms]
        )

    def fig(self) -> Figure:
        from orca_studio.render import MolecularRenderer

        if not self._renderer:
            self._renderer = MolecularRenderer(self)
        return self._renderer.fig

    @classmethod
    def from_xyz_file(
        cls,
        xyz_file: Path | str,
        charge: Optional[int] = None,
        mult: Optional[int] = None,
    ) -> Self:
        """Construct a Molecule from an XYZ file.

        If the charge/mult are not specified by a JSON dict in the comment line of the XYZ file,
        they need to be supplied separately.

        Supplied charge/mult override JSON dict settings.
        """
        xyz = Path(xyz_file).read_text()
        return cls.from_xyz(xyz, charge, mult)

    @classmethod
    def from_xyz(
        cls, xyz: str, charge: Optional[int] = None, mult: Optional[int] = None
    ) -> Self:
        geometry = Geometry.from_xyz(xyz)

        if charge is None or mult is None:
            try:
                metadata = json.loads(geometry.comment.strip())
                charge = metadata.get("charge") if charge is None else charge
                mult = metadata.get("mult") if mult is None else mult
            except json.JSONDecodeError:
                if charge is None or mult is None:
                    raise ValueError(
                        "Charge and multiplicity must be provided if not in XYZ comment"
                    )

        if charge is None or mult is None:
            raise ValueError(
                "Failed to set either charge or mult from either the XYZ file or the method parameters - this should not have happend!"
            )

        return cls(charge, mult, geometry)

    def add_output_file(self, file: Path | str) -> Self:
        self.output_file = Path(file)
        return self

    @classmethod
    def from_output(cls, output_file: Path | str) -> Self:
        output = OrcaOutput(output_file)
        xyz = output.xyz
        charge = output.charge
        mult = output.mult
        return cls.from_xyz(xyz, charge, mult).add_output_file(output_file)

    def get_bonds_by_radius_overlap(self, radius_scale: float = 0.5) -> list[Bond]:
        """
        Detect bonds between atoms based on their atomic radii and distances.

        Uses atomic radii to determine if atoms are close enough to be bonded,
        with special handling for coordination bonds involving metals.

        Args:
            radius_scale: Factor to radius_scale the bond threshold distance (default: 0.5)

        Returns:
            List of detected Bond objects
        """
        bonds: list[Bond] = []
        for i, j in combinations(self.geometry.atoms, 2):
            bond_type = BondType.SINGLE
            bond_threshold = (
                i.element.atomic_radius_pm + j.element.atomic_radius_pm
            ) / 100
            bond_threshold *= radius_scale

            # Coordination bonds are usually longer (same for hydrogen bonds etc)
            if i.element.is_metal or j.element.is_metal:
                bond_type = BondType.COORDINATION
                bond_threshold *= BondType.COORDINATION.value.range

            distance = np.linalg.norm(j.coords - i.coords)

            if distance <= bond_threshold:
                bonds.append(Bond((i, j), bond_type))
        return bonds
