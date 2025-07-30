from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

# ------------------------------
# AILFT MATRIX ELEMENTS (CASSCF)
# --------------------------------

# Ligand field one-electron matrix VLFT (a.u.) :
# Orbital          dz2        dxz        dyz        dx2-y2     dxy
#   dz2         -4.024179   0.009140   0.004054  -0.003326   0.002750
#   dxz          0.009140  -4.109755   0.003117  -0.002725  -0.003117
#   dyz          0.004054   0.003117  -4.104976  -0.001850  -0.001043
#   dx2-y2      -0.003326  -0.002725  -0.001850  -4.088982   0.040136
#   dxy          0.002750  -0.003117  -0.001043   0.040136  -4.064806

# -------------------------------------------------
# Slater-Condon Parameters (electronic repulsion) :
# -------------------------------------------------
# F0dd(from 2el Ints)     =  0.843895520 a.u. =    22.964 eV =  185213.7 cm**-1 (fixed)
# F2dd                    =  0.385413315 a.u. =    10.488 eV =   84588.4 cm**-1
# F4dd                    =  0.245635722 a.u. =     6.684 eV =   53910.8 cm**-1
# -------------------
# Racah Parameters :
# -------------------
# A(F0dd from 2el Ints)   =  0.816602662 a.u. =    22.221 eV =  179223.6 cm**-1
# B                       =  0.005080592 a.u. =     0.138 eV =    1115.1 cm**-1
# C                       =  0.019494899 a.u. =     0.530 eV =    4278.6 cm**-1
# C/B                     =  3.837
# -------------------------------------------------------------------------------

# -----------------------------------------
# The ligand field one electron eigenfunctions:
# -----------------------------------------
# Orbital    Energy (eV)  Energy(cm-1)      dz2        dxz        dyz        dx2-y2     dxy
#     1          0.000        0.0        -0.045686   0.028078  -0.054159  -0.800131   0.594964
#     2          0.194     1565.6        -0.078163   0.929592  -0.354474   0.063899   0.003793
#     3          0.402     3244.2        -0.088930   0.347581   0.931512  -0.001392   0.059691
#     4          2.295    18511.4         0.034107  -0.051866  -0.027864   0.594105   0.801505
#     5          2.620    21128.9        -0.991328  -0.107555  -0.054077   0.052401  -0.005497
# Ligand field orbitals were stored in ailft.casscf.lft.gbw

# ------------------------------
# AILFT MATRIX ELEMENTS (NEVPT2)
# --------------------------------

# Ligand field one-electron matrix VLFT (a.u.) :
# Orbital          dz2        dxz        dyz        dx2-y2     dxy
#   dz2         -4.030886   0.010077   0.004395  -0.003782   0.003169
#   dxz          0.010077  -4.125038   0.003584  -0.003109  -0.003459
#   dyz          0.004395   0.003584  -4.119412  -0.002012  -0.001199
#   dx2-y2      -0.003782  -0.003109  -0.002012  -4.101588   0.044770
#   dxy          0.003169  -0.003459  -0.001199   0.044770  -4.074611

# -------------------------------------------------
# Slater-Condon Parameters (electronic repulsion) :
# -------------------------------------------------
# F2dd                    =  0.340370319 a.u. =     9.262 eV =   74702.7 cm**-1
# F4dd                    =  0.196052209 a.u. =     5.335 eV =   43028.5 cm**-1
# -------------------
# Racah Parameters :
# -------------------
# B                       =  0.004723519 a.u. =     0.129 eV =    1036.7 cm**-1
# C                       =  0.015559699 a.u. =     0.423 eV =    3415.0 cm**-1
# C/B                     =  3.294
# -------------------------------------------------------------------------------

# -----------------------------------------
# The ligand field one electron eigenfunctions:
# -----------------------------------------
# Orbital    Energy (eV)  Energy(cm-1)      dz2        dxz        dyz        dx2-y2     dxy
#     1          0.000        0.0        -0.047179   0.021792  -0.048895  -0.800543   0.595012
#     2          0.208     1677.2        -0.078904   0.929968  -0.354272   0.057915   0.008492
#     3          0.450     3632.7        -0.088632   0.346896   0.931895   0.000951   0.058125
#     4          2.560    20651.5         0.034837  -0.051996  -0.027932   0.593994   0.801545
#     5          2.879    23220.6        -0.991201  -0.107913  -0.053782   0.054285  -0.006023
# Ligand field orbitals were stored in ailft.nevpt2.lft.gbw

# -----SOC-CONSTANTS-----
# ---All Values in cm-1---
# ZETA_D = 440.31
# ------------------------


@dataclass
class LigandFieldData:
    racah_b: float
    racah_c: float
    orbital_energies: list[float]
    ligand_field_matrix: NDArray
    ligand_field_eigenfunctions: NDArray


def ailft(lines: list[str]):
    HEADER_CASSCF = "AILFT MATRIX ELEMENTS (CASSCF)"
    HEADER_NEVPT2 = "AILFT MATRIX ELEMENTS (NEVPT2)"
    AILFT_BLOCK_LINES = 35

    def parse_ailft_block(ailft_block, nevpt2: bool = False):
        ligand_field_matrix_block = ailft_block[5:10]
        if nevpt2:
            racah_params_block = ailft_block[19:22]
            ligand_field_eigenfunctions_block = ailft_block[28:33]
        else:
            racah_params_block = ailft_block[21:24]
            ligand_field_eigenfunctions_block = ailft_block[30:35]

        ligand_field_matrix = []
        for line in ligand_field_matrix_block:
            dz2, dxz, dyz, dx2y2, dxy = list(map(float, line.split()[1:]))
            ligand_field_matrix.append([dz2, dxz, dyz, dx2y2, dxy])
        ligand_field_matrix = np.array(ligand_field_matrix)

        racah = {
            "B": float(racah_params_block[0].split()[-2]),
            "C": float(racah_params_block[1].split()[-2]),
            "C/B": float(racah_params_block[2].split()[-1]),
        }

        ligand_field_eigenfunctions = []
        orbital_energies = []
        for line in ligand_field_eigenfunctions_block:
            _, energy_ev, energy_cm, dz2, dxz, dyz, dx2y2, dxy = list(
                map(float, line.split())
            )
            ligand_field_eigenfunctions.append([dz2, dxz, dyz, dx2y2, dxy])
            orbital_energies.append(energy_cm)
        ligand_field_eigenfunctions = np.array(ligand_field_eigenfunctions)

        return LigandFieldData(
            racah_b=racah["B"],
            racah_c=racah["C"],
            orbital_energies=orbital_energies,
            ligand_field_matrix=ligand_field_matrix,
            ligand_field_eigenfunctions=ligand_field_eigenfunctions,
        )

    data = {}
    for idx, line in enumerate(lines):
        if HEADER_CASSCF in line:
            casscf_block = lines[idx : idx + AILFT_BLOCK_LINES]
            data["CASSCF"] = parse_ailft_block(casscf_block)
        if HEADER_NEVPT2 in line:
            nevpt2_block = lines[idx : idx + AILFT_BLOCK_LINES]
            data["NEVPT2"] = parse_ailft_block(nevpt2_block, nevpt2=True)

    return data["CASSCF"]
