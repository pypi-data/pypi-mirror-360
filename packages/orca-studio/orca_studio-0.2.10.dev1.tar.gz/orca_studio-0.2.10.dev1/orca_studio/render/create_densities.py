import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Density:
    gbw_file: Path
    grid: int = 100

    def compile_input(self) -> str:
        """Return a newline-separated sequence of inputs for `orca_plot`.

        Finish with exiting `orca_plot` and a final newline.

        ```
        4\\n$grid\\n5\\n7\\n3\\n$spin\\n2\\n$id\\n11\\n12\\n
        ```
        """
        ...

    def generate(self, input: str) -> subprocess.CompletedProcess:
        process = subprocess.run(
            ["orca_plot", self.gbw_file, "-i"],
            text=True,
            cwd=self.gbw_file.parent,
            input=input,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return process

    @staticmethod
    def check_grid(cube_file: Path) -> int:
        """Return the grid size of an exisiting cube file"""
        with open(cube_file) as f:
            for i, line in enumerate(f):
                if i == 2:
                    return int(line.split()[0])
            else:
                raise ValueError("Not enough lines in file")


@dataclass
class MolecularOrbital(Density):
    spin_up: bool = True
