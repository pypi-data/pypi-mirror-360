from pathlib import Path

import click

from orca_studio.molecule import Geometry


@click.command(name="scan-mode")
@click.argument(
    "hess_file", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.argument("mode", type=int)
@click.option(
    "--amplitude",
    "-a",
    default=1.0,
    type=float,
    help="Amplitude of the normal mode displacement",
)
@click.option(
    "--n-frames", "-n", default=9, type=int, help="Number of frames to generate"
)
@click.option("--overwrite", "-o", is_flag=True)
@click.argument("output_dir", type=click.Path(path_type=Path), default=None)
def scan_mode_cmd(hess_file, mode, amplitude, n_frames, overwrite, output_dir):
    """
    Generate XYZ files for visualizing normal mode vibrations.

    HESS_FILE is the path to the Hessian (.hess) file.
    MODE is the normal mode number (1-based indexing).
    """
    hess_file = Path(hess_file)
    geometry = Geometry.from_hess_file(hess_file)
    frames = geometry.create_normal_mode_frames(hess_file, mode, amplitude, n_frames)

    base_name = f"{hess_file.stem}_mode_{mode:02d}"
    if not output_dir:
        output_dir = hess_file.parent / base_name
    output_dir.mkdir(exist_ok=True)

    for i, f in enumerate(frames):
        f.write_xyz_file(output_dir / f"{base_name}_{i:02d}.xyz", overwrite)
    click.echo(f"Generated {n_frames} frames in: {output_dir}")
