from pathlib import Path

import polars as pl

from orca_studio.parse.ailft import LigandFieldData, ailft
from orca_studio.parse.basis_functions import basis_functions
from orca_studio.parse.charge import charge
from orca_studio.parse.ir.hessian import hessian
from orca_studio.parse.ir.ir_spectrum import ir_spectrum
from orca_studio.parse.ir.normal_modes import normal_modes
from orca_studio.parse.ir.vibrational_frequencies import vibrational_frequencies
from orca_studio.parse.mult import mult
from orca_studio.parse.run_time import run_time_h
from orca_studio.parse.tddft.absorption_spectra import (
    absorption_spectrum,
    soc_absorption_spectrum,
)
from orca_studio.parse.tddft.tda import tda
from orca_studio.parse.thermodynamics.enthalpy import enthalpy_eh
from orca_studio.parse.thermodynamics.entropy_correction import entropy_correction_eh
from orca_studio.parse.thermodynamics.fspe import fspe_eh
from orca_studio.parse.thermodynamics.gibbs_correction import gibbs_correction_eh
from orca_studio.parse.thermodynamics.gibbs_free_energy import gibbs_free_energy_eh
from orca_studio.parse.thermodynamics.thermal_correction import thermal_correction_eh
from orca_studio.parse.thermodynamics.zero_point_energy import zero_point_energy_eh
from orca_studio.parse.xyz import xyz


class OrcaOutput:
    def __init__(self, output_file: Path | str) -> None:
        self.output_file = Path(output_file)

        if not self.output_file.is_file():
            raise FileNotFoundError(
                f"ORCA output file '{self.output_file.resolve()}' not found"
            )

        self._lines = None

    @property
    def lines(self) -> list[str]:
        """Cache lines in memory"""
        if not self._lines:
            self._lines = self.output_file.read_text().splitlines()
        return self._lines

    @property
    def xyz(self) -> str:
        """Last cartesian coordinates as an XYZ string."""
        return xyz(self.lines)

    @property
    def charge(self) -> int:
        """Total charge"""
        return charge(self.lines)

    @property
    def mult(self) -> int:
        """Multiplicity"""
        return mult(self.lines)

    @property
    def tda(self) -> bool:
        """Tamm-Dancoff approximation"""
        return tda(self.lines)

    @property
    def run_time_h(self) -> float:
        """Total run time in hours"""
        return run_time_h(self.lines)

    @property
    def enthalpy_eh(self) -> float:
        """Total Enthalpy in Hartree"""
        return enthalpy_eh(self.lines)

    @property
    def entropy_correction_eh(self) -> float:
        """Entropy correction in Hartree"""
        return entropy_correction_eh(self.lines)

    @property
    def fspe_eh(self) -> float:
        """Final single point energy in Hartree"""
        return fspe_eh(self.lines)

    @property
    def gibbs_correction_eh(self) -> float:
        """Gibbs free energy minus the electronic energy in Hartree"""
        return gibbs_correction_eh(self.lines)

    @property
    def gibbs_free_energy_eh(self) -> float:
        """Gibbs free energy in Hartree"""
        return gibbs_free_energy_eh(self.lines)

    @property
    def thermal_correction_eh(self) -> float:
        """Thermal correction in Hartree"""
        return thermal_correction_eh(self.lines)

    @property
    def zero_point_energy_eh(self) -> float:
        """Zero-point energy in Hartree"""
        return zero_point_energy_eh(self.lines)

    @staticmethod
    def get_hessian(hess_file: Path | str) -> pl.DataFrame:
        lines = Path(hess_file).read_text().splitlines()
        return hessian(lines)

    @property
    def hessian(self) -> pl.DataFrame:
        """Hessian from the associated .hess file"""
        hess_file = self.output_file.with_suffix(".hess")
        if not hess_file.is_file():
            raise FileNotFoundError(f"Hessian file '{hess_file.resolve()}' not found")
        return self.get_hessian(hess_file)

    @staticmethod
    def get_normal_modes(hess_file: Path | str) -> pl.DataFrame:
        lines = Path(hess_file).read_text().splitlines()
        return normal_modes(lines)

    @property
    def normal_modes(self) -> pl.DataFrame:
        """Normal modes from the associated .hess file"""
        hess_file = self.output_file.with_suffix(".hess")
        if not hess_file.is_file():
            raise FileNotFoundError(f"Hessian file '{hess_file.resolve()}' not found")
        return self.get_normal_modes(hess_file)

    @property
    def absorption_spectrum(self) -> pl.DataFrame:
        """First absorption spectrum via electric transition dipole moments"""
        return absorption_spectrum(self.lines)

    @property
    def soc_absorption_spectrum(self) -> pl.DataFrame:
        """First SOC absorption spectrum via electric transition dipole moments"""
        return soc_absorption_spectrum(self.lines)

    @property
    def ailft(self) -> LigandFieldData:
        """ab initio ligand field data from a CASSCF calculation"""
        return ailft(self.lines)

    @property
    def basis_functions(self) -> int:
        """Number of basis functions"""
        return basis_functions(self.lines)

    @property
    def ir_spectrum(self) -> pl.DataFrame:
        """IR spectrum"""
        return ir_spectrum(self.lines)

    @property
    def vibrational_frequencies(self) -> pl.DataFrame:
        """Vibrational frequencies"""
        return vibrational_frequencies(self.lines)

    @property
    def imaginary_modes(self) -> pl.DataFrame | None:
        """Imaginary modes - returns None if there aren't any"""
        return self.vibrational_frequencies.filter(pl.col("freq") < 0)

    @property
    def has_imaginary_modes(self) -> bool:
        """Whether the calculation has imaginary modes or not"""
        return True if self.imaginary_modes is not None else False
